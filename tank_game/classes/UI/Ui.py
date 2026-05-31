import pygame
import math
import random

# ════════════════════════════════════════════
#  PALETTE
# ════════════════════════════════════════════
_DARK_BG     = ( 10,  14,  22)
_GRID_LINE   = ( 22,  30,  46)
_BORDER_GLOW = ( 45,  90, 160)
_CORNER_COL  = ( 60, 120, 200)
_PANEL_BG    = ( 18,  24,  40)
_PANEL_EDGE  = ( 50,  80, 140)
_WHITE       = (255, 255, 255)
_GREY        = (120, 130, 155)
_GOLD        = (255, 210,  50)
_P1_COL      = ( 70, 210,  90)
_P2_COL      = (220,  65,  65)
_ACCENT      = ( 80, 160, 255)
_SHIELD_COL  = ( 80, 200, 255)

_EXP_COLS = [
    (255, 255, 180), (255, 220, 80), (255, 160, 30),
    (220,  80,  20), (160,  40, 10), ( 80,  20,  5), (30, 10, 2),
]

_POWERUP_COLS = {
    "speed":  (255, 220,  50),
    "shield": ( 80, 200, 255),
    "rapid":  (255,  80,  80),
}
_POWERUP_LABELS = {
    "speed": "SPD", "shield": "SHD", "rapid": "RPD",
}

# ════════════════════════════════════════════
#  CACHES
# ════════════════════════════════════════════
_bg_surf    = None
_notifs     = []
_NOTIF_DUR  = 200

_score_font  = None
_name_font   = None
_notif_font  = None
_big_font    = None
_title_font  = None
_small_font  = None


def _fonts():
    global _score_font, _name_font, _notif_font, _big_font, _title_font, _small_font
    if _score_font is None:
        _score_font = pygame.font.Font(None, 80)
        _name_font  = pygame.font.Font(None, 24)
        _notif_font = pygame.font.Font(None, 28)
        _big_font   = pygame.font.Font(None, 48)
        _title_font = pygame.font.Font(None, 120)
        _small_font = pygame.font.Font(None, 30)


# ════════════════════════════════════════════
#  BACKGROUND
# ════════════════════════════════════════════
def _build_bg(w, h):
    surf = pygame.Surface((w, h))
    surf.fill(_DARK_BG)
    for x in range(0, w, 80):
        pygame.draw.line(surf, _GRID_LINE, (x, 0), (x, h), 1)
    for y in range(0, h, 80):
        pygame.draw.line(surf, _GRID_LINE, (0, y), (w, y), 1)
    vig = pygame.Surface((w, h), pygame.SRCALPHA)
    for step in range(12):
        alpha  = int(6 * (12 - step))
        margin = step * 40
        pygame.draw.rect(vig, (0, 0, 0, alpha),
                         (margin, margin, w - margin*2, h - margin*2), width=40)
    surf.blit(vig, (0, 0))
    return surf


def draw_background(screen):
    global _bg_surf
    if _bg_surf is None:
        _bg_surf = _build_bg(screen.get_width(), screen.get_height())
    screen.blit(_bg_surf, (0, 0))


# ════════════════════════════════════════════
#  ARENA BORDER
# ════════════════════════════════════════════
def draw_arena(screen):
    w, h = screen.get_width(), screen.get_height()
    M, CL, CT = 18, 28, 3
    for i, alpha in enumerate([15, 25, 40, 60]):
        glow = pygame.Surface((w, h), pygame.SRCALPHA)
        m = M - i * 2
        pygame.draw.rect(glow, (*_BORDER_GLOW, alpha),
                         (m, m, w - m*2, h - m*2), width=2)
        screen.blit(glow, (0, 0))
    pygame.draw.rect(screen, _BORDER_GLOW, (M, M, w - M*2, h - M*2), width=1)
    for ax, ay, hd, vd in [
        (M,     M,      CL,  CL),
        (w - M, M,     -CL,  CL),
        (M,     h - M,  CL, -CL),
        (w - M, h - M, -CL, -CL),
    ]:
        pygame.draw.line(screen, _CORNER_COL, (ax, ay), (ax + hd, ay), CT)
        pygame.draw.line(screen, _CORNER_COL, (ax, ay), (ax, ay + vd), CT)


# ════════════════════════════════════════════
#  KILL FEED
# ════════════════════════════════════════════
def push_kill_notif(killer, victim):
    _notifs.append({"killer": killer, "victim": victim, "frames": _NOTIF_DUR})
    if len(_notifs) > 5:
        _notifs.pop(0)


# ════════════════════════════════════════════
#  SCORE HUD
# ════════════════════════════════════════════
def draw_score(screen, font, my_score, enemy_score, player_id=0,
               my_powerup=None, win_score=10):
    _fonts()
    W = screen.get_width()
    my_col    = _P1_COL if player_id == 0 else _P2_COL
    enemy_col = _P2_COL if player_id == 0 else _P1_COL

    # ── Score panel ─────────────────────────
    PW, PH = 360, 95
    PX = W // 2 - PW // 2
    PY = 10

    panel = pygame.Surface((PW, PH), pygame.SRCALPHA)
    panel.fill((*_PANEL_BG, 230))
    pygame.draw.rect(panel, (*_PANEL_EDGE, 255), (0, 0, PW, PH), width=1, border_radius=8)
    screen.blit(panel, (PX, PY))

    acc = pygame.Surface((PW - 2, 3), pygame.SRCALPHA)
    acc.fill((*_ACCENT, 180))
    screen.blit(acc, (PX + 1, PY + 1))

    mid_x = PX + PW // 2
    pygame.draw.line(screen, _PANEL_EDGE, (mid_x, PY + 10), (mid_x, PY + PH - 10), 1)

    vs = _name_font.render("VS", True, _GREY)
    screen.blit(vs, (mid_x - vs.get_width() // 2, PY + PH // 2 - vs.get_height() // 2))

    you_s   = _name_font.render("YOU",   True, my_col)
    enemy_s = _name_font.render("ENEMY", True, enemy_col)
    screen.blit(you_s,   (PX + 16, PY + 12))
    screen.blit(enemy_s, (PX + PW - 16 - enemy_s.get_width(), PY + 12))

    s1 = _score_font.render(str(my_score),    True, _WHITE)
    s2 = _score_font.render(str(enemy_score), True, _WHITE)
    half    = PW // 2
    score_y = PY + PH // 2 - s1.get_height() // 2 + 6
    screen.blit(s1, (PX + (half - s1.get_width()) // 2, score_y))
    screen.blit(s2, (mid_x + (half - s2.get_width()) // 2, score_y))

    # Win score progress bars
    for side, score, col, base_x in [
        ("my",    my_score,    my_col,    PX + 10),
        ("enemy", enemy_score, enemy_col, mid_x + 5),
    ]:
        bar_w = half - 15
        bar_h = 4
        bar_y = PY + PH - 10
        bx    = base_x
        pygame.draw.rect(screen, (40, 40, 55), (bx, bar_y, bar_w, bar_h), border_radius=2)
        fill = int(bar_w * min(score, win_score) / win_score)
        if fill > 0:
            pygame.draw.rect(screen, col, (bx, bar_y, fill, bar_h), border_radius=2)

    # ── Active powerup indicator ─────────────
    if my_powerup:
        col   = _POWERUP_COLS.get(my_powerup, _WHITE)
        label = _POWERUP_LABELS.get(my_powerup, "?")
        pu_s  = _small_font.render(f"[ {label} ]", True, col)
        screen.blit(pu_s, (10, 10))

    # ── Kill feed ────────────────────────────
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


# ════════════════════════════════════════════
#  WAITING SCREEN
# ════════════════════════════════════════════
def draw_waiting_screen(screen, player_id):
    _fonts()
    W, H = screen.get_width(), screen.get_height()

    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    col = _P1_COL if player_id == 0 else _P2_COL

    title = _title_font.render("TANK BATTLE", True, col)
    screen.blit(title, (W // 2 - title.get_width() // 2, H // 2 - 120))

    dot_count = (pygame.time.get_ticks() // 400) % 4
    wait = _big_font.render("Waiting for opponent" + "." * dot_count, True, _WHITE)
    screen.blit(wait, (W // 2 - wait.get_width() // 2, H // 2 + 20))

    pid_s = _small_font.render(f"You are Player {player_id + 1}", True, _GREY)
    screen.blit(pid_s, (W // 2 - pid_s.get_width() // 2, H // 2 + 80))


# ════════════════════════════════════════════
#  WIN SCREEN
# ════════════════════════════════════════════
def draw_win_screen(screen, winner_id, my_player_id):
    _fonts()
    W, H = screen.get_width(), screen.get_height()

    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    i_won = (winner_id == my_player_id)
    col   = _P1_COL if my_player_id == 0 else _P2_COL

    if i_won:
        text = "YOU WIN!"
        col  = _GOLD
    else:
        text = "YOU LOSE"
        col  = _P2_COL if my_player_id == 0 else _P1_COL

    title = _title_font.render(text, True, col)
    screen.blit(title, (W // 2 - title.get_width() // 2, H // 2 - 100))

    restart = _big_font.render("Hold  R  to restart", True, _WHITE)
    screen.blit(restart, (W // 2 - restart.get_width() // 2, H // 2 + 40))


# ════════════════════════════════════════════
#  POWERUP
# ════════════════════════════════════════════
def draw_powerup(screen, x, y, kind):
    _fonts()
    t     = pygame.time.get_ticks() / 1000
    pulse = 0.5 + 0.5 * math.sin(t * 3)
    col   = _POWERUP_COLS.get(kind, _WHITE)
    label = _POWERUP_LABELS.get(kind, "?")

    # Outer glow ring
    r    = int(20 + pulse * 4)
    surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(surf, (*col, int(60 + pulse * 60)), (r + 2, r + 2), r, 3)
    screen.blit(surf, (int(x) - r - 2, int(y) - r - 2))

    # Solid inner circle
    pygame.draw.circle(screen, col, (int(x), int(y)), 14)
    pygame.draw.circle(screen, _DARK_BG, (int(x), int(y)), 11)

    lbl = _name_font.render(label, True, col)
    screen.blit(lbl, (int(x) - lbl.get_width() // 2, int(y) - lbl.get_height() // 2))


# ════════════════════════════════════════════
#  SHIELD RING
# ════════════════════════════════════════════
def draw_shield_ring(screen, x, y, time_left, max_time):
    t     = pygame.time.get_ticks() / 1000
    pulse = 0.5 + 0.5 * math.sin(t * 6)
    alpha = int(120 + pulse * 80)
    r     = 46

    surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(surf, (*_SHIELD_COL, alpha), (r + 2, r + 2), r, 3)

    # Arc showing time remaining
    if max_time > 0:
        ratio  = min(1.0, time_left / max_time)
        deg    = int(360 * ratio)
        if deg > 2:
            arc_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.arc(arc_surf, (*_SHIELD_COL, 200),
                            (2, 2, r * 2, r * 2),
                            math.radians(90),
                            math.radians(90 + deg), 4)
            surf.blit(arc_surf, (0, 0))

    screen.blit(surf, (int(x) - r - 2, int(y) - r - 2))


# ════════════════════════════════════════════
#  EXPLOSION
# ════════════════════════════════════════════
def draw_explosion(screen, x, y, frame, max_frames):
    progress = frame / max_frames
    if progress >= 1.0:
        return
    big = max_frames > 20

    ring_r = int(progress * (80 if big else 40))
    if ring_r > 2:
        ci = min(len(_EXP_COLS) - 1, int(progress * len(_EXP_COLS)))
        rs = pygame.Surface((ring_r*2+2, ring_r*2+2), pygame.SRCALPHA)
        pygame.draw.circle(rs, (*_EXP_COLS[ci], int(200*(1-progress))),
                           (ring_r+1, ring_r+1), ring_r, 2)
        screen.blit(rs, (int(x)-ring_r-1, int(y)-ring_r-1))

    core_r = int((1 - progress) * (30 if big else 15))
    if core_r > 0:
        ci = min(len(_EXP_COLS) - 1, int(progress * len(_EXP_COLS)))
        ca = min(255, int(255 * (1 - progress) * 1.5))
        cs = pygame.Surface((core_r*2+2, core_r*2+2), pygame.SRCALPHA)
        pygame.draw.circle(cs, (*_EXP_COLS[ci], ca), (core_r+1, core_r+1), core_r)
        screen.blit(cs, (int(x)-core_r-1, int(y)-core_r-1))

    rng = random.Random(int(x * 31 + y * 17))
    for _ in range(10 if big else 6):
        angle = rng.uniform(0, math.pi * 2)
        dist  = progress * rng.uniform(0.3, 1.0) * (60 if big else 30)
        sx    = x + math.cos(angle) * dist
        sy    = y + math.sin(angle) * dist
        ci    = min(len(_EXP_COLS) - 1, int(progress * len(_EXP_COLS)))
        sz    = max(1, int((1 - progress) * 5))
        ss    = pygame.Surface((sz*2+2, sz*2+2), pygame.SRCALPHA)
        pygame.draw.circle(ss, (*_EXP_COLS[ci], int(255*(1-progress))), (sz+1, sz+1), sz)
        screen.blit(ss, (int(sx)-sz-1, int(sy)-sz-1))


# ════════════════════════════════════════════
#  MUZZLE FLASH
# ════════════════════════════════════════════
def draw_muzzle_flash(screen, x, y, angle_deg, frame):
    if frame >= 6:
        return
    progress = frame / 6
    alpha = int(255 * (1 - progress))
    size  = int(18 * (1 - progress * 0.5))
    surf  = pygame.Surface((size*4, size*4), pygame.SRCALPHA)
    pygame.draw.circle(surf, (255, 240, 140, alpha), (size*2, size*2), size)
    pygame.draw.circle(surf, (255, 180, 60, alpha//2), (size*2, size*2), int(size*1.8), 3)
    screen.blit(surf, (int(x) - size*2, int(y) - size*2))


# ════════════════════════════════════════════
#  BULLET TRAIL
# ════════════════════════════════════════════
def draw_bullet_trail(screen, trail, color=(80, 200, 90)):
    if len(trail) < 2:
        return
    for i in range(1, len(trail)):
        alpha = int(200 * (i / len(trail)))
        width = max(1, int(3 * (i / len(trail))))
        p1, p2 = trail[i-1], trail[i]
        x0, y0 = int(p1[0]), int(p1[1])
        x1, y1 = int(p2[0]), int(p2[1])
        mx = min(x0, x1) - width - 1
        my = min(y0, y1) - width - 1
        mw = abs(x1 - x0) + width*2 + 2
        mh = abs(y1 - y0) + width*2 + 2
        if mw < 1 or mh < 1:
            continue
        ts = pygame.Surface((mw, mh), pygame.SRCALPHA)
        pygame.draw.line(ts, (*color, alpha),
                         (x0-mx, y0-my), (x1-mx, y1-my), width)
        screen.blit(ts, (mx, my))