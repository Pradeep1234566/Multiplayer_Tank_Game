import socket
import pickle
import random
import threading
from _thread import start_new_thread

# ─────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────
SERVER     = "127.0.0.1"
PORT       = 5555
MAX_HEALTH = 3
HIT_RADIUS = 40

# All valid spawn zones — rectangular areas guaranteed clear of obstacles.
# Format: (x_min, x_max, y_min, y_max)
# These are the safe corners/pockets in the arena layout.
SPAWN_ZONES = [
    # Player 0 side (left half)
    (120,  280,  120,  260),   # top-left corner
    (120,  280,  580,  780),   # bottom-left corner
    (120,  380,  320,  520),   # mid-left open
    # Player 1 side (right half)
    (1120, 1280, 120,  260),   # top-right corner
    (1120, 1280, 580,  780),   # bottom-right corner
    (1020, 1280, 320,  520),   # mid-right open
]

# Initial fixed spawns (used only for first connect handshake)
INITIAL_SPAWN = {
    0: {"x": 200, "y": 200},
    1: {"x": 1200, "y": 200},
}


def random_spawn(player_id: int) -> dict:
    """
    Pick a random spawn point from the zones belonging to this player's side.
    Player 0 uses zones 0-2 (left), player 1 uses zones 3-5 (right).
    """
    side_zones = SPAWN_ZONES[:3] if player_id == 0 else SPAWN_ZONES[3:]
    zone = random.choice(side_zones)
    x = random.randint(zone[0], zone[1])
    y = random.randint(zone[2], zone[3])
    return {"x": x, "y": y}


# ─────────────────────────────────────────
#  SERVER SOCKET
# ─────────────────────────────────────────
socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
socket_server.bind((SERVER, PORT))
socket_server.listen(2)
print(f"[Server] Listening on {SERVER}:{PORT}")


# ─────────────────────────────────────────
#  SHARED GAME STATE
# ─────────────────────────────────────────
players = [
    {
        "x": INITIAL_SPAWN[0]["x"], "y": INITIAL_SPAWN[0]["y"],
        "angle": 0, "health": MAX_HEALTH, "score": 0, "bullets": [],
        # spawn_x/y: where this player should be after next respawn
        # client reads this and teleports locally
        "spawn_x": INITIAL_SPAWN[0]["x"], "spawn_y": INITIAL_SPAWN[0]["y"],
        "just_spawned": False,
    },
    {
        "x": INITIAL_SPAWN[1]["x"], "y": INITIAL_SPAWN[1]["y"],
        "angle": 0, "health": MAX_HEALTH, "score": 0, "bullets": [],
        "spawn_x": INITIAL_SPAWN[1]["x"], "spawn_y": INITIAL_SPAWN[1]["y"],
        "just_spawned": False,
    },
]

# Bullet IDs that already dealt damage — never process twice
hit_bullets = set()

current_players = 0
lock = threading.Lock()


# ─────────────────────────────────────────
#  COLLISION
# ─────────────────────────────────────────
def dist_sq(ax, ay, bx, by):
    return (ax - bx) ** 2 + (ay - by) ** 2


def process_hits(shooter_id: int, victim_id: int):
    shooter = players[shooter_id]
    victim  = players[victim_id]
    to_remove = []

    for bullet in shooter["bullets"]:
        bx, by = bullet["x"], bullet["y"]
        bid    = bullet.get("bid")

        if bid in hit_bullets:
            continue

        if dist_sq(bx, by, victim["x"], victim["y"]) < HIT_RADIUS ** 2:
            to_remove.append(bullet)

            if bid:
                hit_bullets.add(bid)

            victim["health"] -= 1
            print(f"[Server] P{shooter_id} hit P{victim_id} | hp={victim['health']}")

            if victim["health"] <= 0:
                # Pick a new random spawn for the victim
                spawn = random_spawn(victim_id)
                victim["health"]      = MAX_HEALTH
                victim["x"]           = spawn["x"]
                victim["y"]           = spawn["y"]
                victim["spawn_x"]     = spawn["x"]
                victim["spawn_y"]     = spawn["y"]
                victim["just_spawned"] = True
                shooter["score"]      += 1
                print(f"[Server] P{shooter_id} kills P{victim_id} → respawn {spawn} | score={shooter['score']}")

            break

    for b in to_remove:
        try:
            shooter["bullets"].remove(b)
        except ValueError:
            pass


# ─────────────────────────────────────────
#  CLIENT THREAD
# ─────────────────────────────────────────
def threaded_client(conn, player_id):
    global current_players

    try:
        conn.send(pickle.dumps((player_id, players[player_id])))

        while True:
            raw = b""
            while True:
                chunk = conn.recv(8192)
                if not chunk:
                    raise ConnectionResetError("Client disconnected")
                raw += chunk
                try:
                    pickle.loads(raw)
                    break
                except Exception:
                    continue

            data = pickle.loads(raw)
            enemy_id = 1 - player_id

            with lock:
                players[player_id]["x"]       = data["x"]
                players[player_id]["y"]       = data["y"]
                players[player_id]["angle"]   = data["angle"]
                players[player_id]["bullets"] = data["bullets"]

                process_hits(player_id, enemy_id)

                me    = players[player_id]
                enemy = players[enemy_id]

                reply = {
                    # Enemy state
                    "x":            enemy["x"],
                    "y":            enemy["y"],
                    "angle":        enemy["angle"],
                    "health":       enemy["health"],
                    "score":        enemy["score"],
                    "bullets":      enemy["bullets"],
                    # My authoritative state
                    "my_health":    me["health"],
                    "my_score":     me["score"],
                    # Spawn position (used after a kill)
                    "my_spawn_x":   me["spawn_x"],
                    "my_spawn_y":   me["spawn_y"],
                    "just_spawned": me["just_spawned"],
                }

                # Reset the just_spawned flag after sending it once
                me["just_spawned"] = False

            conn.sendall(pickle.dumps(reply))

    except Exception as e:
        print(f"[Server] P{player_id} disconnected: {e}")
    finally:
        with lock:
            current_players -= 1
        conn.close()


# ─────────────────────────────────────────
#  CONNECTION LOOP
# ─────────────────────────────────────────
while True:
    conn, addr = socket_server.accept()
    print(f"[Server] Connection from {addr}")

    with lock:
        if current_players >= 2:
            print("[Server] Full — rejecting")
            conn.close()
            continue
        pid = current_players
        current_players += 1

    start_new_thread(threaded_client, (conn, pid))