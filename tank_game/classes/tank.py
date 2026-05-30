import pygame
import math

from settings import *


class Tank:

    def __init__(
        self,
        x,
        y,
        controls,
        color
    ):

        self.x = x
        self.y = y

        self.controls = controls
        self.color = color

        self.speed = TANK_SPEED
        self.rotation_speed = ROTATION_SPEED

        self.angle = 0

        # ---------------- LOAD TANK IMAGE ----------------
        self.tank_image = pygame.image.load(
            "assets/Tank_top.png"
        ).convert_alpha()

        self.tank_image = pygame.transform.scale(
            self.tank_image,
            (110, 110)
        )

    def move(
        self,
        keys,
        obstacles
    ):

        old_x = self.x
        old_y = self.y

        # ---------------- MOVEMENT ----------------
        if keys[
            self.controls["up"]
        ]:
            print("MOVE UP")
            self.y -= self.speed

        if keys[
            self.controls["down"]
        ]:
            self.y += self.speed

        if keys[
            self.controls["left"]
        ]:
            self.x -= self.speed

        if keys[
            self.controls["right"]
        ]:
            self.x += self.speed

        # ---------------- ROTATION ----------------
        if keys[
            self.controls[
                "rotate_left"
            ]
        ]:
            self.angle += (
                self.rotation_speed
            )

        if keys[
            self.controls[
                "rotate_right"
            ]
        ]:
            self.angle -= (
                self.rotation_speed
            )

        # ---------------- SCREEN BOUNDS ----------------
        self.x = max(
            70,
            min(
                WIDTH - 70,
                self.x
            )
        )

        self.y = max(
            70,
            min(
                HEIGHT - 70,
                self.y
            )
        )

        # ---------------- WALL COLLISION ----------------
        for obstacle in obstacles:

            if (
                self.get_rect()
                .colliderect(
                    obstacle.rect
                )
            ):
                self.x = old_x
                self.y = old_y

    def get_rect(self):

        return pygame.Rect(
            self.x - 35,
            self.y - 35,
            70,
            70
        )   

    def draw(
        self,
        screen
    ):

        # ---------------- SHADOW ----------------
        pygame.draw.ellipse(
            screen,
            (15, 15, 15),
            (
                self.x - 50,
                self.y + 40,
                100,
                20
            )
        )

        # ---------------- ROTATE IMAGE ----------------
        # If tank faces UP ↑ change:
        # self.angle → self.angle - 90

        rotated_tank = pygame.transform.rotate(
            self.tank_image,
            self.angle
        )

        # ---------------- CENTER IMAGE ----------------
        rect = rotated_tank.get_rect(
            center=(
                self.x,
                self.y
            )
        )

        # ---------------- DRAW ----------------
        screen.blit(
            rotated_tank,
            rect
        )