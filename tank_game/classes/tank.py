import pygame
import math
from settings import *


class Tank:
    """
    Tank — drawn as a loaded PNG sprite with:
      • smooth health bar (green → yellow → red)
      • hit-flash red tint
      • callsign label below health bar
    """

    def __init__(self, x, y, controls, color):
        self.x = x
        self.y = y
        self.max_health = MAX_HEALTH
        self.health     = MAX_HEALTH
        self.controls   = controls
        self.color      = color   # colour tuple used for tinting + bullets
        self.speed          = TANK_SPEED
        self.rotation_speed = ROTATION_SPEED
        self.angle = 0

        # ── Image ────────────────────────────
        raw = pygame.image.load("assets/Tank_top.png").convert_alpha()
        self.tank_image = pygame.transform.scale(raw, (110, 110))

        # Colour-tint a copy for this player's team colour
        tinted = self.tank_image.copy()
        tinted.fill((*color[:3], 60), special_flags=pygame.BLEND_RGBA_ADD)
        self.tank_image = tinted

        # ── Hit flash ────────────────────────
        self._flash_frames  = 0
        self._FLASH_MAX     = 14

        # ── Label ────────────────────────────
        self._label_font  = pygame.font.Font(None, 22)
        is_green = (color == GREEN_TANK)
        self._label_text  = "P1" if is_green else "P2"
        self._label_color = ( 80, 220,  90) if is_green else (220, 70, 70)

        # ── Health bar dims ──────────────────
        self._BW = 64
        self._BH =  9

    # ─────────────────────────────────────────
    def take_hit(self):
        self._flash_frames = self._FLASH_MAX

    # ─────────────────────────────────────────
    def move(self, keys, obstacles):
        old_x, old_y = self.x, self.y

        if keys[self.controls["up"]]:    self.y -= self.speed
        if keys[self.controls["down"]]:  self.y += self.speed
        if keys[self.controls["left"]]:  self.x -= self.speed
        if keys[self.controls["right"]]: self.x += self.speed
        if keys[self.controls["rotate_left"]]:  self.angle += self.rotation_speed
        if keys[self.controls["rotate_right"]]: self.angle -= self.rotation_speed

        self.x = max(70, min(WIDTH  - 70, self.x))
        self.y = max(70, min(HEIGHT - 70, self.y))

        # for obs in obstacles:
        #     if self.get_rect().colliderect(obs.rect):
        #         self.x, self.y = old_x, old_y
        #         break

    # ─────────────────────────────────────────
    def get_rect(self):
        return pygame.Rect(self.x - 35, self.y - 35, 70, 70)

    # ─────────────────────────────────────────
    def draw(self, screen):
        # Shadow
        pygame.draw.ellipse(
            screen, (8, 10, 16),
            (self.x - 52, self.y + 38, 104, 22),
        )

        # Rotate image
        rotated = pygame.transform.rotate(self.tank_image, self.angle)
        rect    = rotated.get_rect(center=(self.x, self.y))

        # Hit flash
        if self._flash_frames > 0:
            flash = rotated.copy()
            t = self._flash_frames / self._FLASH_MAX
            flash.fill((255, 30, 30, int(190 * t)), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(rotated, rect)
            screen.blit(flash, rect)
            self._flash_frames -= 1
        else:
            screen.blit(rotated, rect)

        # ── Health bar ──────────────────────
        bx = self.x - self._BW // 2
        by = self.y - 74

        ratio = max(0.0, self.health / self.max_health)

        # Background track
        pygame.draw.rect(screen, (35, 35, 45),
                         (bx - 1, by - 1, self._BW + 2, self._BH + 2),
                         border_radius=5)
        pygame.draw.rect(screen, (55, 55, 65),
                         (bx, by, self._BW, self._BH),
                         border_radius=5)

        # Coloured fill
        if ratio > 0.6:
            bar_col = ( 55, 220,  75)
        elif ratio > 0.3:
            bar_col = (230, 185,  15)
        else:
            bar_col = (220,  45,  45)

        fw = int(self._BW * ratio)
        if fw > 2:
            pygame.draw.rect(screen, bar_col,
                             (bx, by, fw, self._BH),
                             border_radius=5)

        # Pip separators (every 33%)
        for pip in [1, 2]:
            px = bx + int(self._BW * pip / self.max_health)
            pygame.draw.line(screen, (20, 20, 30),
                             (px, by), (px, by + self._BH), 1)

        # ── Label ───────────────────────────
        lbl = self._label_font.render(self._label_text, True, self._label_color)
        screen.blit(lbl, (self.x - lbl.get_width() // 2, by - lbl.get_height() - 2))