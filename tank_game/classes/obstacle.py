import pygame

from settings import *


class Obstacle:

    def __init__(
        self,
        x,
        y,
        width,
        height
    ):

        self.rect = pygame.Rect(
            x,
            y,
            width,
            height
        )

    def draw(self, screen):

        pygame.draw.rect(
            screen,
            OBSTACLE_COLOR,
            self.rect,
            border_radius=12
        )

        pygame.draw.rect(
            screen,
            OBSTACLE_BORDER,
            self.rect,
            width=3,
            border_radius=12
        )