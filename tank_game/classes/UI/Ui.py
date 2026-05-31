"""
UI.py  —  All drawing utilities for Tank Battle.

Exports:
    draw_background(screen)
    draw_arena(screen)
    draw_score(screen, font, my_score, enemy_score, player_id)
    draw_explosion(screen, x, y, frame, max_frames)
    draw_muzzle_flash(screen, x, y, angle_deg, frame)
    draw_bullet_trail(screen, trail, color)
    push_kill_notif(killer, victim)
"""

import pygame
import math
import random

# ════════════════════════════════════════
#  PALETTE
# ════════════════════════════════════════
_DARK_BG      = ( 10,  14,  22)
_GRID_LINE    = ( 22,  30,  46)
_BORDER_GLOW  = ( 45,  90, 160)
_CORNER_COL   = ( 60, 120, 200)

_PANEL_BG     = ( 18,  24,  40)
_PANEL_EDGE   = ( 50,  80, 140)
_WHITE        = (255, 255, 255)
_GREY         = (120, 130, 155)
_GOLD         = (255, 210,  50)
_P1_COL       = ( 70, 210,  90)
_P2_COL       = (220,  65,  65)
_ACCENT       = ( 80, 160, 255)

_EXP_COLS = [
    (255, 255, 180),
    (255, 220,  80),
    (255, 160,  30),
    (220,  80,  20),
    (160,  40,  10),
    ( 80,  20,   5),
    ( 30,  10,   2),
]

# ════════════════════════════════════════
#  MODULE-LEVEL CACHES
# ════════════════════════════════════════
_bg_surf    = None
_notifs     = []
_NOTIF_DUR  = 200

_score_font = None
_name_font  = None
_notif_font = None


def _init_fonts():
    global _score_font, _name_font, _notif_font
    if _score_font is None:
        _score_font = pygame.font.Font(None, 80)
        _name_font  = pygame.font.Font(None, 24)
        _notif_font = pygame.font.Font(None, 28)


# ════════════════════════════════════════
#  BACKGROUND
# ════════════════════════════════════════
def _build_bg(w, h):
    surf = pygame.Surface((w, h))
    surf.fill(_DARK_BG)
    GRID = 80
    for x in range(0, w, GRID):
        pygame.draw.line(surf, _GRID_LINE, (x, 0), (x, h), 1)
    for y in range(0, h, GRID):
        pygame.draw.line(surf, _GRID_LINE, (0, y), (w, y), 1)
    vignette = pygame.Surface((w, h), pygame.SRCALPHA)
    for step in range(12):
        alpha  = int(6 * (12 - step))
        margin = step * 40
        pygame.draw.rect(
            vignette, (0, 0, 0, alpha),
            (margin, margin, w - margin * 2, h - margin * 2),
            width=40,
        )
    surf.blit(vignette, (0, 0))
    return surf


def draw_background(screen):
    global _bg_surf
    if _bg_surf is None:
        _bg_surf = _build_bg(screen.get_width(), screen.get_height())
    screen.blit(_bg_surf, (0, 0))


# ════════════════════════════════════════
#  ARENA BORDER
# ════════════════════════════════════════
def draw_arena(screen):
    """Glowing border + corner L-brackets."""
    w, h = screen.get_width(), screen.get_height()
    M  = 18
    CL = 28
    CT = 3

    # Layered glow
    for i, alpha in enumerate([15, 25, 40, 60]):
        glow = pygame.Surface((w, h), pygame.SRCALPHA)
        m = M - i * 2
        pygame.draw.rect(
            glow, (*_BORDER_GLOW, alpha),
            (m, m, w - m * 2, h - m * 2),
            width=2,
        )
        screen.blit(glow, (0, 0))

    # Solid border
    pygame.draw.rect(screen, _BORDER_GLOW, (M, M, w - M * 2, h - M * 2), width=1)

    # Corner brackets: (anchor_x, anchor_y, horiz_dir, vert_dir)
    for ax, ay, hd, vd in [
        (M,     M,     +CL, +CL),
        (w - M, M,     -CL, +CL),
        (M,     h - M, +CL, -CL),
        (w - M, h - M, -CL, -CL),
    ]:
        pygame.draw.line(screen, _CORNER_COL, (ax, ay), (ax + hd, ay), CT)
        pygame.draw.line(screen, _CORNER_COL, (ax, ay), (ax, ay + vd), CT)


# ════════════════════════════════════════
#  KILL NOTIFICATIONS
# ════════════════════════════════════════
def push_kill_notif(killer, victim):
    _notifs.append({"killer": killer, "victim": victim, "frames": _NOTIF_DUR})
    if len(_notifs) > 5:
        _notifs.pop(0)


# ════════════════════════════════════════
#  SCORE HUD
# ════════════════════════════════════════
def draw_score(screen, font, my_score, enemy_score, player_id=0):
    _init_fonts()
    W = screen.get_width()

    my_col    = _P1_COL if player_id == 0 else _P2_COL
    enemy_col = _P2_COL if player_id == 0 else _P1_COL

    PW, PH = 340, 90
    PX = W // 2 - PW // 2
    PY = 10

    # Panel
    panel = pygame.Surface((PW, PH), pygame.SRCALPHA)
    panel.fill((*_PANEL_BG, 230))
    pygame.draw.rect(panel, (*_PANEL_EDGE, 255), (0, 0, PW, PH), width=1, border_radius=8)
    screen.blit(panel, (PX, PY))

    # Top accent bar
    acc = pygame.Surface((PW - 2, 3), pygame.SRCALPHA)
    acc.fill((*_ACCENT, 180))
    screen.blit(acc, (PX + 1, PY + 1))

    # Centre divider + VS label
    mid_x = PX + PW // 2
    pygame.draw.line(screen, _PANEL_EDGE, (mid_x, PY + 10), (mid_x, PY + PH - 10), 1)
    vs = _name_font.render("VS", True, _GREY)
    screen.blit(vs, (mid_x - vs.get_width() // 2, PY + PH // 2 - vs.get_height() // 2))

    # Name labels
    you_s   = _name_font.render("YOU",   True, my_col)
    enemy_s = _name_font.render("ENEMY", True, enemy_col)
    screen.blit(you_s,   (PX + 16,                            PY + 12))
    screen.blit(enemy_s, (PX + PW - 16 - enemy_s.get_width(), PY + 12))

    # Big score numbers
    s1 = _score_font.render(str(my_score),    True, _WHITE)
    s2 = _score_font.render(str(enemy_score), True, _WHITE)
    half    = PW // 2
    score_y = PY + PH // 2 - s1.get_height() // 2 + 6
    screen.blit(s1, (PX + (half - s1.get_width()) // 2,      score_y))
    screen.blit(s2, (mid_x + (half - s2.get_width()) // 2,   score_y))

    # Kill feed
    feed_y = PY + PH + 6
    for notif in _notifs[:]:
        alpha = min(255, notif["frames"] * 4)
        text  = "  {}  x  {}  ".format(notif["killer"], notif["victim"])
        surf  = _notif_font.render(text, True, _GOLD)
        surf.set_alpha(alpha)
        pill  = pygame.Surface((surf.get_width() + 4, surf.get_height() + 4), pygame.SRCALPHA)
        pill.fill((0, 0, 0, min(160, alpha // 2)))
        pill.blit(surf, (2, 2))
        screen.blit(pill, (W // 2 - pill.get_width() // 2, feed_y))
        feed_y += pill.get_height() + 3
        notif["frames"] -= 1
        if notif["frames"] <= 0:
            _notifs.remove(notif)


# ════════════════════════════════════════
#  EXPLOSION
# ════════════════════════════════════════
def draw_explosion(screen, x, y, frame, max_frames):
    progress = frame / max_frames
    if progress >= 1.0:
        return

    big = max_frames > 20

    # Shockwave ring
    ring_r = int(progress * (80 if big else 40))
    if ring_r > 2:
        ring_alpha = int(200 * (1 - progress))
        ci  = min(len(_EXP_COLS) - 1, int(progress * len(_EXP_COLS)))
        rs  = pygame.Surface((ring_r * 2 + 2, ring_r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(rs, (*_EXP_COLS[ci], ring_alpha),
                           (ring_r + 1, ring_r + 1), ring_r, 2)
        screen.blit(rs, (int(x) - ring_r - 1, int(y) - ring_r - 1))

    # Core flash
    core_r = int((1 - progress) * (30 if big else 15))
    if core_r > 0:
        ci  = min(len(_EXP_COLS) - 1, int(progress * len(_EXP_COLS)))
        ca  = min(255, int(255 * (1 - progress) * 1.5))
        cs  = pygame.Surface((core_r * 2 + 2, core_r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(cs, (*_EXP_COLS[ci], ca),
                           (core_r + 1, core_r + 1), core_r)
        screen.blit(cs, (int(x) - core_r - 1, int(y) - core_r - 1))

    # Sparks (seeded so they don't jitter frame-to-frame)
    rng = random.Random(int(x * 31 + y * 17))
    for _ in range(10 if big else 6):
        angle = rng.uniform(0, math.pi * 2)
        dist  = progress * rng.uniform(0.3, 1.0) * (60 if big else 30)
        sx    = x + math.cos(angle) * dist
        sy    = y + math.sin(angle) * dist
        sa    = int(255 * (1 - progress))
        ci    = min(len(_EXP_COLS) - 1, int(progress * len(_EXP_COLS)))
        sz    = max(1, int((1 - progress) * 5))
        ss    = pygame.Surface((sz * 2 + 2, sz * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(ss, (*_EXP_COLS[ci], sa), (sz + 1, sz + 1), sz)
        screen.blit(ss, (int(sx) - sz - 1, int(sy) - sz - 1))


# ════════════════════════════════════════
#  MUZZLE FLASH
# ════════════════════════════════════════
def draw_muzzle_flash(screen, x, y, angle_deg, frame):
    if frame >= 6:
        return
    progress = frame / 6
    alpha    = int(255 * (1 - progress))
    size     = int(18 * (1 - progress * 0.5))
    surf     = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
    pygame.draw.circle(surf, (255, 240, 140, alpha),      (size * 2, size * 2), size)
    pygame.draw.circle(surf, (255, 180,  60, alpha // 2), (size * 2, size * 2), int(size * 1.8), 3)
    screen.blit(surf, (int(x) - size * 2, int(y) - size * 2))


# ════════════════════════════════════════
#  BULLET TRAIL
# ════════════════════════════════════════
def draw_bullet_trail(screen, trail, color=(80, 200, 90)):
    if len(trail) < 2:
        return
    for i in range(1, len(trail)):
        alpha = int(200 * (i / len(trail)))
        width = max(1, int(3 * (i / len(trail))))
        p1, p2 = trail[i - 1], trail[i]
        # pygame.draw.line doesn't support alpha natively,
        # so we draw onto a temp surface and blit
        x0, y0 = int(p1[0]), int(p1[1])
        x1, y1 = int(p2[0]), int(p2[1])
        mx = min(x0, x1) - width - 1
        my = min(y0, y1) - width - 1
        mw = abs(x1 - x0) + width * 2 + 2
        mh = abs(y1 - y0) + width * 2 + 2
        if mw < 1 or mh < 1:
            continue
        ts = pygame.Surface((mw, mh), pygame.SRCALPHA)
        pygame.draw.line(
            ts, (*color, alpha),
            (x0 - mx, y0 - my),
            (x1 - mx, y1 - my),
            width,
        )
        screen.blit(ts, (mx, my))









