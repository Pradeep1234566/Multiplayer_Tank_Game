import pygame
import math
from settings import *


class Bullet:
    """
    Projectile — glowing dot with a bright core.
    """

    SPEED = BULLET_SPEED

    def __init__(self, x, y, angle, owner):
        self.x     = float(x)
        self.y     = float(y)
        self.angle = angle
        self.owner = owner

        rad = math.radians(angle)
        self.vx =  math.cos(rad) * self.SPEED
        self.vy = -math.sin(rad) * self.SPEED

        # Colour derived from owner colour
        c = getattr(owner, "color", (255, 255, 100))
        self._core_col  = (255, 255, 200)
        self._outer_col = (c[0], c[1], min(255, c[2] + 60))

    def move(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, screen: pygame.Surface):
        ix, iy = int(self.x), int(self.y)

        # Soft outer glow
        glow = pygame.Surface((18, 18), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self._outer_col, 60), (9, 9), 9)
        screen.blit(glow, (ix - 9, iy - 9))

        # Mid ring
        pygame.draw.circle(screen, self._outer_col, (ix, iy), 5)

        # Bright core
        pygame.draw.circle(screen, self._core_col, (ix, iy), 3)