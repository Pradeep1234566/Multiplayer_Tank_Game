import pygame
import sys
import math

from settings import *

from classes.tank import Tank
from classes.obstacle import Obstacle
from classes.bullet import Bullet

from UI.Ui import (
    draw_background,
    draw_score
)

from network import Network


# ---------------- INIT ----------------
pygame.init()

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "Tank Battle Multiplayer"
)

clock = pygame.time.Clock()

font = pygame.font.Font(
    None,
    50
)

score1 = 0
score2 = 0


# ---------------- NETWORK ----------------
network = Network()

player_id = (
    network.player_id
)

start_data = (
    network.player_data
)

print(
    f"Player ID: {player_id}"
)


# ---------------- CONTROLS ----------------
controls1 = {
    "up": pygame.K_w,
    "down": pygame.K_s,
    "left": pygame.K_a,
    "right": pygame.K_d,
    "rotate_left": pygame.K_q,
    "rotate_right": pygame.K_e
}

controls2 = {
    "up": pygame.K_i,
    "down": pygame.K_k,
    "left": pygame.K_j,
    "right": pygame.K_l,
    "rotate_left": pygame.K_u,
    "rotate_right": pygame.K_o
}


# ---------------- CREATE PLAYERS ----------------
if player_id == 0:

    player = Tank(
        start_data["x"],
        start_data["y"],
        controls1,
        GREEN_TANK
    )

    enemy = Tank(
        1150,
        450,
        controls2,
        RED_TANK
    )

else:

    player = Tank(
        start_data["x"],
        start_data["y"],
        controls2,
        RED_TANK
    )

    enemy = Tank(
        250,
        450,
        controls1,
        GREEN_TANK
    )


# ---------------- BULLETS ----------------
bullets = []
enemy_bullets = []


# ---------------- OBSTACLES ----------------
obstacles = [

    Obstacle(
        600,
        150,
        40,
        300
    ),

    Obstacle(
        800,
        500,
        300,
        40
    ),

    Obstacle(
        250,
        650,
        350,
        40
    ),

    Obstacle(
        1000,
        200,
        40,
        250
    )
]


# ---------------- GAME LOOP ----------------
while True:

    # EVENTS
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # ---------------- SHOOT ----------------
        if event.type == pygame.KEYDOWN:

            shoot_key = (
                pygame.K_SPACE
                if player_id == 0
                else pygame.K_p
            )

            if event.key == shoot_key:

                bullet_x = (
                    player.x
                    + math.cos(
                        math.radians(
                            player.angle
                        )
                    ) * 60
                )

                bullet_y = (
                    player.y
                    - math.sin(
                        math.radians(
                            player.angle
                        )
                    ) * 60
                )

                bullets.append(
                    Bullet(
                        bullet_x,
                        bullet_y,
                        player.angle,
                        player
                    )
                )

    # ---------------- UPDATE ----------------
    keys = pygame.key.get_pressed()

    player.move(
        keys,
        obstacles
    )

    # ---------------- MOVE BULLETS ----------------
    for bullet in bullets[:]:

        bullet.move()

        if (
            bullet.x < 0
            or bullet.x > WIDTH
            or bullet.y < 0
            or bullet.y > HEIGHT
        ):
            bullets.remove(
                bullet
            )

    # ---------------- SEND DATA ----------------
    data = {
        "x": player.x,
        "y": player.y,
        "angle": player.angle,

        "bullets": [
            {
                "x": bullet.x,
                "y": bullet.y,
                "angle": bullet.angle
            }

            for bullet in bullets
        ]
    }

    enemy_data = (
        network.send(data)
    )

    if enemy_data:

        enemy.x = (
            enemy_data["x"]
        )

        enemy.y = (
            enemy_data["y"]
        )

        enemy.angle = (
            enemy_data["angle"]
        )

        # ---------------- ENEMY BULLETS ----------------
        enemy_bullets = []

        for bullet_data in enemy_data[
            "bullets"
        ]:

            enemy_bullets.append(

                Bullet(
                    bullet_data["x"],
                    bullet_data["y"],
                    bullet_data["angle"],
                    enemy
                )
            )

    # ---------------- DRAW ----------------
    draw_background(
        screen
    )

    for obstacle in obstacles:
        obstacle.draw(screen)

    player.draw(screen)
    enemy.draw(screen)

    # Draw bullets
    for bullet in bullets:
        bullet.draw(screen)

    for bullet in enemy_bullets:
        bullet.draw(screen)

    draw_score(
        screen,
        font,
        score1,
        score2
    )

    pygame.display.flip()

    clock.tick(FPS)