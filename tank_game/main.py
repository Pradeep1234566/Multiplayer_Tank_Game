import pygame
import sys
import math
import random

from settings import *
from classes.tank import Tank
from classes.obstacle import Obstacle
from classes.bullet import Bullet
from classes.UI.Ui import draw_powerup, draw_score, draw_shield_ring, draw_waiting_screen, draw_win_screen
from classes.UI.Ui import draw_background
from classes.UI.Ui import draw_arena
from classes.UI.Ui import draw_explosion
from classes.UI.Ui import draw_muzzle_flash
from classes.UI.Ui import draw_bullet_trail
from classes.UI.Ui import push_kill_notif
from network import Network



# ══════════════════════════════════════════════
#  INIT
# ══════════════════════════════════════════════
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TANK BATTLE")
clock = pygame.time.Clock()
font  = pygame.font.Font(None, 50)


# ══════════════════════════════════════════════
#  NETWORK
# ══════════════════════════════════════════════
network    = Network()
player_id  = network.player_id
start_data = network.player_data
print(f"[Client] Player {player_id}")


# ══════════════════════════════════════════════
#  CONTROLS — online: everyone uses WASD+SPACE
# ══════════════════════════════════════════════
my_controls = {
    "up":           pygame.K_w,
    "down":         pygame.K_s,
    "left":         pygame.K_a,
    "right":        pygame.K_d,
    "rotate_left":  pygame.K_q,
    "rotate_right": pygame.K_e,
}
SHOOT_KEY = pygame.K_SPACE


# ══════════════════════════════════════════════
#  PLAYERS
# ══════════════════════════════════════════════
if player_id == 0:
    my_color    = GREEN_TANK
    enemy_color = RED_TANK
else:
    my_color    = RED_TANK
    enemy_color = GREEN_TANK

player = Tank(start_data["x"], start_data["y"], my_controls, my_color)
enemy  = Tank(start_data["x"], start_data["y"], my_controls, enemy_color)  # pos synced from server


# ══════════════════════════════════════════════
#  GAME STATE
# ══════════════════════════════════════════════
bullets       = []
enemy_bullets = []
my_score      = 0
enemy_score   = 0

prev_my_health    = MAX_HEALTH
prev_enemy_health = MAX_HEALTH

game_state    = "waiting"   # "waiting" | "playing" | "game_over"
winner_id     = None

# Visual effects
explosions    = []
muzzle_flash  = []
bullet_trails = {}

# Screen shake
shake_frames  = 0
shake_mag     = 0

# Spawn shield
shielded      = False
shield_left   = 0.0

# Powerups on field
field_powerups = []
my_powerup     = None
rapid_fire     = False
speed_mult     = 1.0

shoot_cooldown    = 0
bullet_id_counter = 0


# ══════════════════════════════════════════════
#  OBSTACLES
# ══════════════════════════════════════════════
obstacles = [
    Obstacle(665,  350,  70, 200),
    Obstacle(320,  180, 200,  45),
    Obstacle(880,  180, 200,  45),
    Obstacle(280,  620,  45, 200),
    Obstacle(1075, 620,  45, 200),
    Obstacle(450,  430,  45, 160),
    Obstacle(905,  430,  45, 160),
]


# ══════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════
def get_shoot_cooldown():
    return 150 if rapid_fire else 350

def spawn_bullet(tank):
    global bullet_id_counter
    rad = math.radians(tank.angle)
    bx  = tank.x + math.cos(rad) * 62
    by  = tank.y - math.sin(rad) * 62
    b   = Bullet(bx, by, tank.angle, tank)
    b.bid = f"{player_id}_{bullet_id_counter}"
    bullet_id_counter += 1
    muzzle_flash.append({"x": bx, "y": by, "angle": tank.angle, "frame": 0})
    return b

def do_shake(mag=8, frames=10):
    global shake_frames, shake_mag
    shake_frames = frames
    shake_mag    = mag

def spawn_explosion(x, y, big=False):
    explosions.append({"x": x, "y": y, "frame": 0, "max": 28 if big else 18})

def get_shake_offset():
    if shake_frames <= 0:
        return (0, 0)
    return (random.randint(-shake_mag, shake_mag),
            random.randint(-shake_mag, shake_mag))


# ══════════════════════════════════════════════
#  GAME LOOP
# ══════════════════════════════════════════════
while True:
    clock.tick(FPS)
    ox, oy = get_shake_offset()
    if shake_frames > 0:
        shake_frames -= 1

    # ── EVENTS ────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            # Shoot
            if event.key == SHOOT_KEY and game_state == "playing":
                now = pygame.time.get_ticks()
                if now - shoot_cooldown >= get_shoot_cooldown():
                    if len(bullets) < MAX_BULLETS:
                        bullets.append(spawn_bullet(player))
                        shoot_cooldown = now

            # Restart after game over
            if event.key == pygame.K_r and game_state == "game_over":
                # Send restart signal next frame (handled in network data)
                pass

    # ── MOVEMENT (only while playing) ─────────
    if game_state == "playing":
        player.speed = TANK_SPEED * speed_mult
        player.move(pygame.key.get_pressed(), obstacles)

    # ── MOVE MY BULLETS ───────────────────────
    for b in bullets[:]:
        b.move()
        tid = id(b)
        if tid not in bullet_trails:
            bullet_trails[tid] = []
        bullet_trails[tid].append((b.x, b.y))
        if len(bullet_trails[tid]) > 10:
            bullet_trails[tid].pop(0)

        if b.x < 0 or b.x > WIDTH or b.y < 0 or b.y > HEIGHT:
            bullet_trails.pop(tid, None)
            bullets.remove(b)
            continue

        if any(obs.rect.collidepoint(b.x, b.y) for obs in obstacles):
            spawn_explosion(b.x, b.y)
            bullet_trails.pop(tid, None)
            bullets.remove(b)
            continue

    # ── SEND / RECEIVE ────────────────────────
    data = {
        "x":      player.x,
        "y":      player.y,
        "angle":  player.angle,
        "bullets": [{"x": b.x, "y": b.y, "angle": b.angle, "bid": b.bid} for b in bullets],
        "restart": pygame.key.get_pressed()[pygame.K_r] and game_state == "game_over",
    }
    resp = network.send(data)

    if resp:
        game_state = resp.get("game_state", game_state)
        winner_id  = resp.get("winner_id")

        new_my_health    = resp["my_health"]
        new_enemy_health = resp["health"]
        shielded         = resp.get("shielded", False)
        shield_left      = resp.get("shield_left", 0.0)
        my_powerup       = resp.get("my_powerup")
        rapid_fire       = resp.get("rapid_fire", False)
        speed_mult       = resp.get("speed_mult", 1.0)
        field_powerups   = resp.get("powerups", [])

        if game_state == "playing":
            # Hit detection feedback
            if new_my_health < prev_my_health:
                player.take_hit()
                do_shake(mag=7, frames=8)

            if new_enemy_health < prev_enemy_health:
                spawn_explosion(enemy.x, enemy.y)

            # Respawn
            if resp.get("just_spawned"):
                spawn_explosion(player.x, player.y, big=True)
                player.x     = resp["my_spawn_x"]
                player.y     = resp["my_spawn_y"]
                player.angle = 0
                bullets.clear()
                bullet_trails.clear()
                push_kill_notif("ENEMY", "YOU")

            # Kill confirmed
            if prev_enemy_health < MAX_HEALTH and new_enemy_health == MAX_HEALTH:
                spawn_explosion(enemy.x, enemy.y, big=True)
                push_kill_notif("YOU", "ENEMY")

        prev_my_health    = new_my_health
        prev_enemy_health = new_enemy_health

        # Sync from server
        player.health  = new_my_health
        my_score       = resp["my_score"]
        enemy.x        = resp["x"]
        enemy.y        = resp["y"]
        enemy.angle    = resp["angle"]
        enemy.health   = new_enemy_health
        enemy_score    = resp["score"]

        enemy_bullets = [
            Bullet(bd["x"], bd["y"], bd["angle"], enemy)
            for bd in resp["bullets"]
        ]

    # ══════════════════════════════════════
    #  DRAW — apply shake offset to world
    # ══════════════════════════════════════
    draw_background(screen)

    # Blit everything to an offset surface for shake
    world = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    draw_arena(world)

    for obs in obstacles:
        obs.draw(world)

    # Powerups
    for pu in field_powerups:
        draw_powerup(world, pu["x"], pu["y"], pu["kind"])

    # Bullet trails
    for b in bullets:
        trail = bullet_trails.get(id(b), [])
        draw_bullet_trail(world, trail, my_color)

    # Muzzle flashes
    for mf in muzzle_flash[:]:
        draw_muzzle_flash(world, mf["x"], mf["y"], mf["angle"], mf["frame"])
        mf["frame"] += 1
        if mf["frame"] > 5:
            muzzle_flash.remove(mf)

    player.draw(world)
    enemy.draw(world)

    # Shield rings
    if shielded:
        draw_shield_ring(world, player.x, player.y, shield_left, SPAWN_SHIELD_MS / 1000)
    if resp and resp.get("enemy_shielded"):
        draw_shield_ring(world, enemy.x, enemy.y, 0, 0)

    for b in bullets:
        b.draw(world)
    for b in enemy_bullets:
        b.draw(world)

    # Explosions
    for ex in explosions[:]:
        draw_explosion(world, ex["x"], ex["y"], ex["frame"], ex["max"])
        ex["frame"] += 1
        if ex["frame"] >= ex["max"]:
            explosions.remove(ex)

    # Blit world with shake offset
    screen.blit(world, (ox, oy))

    # HUD drawn on top (no shake)
    if game_state == "playing":
        draw_score(screen, font, my_score, enemy_score, player_id,
                   my_powerup=my_powerup, win_score=WIN_SCORE)

    elif game_state == "waiting":
        draw_waiting_screen(screen, player_id)

    elif game_state == "game_over":
        draw_score(screen, font, my_score, enemy_score, player_id,
                   my_powerup=my_powerup, win_score=WIN_SCORE)
        draw_win_screen(screen, winner_id, player_id)

    pygame.display.flip()