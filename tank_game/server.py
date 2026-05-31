import socket
import pickle
import random
import threading
import time
from _thread import start_new_thread

# ─────────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────────
SERVER          = "0.0.0.0"
PORT            = 5555
MAX_HEALTH      = 3
HIT_RADIUS      = 40
WIN_SCORE       = 10
SPAWN_SHIELD_S  = 2.5    # seconds of invincibility after respawn
POWERUP_INTERVAL = 15.0  # seconds between new powerup spawns

# Safe spawn zones per side — (x_min, x_max, y_min, y_max)
SPAWN_ZONES = [
    (120, 280, 120, 260),    # P0 top-left
    (120, 280, 580, 780),    # P0 bottom-left
    (120, 380, 320, 520),    # P0 mid-left
    (1120, 1280, 120, 260),  # P1 top-right
    (1120, 1280, 580, 780),  # P1 bottom-right
    (1020, 1280, 320, 520),  # P1 mid-right
]

INITIAL_SPAWN = {
    0: {"x": 200, "y": 200},
    1: {"x": 1200, "y": 200},
}

# Powerup spawn zones — centre of map, away from spawns
POWERUP_ZONES = [
    (500, 900, 200, 700),
]


def random_spawn(pid):
    zones = SPAWN_ZONES[:3] if pid == 0 else SPAWN_ZONES[3:]
    z = random.choice(zones)
    return {"x": random.randint(z[0], z[1]), "y": random.randint(z[2], z[3])}


def random_powerup():
    z = random.choice(POWERUP_ZONES)
    kind = random.choice(["speed", "shield", "rapid"])
    return {
        "x":    random.randint(z[0], z[1]),
        "y":    random.randint(z[2], z[3]),
        "kind": kind,
        "id":   random.randint(100000, 999999),
    }


# ─────────────────────────────────────────────────
#  SERVER SOCKET
# ─────────────────────────────────────────────────
socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
socket_server.bind((SERVER, PORT))
socket_server.listen(2)
print(f"[Server] Listening on {SERVER}:{PORT}")


# ─────────────────────────────────────────────────
#  SHARED GAME STATE
# ─────────────────────────────────────────────────
players = [
    {
        "x": INITIAL_SPAWN[0]["x"], "y": INITIAL_SPAWN[0]["y"],
        "angle": 0, "health": MAX_HEALTH, "score": 0, "bullets": [],
        "spawn_x": INITIAL_SPAWN[0]["x"], "spawn_y": INITIAL_SPAWN[0]["y"],
        "just_spawned": False,
        "shield_until": 0.0,   # epoch time until shield active
        "active_powerup": None, # "speed" | "shield" | "rapid" | None
        "powerup_until": 0.0,
        "connected": False,
    },
    {
        "x": INITIAL_SPAWN[1]["x"], "y": INITIAL_SPAWN[1]["y"],
        "angle": 0, "health": MAX_HEALTH, "score": 0, "bullets": [],
        "spawn_x": INITIAL_SPAWN[1]["x"], "spawn_y": INITIAL_SPAWN[1]["y"],
        "just_spawned": False,
        "shield_until": 0.0,
        "active_powerup": None,
        "powerup_until": 0.0,
        "connected": False,
    },
]

# Game state: "waiting" | "playing" | "game_over"
game_state      = "waiting"
winner_id       = None
game_start_time = None

# Powerups on the field: list of {"x","y","kind","id"}
powerups        = []
last_powerup_t  = 0.0

hit_bullets     = set()
current_players = 0
lock            = threading.Lock()


# ─────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────
def dist_sq(ax, ay, bx, by):
    return (ax - bx) ** 2 + (ay - by) ** 2


def reset_game():
    global game_state, winner_id, game_start_time, hit_bullets, powerups, last_powerup_t
    for pid in range(2):
        sp = random_spawn(pid)
        players[pid].update({
            "x": sp["x"], "y": sp["y"],
            "angle": 0, "health": MAX_HEALTH, "score": 0, "bullets": [],
            "spawn_x": sp["x"], "spawn_y": sp["y"],
            "just_spawned": False,
            "shield_until": time.time() + SPAWN_SHIELD_S,
            "active_powerup": None,
            "powerup_until": 0.0,
        })
    game_state      = "playing"
    winner_id       = None
    game_start_time = time.time()
    hit_bullets     = set()
    powerups        = []
    last_powerup_t  = time.time()
    print("[Server] Game started!")


def process_hits(shooter_id, victim_id):
    global game_state, winner_id
    shooter = players[shooter_id]
    victim  = players[victim_id]

    # Victim shielded by spawn protection?
    if time.time() < victim["shield_until"]:
        return

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

            # Shield powerup absorbs one hit then is consumed
            if victim["active_powerup"] == "shield":
                victim["active_powerup"]  = None
                victim["powerup_until"]   = 0.0
                victim["shield_blocked"]  = True   # tell client to flash blue
                print(f"[Server] P{victim_id} shield absorbed a hit")
            else:
                victim["health"] -= 1
                print(f"[Server] P{shooter_id} hit P{victim_id} | hp={victim['health']}")
                if victim["health"] <= 0:
                    spawn = random_spawn(victim_id)
                    victim.update({
                        "health":         MAX_HEALTH,
                        "x":              spawn["x"],
                        "y":              spawn["y"],
                        "spawn_x":        spawn["x"],
                        "spawn_y":        spawn["y"],
                        "just_spawned":   True,
                        "shield_until":   time.time() + SPAWN_SHIELD_S,
                        "active_powerup": None,
                        "powerup_until":  0.0,
                    })
                    shooter["score"] += 1
                    print(f"[Server] P{shooter_id} kills P{victim_id} | score={shooter['score']}")
                    if shooter["score"] >= WIN_SCORE:
                        game_state = "game_over"
                        winner_id  = shooter_id
                        print(f"[Server] P{shooter_id} WINS!")
            break
    for b in to_remove:
        try:
            shooter["bullets"].remove(b)
        except ValueError:
            pass


def process_powerups(pid):
    """Check if player pid walks over a powerup."""
    global powerups
    p = players[pid]
    remaining = []
    for pu in powerups:
        if dist_sq(p["x"], p["y"], pu["x"], pu["y"]) < 50 ** 2:
            # Apply powerup
            p["active_powerup"] = pu["kind"]
            p["powerup_until"]  = time.time() + 8.0   # 8 seconds duration
            print(f"[Server] P{pid} picked up {pu['kind']}")
        else:
            remaining.append(pu)
    powerups = remaining


def cleanup_hit_bullets():
    """Remove bids that are no longer in anyone's bullet list."""
    active_bids = set()
    for p in players:
        for b in p["bullets"]:
            bid = b.get("bid")
            if bid:
                active_bids.add(bid)
    hit_bullets.intersection_update(active_bids | hit_bullets)
    # Actually just cap the set size to prevent unbounded growth
    if len(hit_bullets) > 2000:
        hit_bullets.clear()


# ─────────────────────────────────────────────────
#  CLIENT THREAD
# ─────────────────────────────────────────────────
def threaded_client(conn, player_id):
    global current_players, game_state, last_powerup_t

    try:
        with lock:
            players[player_id]["connected"] = True
            # Start game when both connect
            both_connected = all(p["connected"] for p in players)
            if both_connected and game_state == "waiting":
                reset_game()

        conn.send(pickle.dumps((player_id, players[player_id])))

        while True:
            # ── Recv ──────────────────────────
            raw = b""
            while True:
                chunk = conn.recv(8192)
                if not chunk:
                    raise ConnectionResetError("disconnected")
                raw += chunk
                try:
                    pickle.loads(raw)
                    break
                except Exception:
                    continue

            data = pickle.loads(raw)
            enemy_id = 1 - player_id
            now = time.time()

            with lock:
                if game_state == "playing":
                    # Update player state from client
                    players[player_id]["x"]       = data["x"]
                    players[player_id]["y"]       = data["y"]
                    players[player_id]["angle"]   = data["angle"]
                    players[player_id]["bullets"] = data["bullets"]

                    # Expire powerups
                    for pid in range(2):
                        if players[pid]["active_powerup"] and now > players[pid]["powerup_until"]:
                            players[pid]["active_powerup"] = None

                    # Spawn new powerup?
                    if now - last_powerup_t > POWERUP_INTERVAL and len(powerups) < 3:
                        powerups.append(random_powerup())
                        last_powerup_t = now

                    process_powerups(player_id)
                    process_hits(player_id, enemy_id)
                    cleanup_hit_bullets()

                elif game_state == "game_over":
                    # Client sent a "restart" request
                    if data.get("restart"):
                        reset_game()

                me    = players[player_id]
                enemy = players[enemy_id]

                # Build powerup speed/rapid modifiers
                my_speed_mult   = 1.8 if me["active_powerup"] == "speed"  else 1.0
                my_rapid        = me["active_powerup"] == "rapid"
                my_shield_on    = now < me["shield_until"]
                enemy_shield_on = now < enemy["shield_until"]

                # Shield-blocked flag: did a bullet just get absorbed?
                # We detect it: active_powerup was "shield" but is now None
                # Actually we track it explicitly — add a flag to player state
                shield_blocked = me.get("shield_blocked", False)
                me["shield_blocked"] = False   # reset after reading once

                reply = {
                    "game_state":    game_state,
                    "winner_id":     winner_id,
                    # Enemy
                    "x":             enemy["x"],
                    "y":             enemy["y"],
                    "angle":         enemy["angle"],
                    "health":        enemy["health"],
                    "score":         enemy["score"],
                    "bullets":       enemy["bullets"],
                    "enemy_shielded": enemy_shield_on,
                    "enemy_powerup": enemy["active_powerup"],
                    # Me
                    "my_health":     me["health"],
                    "my_score":      me["score"],
                    "my_spawn_x":    me["spawn_x"],
                    "my_spawn_y":    me["spawn_y"],
                    "just_spawned":  me["just_spawned"],
                    "shielded":      my_shield_on,
                    "shield_left":   max(0.0, me["shield_until"] - now),
                    "my_powerup":    me["active_powerup"],
                    "speed_mult":    my_speed_mult,
                    "rapid_fire":    my_rapid,
                    # Powerups on field
                    "powerups":      list(powerups),
                }

                me["just_spawned"] = False

            conn.sendall(pickle.dumps(reply))

    except Exception as e:
        print(f"[Server] P{player_id} disconnected: {e}")
    finally:
        with lock:
            players[player_id]["connected"] = False
            current_players -= 1
            if game_state == "playing":
                game_state = "waiting"
                print("[Server] Player left — back to waiting")
        conn.close()


# ─────────────────────────────────────────────────
#  CONNECTION LOOP
# ─────────────────────────────────────────────────
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