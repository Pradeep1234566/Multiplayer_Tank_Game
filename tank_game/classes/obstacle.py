import pygame


class Obstacle:
    """
    Solid wall block — drawn with a metallic look:
    dark fill, bright top-left highlight, dark bottom-right shadow.
    """

    _COL_FILL    = ( 32,  42,  60)
    _COL_EDGE    = ( 22,  30,  46)
    _COL_HILIGHT = ( 70,  95, 140)
    _COL_SHADOW  = ( 12,  16,  28)
    _COL_STRIPE  = ( 40,  55,  80, 40)   # subtle diagonal stripe

    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self._surf = self._build(w, h)

    def _build(self, w, h) -> pygame.Surface:
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        # Base fill
        surf.fill(self._COL_FILL)
        # Top & left highlight
        pygame.draw.line(surf, self._COL_HILIGHT, (0, 0), (w-1, 0), 2)
        pygame.draw.line(surf, self._COL_HILIGHT, (0, 0), (0, h-1), 2)
        # Bottom & right shadow
        pygame.draw.line(surf, self._COL_SHADOW, (0, h-1), (w-1, h-1), 2)
        pygame.draw.line(surf, self._COL_SHADOW, (w-1, 0), (w-1, h-1), 2)
        # Inner edge
        pygame.draw.rect(surf, self._COL_EDGE, (2, 2, w-4, h-4), width=1)
        return surf

    def draw(self, screen: pygame.Surface):
        # Drop shadow
        shadow = pygame.Surface((self.rect.w + 6, self.rect.h + 6), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 60))
        screen.blit(shadow, (self.rect.x + 3, self.rect.y + 3))
        # Main block
        screen.blit(self._surf, self.rect.topleft)