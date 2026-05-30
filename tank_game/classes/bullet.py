import pygame
import math

from settings import *


class Bullet:

    def __init__(
        self,
        x,
        y,
        angle,
        owner
    ):

        self.x = x
        self.y = y

        self.angle = angle
        self.owner = owner

        self.speed = BULLET_SPEED
        self.radius = BULLET_RADIUS

        self.bounces = BOUNCE_COUNT

    def move(self):

        self.x += (
            math.cos(
                math.radians(
                    self.angle
                )
            )
            * self.speed
        )

        self.y -= (
            math.sin(
                math.radians(
                    self.angle
                )
            )
            * self.speed
        )

    def draw(self, screen):

        # Glow
        pygame.draw.circle(
            screen,
            BULLET_OUTER,
            (
                int(self.x),
                int(self.y)
            ),
            self.radius
        )

        pygame.draw.circle(
            screen,
            BULLET_INNER,
            (
                int(self.x),
                int(self.y)
            ),
            self.radius // 2
        )