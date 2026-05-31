import pygame
import sys
import math
import random

from settings import *
from classes.tank import Tank
from classes.obstacle import Obstacle
from classes.bullet import Bullet
from classes.UI.Ui import draw_score
from classes.UI.Ui import draw_background
from classes.UI.Ui import draw_arena
from classes.UI.Ui import draw_explosion
from classes.UI.Ui import draw_muzzle_flash
from classes.UI.Ui import draw_bullet_trail
from classes.UI.Ui import push_kill_notif
from network import Network

import pygame
import sys
import math
import random

# ══════════════════════════════════════════
#  INIT
# ══════════════════════════════════════════
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TANK BATTLE")
clock = pygame.time.Clock()
font  = pygame.font.Font(None, 50)


# ══════════════════════════════════════════
#  NETWORK
# ══════════════════════════════════════════
network    = Network()
player_id  = network.player_id
start_data = network.player_data
print(f"[Client] Player {player_id}")


# ══════════════════════════════════════════
#  CONTROLS
# ══════════════════════════════════════════
controls1 = {
    "up": pygame.K_w,  "down": pygame.K_s,
    "left": pygame.K_a, "right": pygame.K_d,
    "rotate_left": pygame.K_q, "rotate_right": pygame.K_e,
}
controls2 = {
    "up": pygame.K_i,  "down": pygame.K_k,
    "left": pygame.K_j, "right": pygame.K_l,
    "rotate_left": pygame.K_u, "rotate_right": pygame.K_o,
}
SHOOT_KEYS = {0: pygame.K_SPACE, 1: pygame.K_p}


# ══════════════════════════════════════════
#  PLAYERS
# ══════════════════════════════════════════
if player_id == 0:
    my_color    = GREEN_TANK
    enemy_color = RED_TANK
    player = Tank(start_data["x"], start_data["y"], controls1, my_color)
    enemy  = Tank(1200, 200, controls2, enemy_color)
else:
    my_color    = RED_TANK
    enemy_color = GREEN_TANK
    player = Tank(start_data["x"], start_data["y"], controls2, my_color)
    enemy  = Tank(200, 200, controls1, enemy_color)


# ══════════════════════════════════════════
#  GAME STATE
# ══════════════════════════════════════════
bullets       = []
enemy_bullets = []
my_score      = 0
enemy_score   = 0

# Previous server-health values — used to detect hits & kills
prev_my_health    = MAX_HEALTH
prev_enemy_health = MAX_HEALTH

# Visual effects
explosions   = []  # list of {"x","y","frame","max"}
muzzle_flash = []  # list of {"x","y","angle","frame"}
bullet_trails = {} # id(bullet) -> [(x,y), ...]

shoot_cooldown = 0
SHOOT_COOLDOWN = 350  # ms
bullet_id_counter = 0  # unique id stamped on each bullet when spawned


# ══════════════════════════════════════════
#  OBSTACLES
# ══════════════════════════════════════════
obstacles = [
    # Centre column
    Obstacle(665,  350,  70, 200),
    # Top-left block
    Obstacle(320,  180,  200, 45),
    # Top-right block
    Obstacle(880,  180,  200, 45),
    # Bottom-left block
    Obstacle(280,  620,  45, 200),
    # Bottom-right block
    Obstacle(1075, 620,  45, 200),
    # Mid-left wall
    Obstacle(450,  430,  45, 160),
    # Mid-right wall
    Obstacle(905,  430,  45, 160),
]


# ══════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════
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

def hits(bx, by, tx, ty, r=38):
    return (bx - tx) ** 2 + (by - ty) ** 2 < r * r

def spawn_explosion(x, y, big=False):
    explosions.append({"x": x, "y": y, "frame": 0, "max": 28 if big else 18})


# ══════════════════════════════════════════
#  GAME LOOP
# ══════════════════════════════════════════
while True:
    clock.tick(FPS)

    # ── EVENTS ──────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == SHOOT_KEYS[player_id]:
                now = pygame.time.get_ticks()
                if now - shoot_cooldown >= SHOOT_COOLDOWN:
                    bullets.append(spawn_bullet(player))
                    shoot_cooldown = now

    # ── PLAYER MOVEMENT ─────────────────────
    player.move(pygame.key.get_pressed(), obstacles)

    # ── MOVE MY BULLETS ─────────────────────
    for b in bullets[:]:
        b.move()

        tid = id(b)
        if tid not in bullet_trails:
            bullet_trails[tid] = []
        bullet_trails[tid].append((b.x, b.y))
        if len(bullet_trails[tid]) > 8:
            bullet_trails[tid].pop(0)

        # Off screen
        if b.x < 0 or b.x > WIDTH or b.y < 0 or b.y > HEIGHT:
            bullet_trails.pop(tid, None)
            bullets.remove(b)
            continue

        # Hit wall
        if any(obs.rect.collidepoint(b.x, b.y) for obs in obstacles):
            spawn_explosion(b.x, b.y, big=False)
            bullet_trails.pop(tid, None)
            bullets.remove(b)
            continue

        # Do NOT remove bullet on visual contact with enemy.
        # Server handles damage and bullet removal — if we delete it
        # client-side first, the server never sees it at the hit position.

    # ── SEND & RECEIVE ──────────────────────
    data = {
        "x":     player.x,
        "y":     player.y,
        "angle": player.angle,
        "bullets": [{"x": b.x, "y": b.y, "angle": b.angle, "bid": b.bid} for b in bullets],
    }
    resp = network.send(data)

    if resp:
        new_my_health    = resp["my_health"]
        new_enemy_health = resp["health"]

        # ── We took a hit ──────────────────────
        if new_my_health < prev_my_health:
            player.take_hit()

        # ── Enemy took a hit (our bullet landed) ──
        if new_enemy_health < prev_enemy_health:
            spawn_explosion(enemy.x, enemy.y, big=False)

        # ── We were killed — server tells us where to respawn ──
        if resp.get("just_spawned"):
            spawn_explosion(player.x, player.y, big=True)
            player.x     = resp["my_spawn_x"]
            player.y     = resp["my_spawn_y"]
            player.angle = 0
            push_kill_notif("ENEMY", "YOU")

        # ── We got a kill (enemy health reset to MAX) ─────────
        if prev_enemy_health < MAX_HEALTH and new_enemy_health == MAX_HEALTH:
            spawn_explosion(enemy.x, enemy.y, big=True)
            push_kill_notif("YOU", "ENEMY")

        prev_my_health    = new_my_health
        prev_enemy_health = new_enemy_health

        # Sync everything from server (server is authoritative)
        player.health = new_my_health
        my_score      = resp["my_score"]
        enemy.x       = resp["x"]
        enemy.y       = resp["y"]
        enemy.angle   = resp["angle"]
        enemy.health  = new_enemy_health
        enemy_score   = resp["score"]

        # Rebuild enemy bullets
        enemy_bullets = [
            Bullet(bd["x"], bd["y"], bd["angle"], enemy)
            for bd in resp["bullets"]
        ]

    # ══════════════════════════════════════
    #  DRAW
    # ══════════════════════════════════════
    draw_background(screen)
    draw_arena(screen)

    for obs in obstacles:
        obs.draw(screen)

    # My bullet trails
    for b in bullets:
        trail = bullet_trails.get(id(b), [])
        draw_bullet_trail(screen, trail, my_color)

    # Enemy bullets — draw directly (no trail since they're rebuilt each frame)
    for b in enemy_bullets:
        b.draw(screen)

    # Muzzle flashes
    for mf in muzzle_flash[:]:
        draw_muzzle_flash(screen, mf["x"], mf["y"], mf["angle"], mf["frame"])
        mf["frame"] += 1
        if mf["frame"] > 5:
            muzzle_flash.remove(mf)

    player.draw(screen)
    enemy.draw(screen)

    for b in bullets:
        b.draw(screen)

    # Explosions
    for ex in explosions[:]:
        draw_explosion(screen, ex["x"], ex["y"], ex["frame"], ex["max"])
        ex["frame"] += 1
        if ex["frame"] >= ex["max"]:
            explosions.remove(ex)

    draw_score(screen, font, my_score, enemy_score, player_id)

    pygame.display.flip()