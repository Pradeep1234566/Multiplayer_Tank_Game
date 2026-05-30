import pygame
import sys
import math

from settings import *

from classes.tank import Tank
from classes.bullet import Bullet
from classes.obstacle import Obstacle

from UI.Ui import (
    draw_background,
    draw_score
)


pygame.init()

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "Tank Battle"
)

clock = pygame.time.Clock()

font = pygame.font.Font(
    None,
    50
)

score1 = 0
score2 = 0


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
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "rotate_left": pygame.K_KP4,
    "rotate_right": pygame.K_KP6
}


# ---------------- PLAYERS ----------------
player1 = Tank(
    250,
    450,
    controls1,
    GREEN_TANK
)

player2 = Tank(
    1150,
    450,
    controls2,
    RED_TANK
)

bullets = []


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

        if event.type == pygame.KEYDOWN:

            # Player 1 shoot
            if event.key == pygame.K_SPACE:

                bullet_x = (
                    player1.x
                    + math.cos(
                        math.radians(
                            player1.angle
                        )
                    ) * 80
                )

                bullet_y = (
                    player1.y
                    - math.sin(
                        math.radians(
                            player1.angle
                        )
                    ) * 80
                )

                bullets.append(
                    Bullet(
                        bullet_x,
                        bullet_y,
                        player1.angle,
                        player1
                    )
                )

            # Player 2 shoot
            if event.key == pygame.K_RETURN:

                bullet_x = (
                    player2.x
                    + math.cos(
                        math.radians(
                            player2.angle
                        )
                    ) * 80
                )

                bullet_y = (
                    player2.y
                    - math.sin(
                        math.radians(
                            player2.angle
                        )
                    ) * 80
                )

                bullets.append(
                    Bullet(
                        bullet_x,
                        bullet_y,
                        player2.angle,
                        player2
                    )
                )

    # UPDATE
    keys = pygame.key.get_pressed()

    player1.move(
        keys,
        obstacles
    )

    player2.move(
        keys,
        obstacles
    )

    # BULLET LOGIC
    for bullet in bullets[:]:

        bullet.move()

        bullet_rect = pygame.Rect(
            bullet.x - 5,
            bullet.y - 5,
            10,
            10
        )

        # Bounce
        for obstacle in obstacles:

            if bullet_rect.colliderect(
                obstacle.rect
            ):

                overlap_left = abs(
                    bullet_rect.right
                    - obstacle.rect.left
                )

                overlap_right = abs(
                    bullet_rect.left
                    - obstacle.rect.right
                )

                overlap_top = abs(
                    bullet_rect.bottom
                    - obstacle.rect.top
                )

                overlap_bottom = abs(
                    bullet_rect.top
                    - obstacle.rect.bottom
                )

                min_overlap = min(
                    overlap_left,
                    overlap_right,
                    overlap_top,
                    overlap_bottom
                )

                if (
                    min_overlap
                    == overlap_left
                    or min_overlap
                    == overlap_right
                ):
                    bullet.angle = (
                        180
                        - bullet.angle
                    )
                else:
                    bullet.angle = (
                        -bullet.angle
                    )

                bullet.bounces -= 1
                break

        if bullet.bounces < 0:
            bullets.remove(bullet)
            continue

        # Hit player 2
        if (
            bullet.owner == player1
            and player2.get_rect()
            .collidepoint(
                bullet.x,
                bullet.y
            )
        ):

            score1 += 1
            bullets.remove(bullet)

            player2.x = 1150
            player2.y = 450
            player2.angle = 0

        # Hit player 1
        elif (
            bullet.owner == player2
            and player1.get_rect()
            .collidepoint(
                bullet.x,
                bullet.y
            )
        ):

            score2 += 1
            bullets.remove(bullet)

            player1.x = 250
            player1.y = 450
            player1.angle = 0

    # DRAW
    draw_background(
        screen
    )

    for obstacle in obstacles:
        obstacle.draw(screen)

    player1.draw(screen)
    player2.draw(screen)

    for bullet in bullets:
        bullet.draw(screen)

    draw_score(
        screen,
        font,
        score1,
        score2
    )

    pygame.display.flip()

    clock.tick(FPS)