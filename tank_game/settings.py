# ── Screen ─────────────────────────────────────
WIDTH  = 1400
HEIGHT = 900
FPS    = 60

# ── Tank ───────────────────────────────────────
TANK_SPEED      = 3
ROTATION_SPEED  = 3
MAX_HEALTH      = 3

# ── Bullet ─────────────────────────────────────
BULLET_SPEED    = 9
MAX_BULLETS     = 3      # max bullets in flight at once per player

# ── Game ───────────────────────────────────────
WIN_SCORE       = 10     # first to this wins
SPAWN_SHIELD_MS = 2500   # ms of invincibility after respawn

# ── Colours ────────────────────────────────────
GREEN_TANK = ( 60, 200,  80)
RED_TANK   = (220,  55,  55)

# ── Powerup ────────────────────────────────────
POWERUP_INTERVAL_MS = 15000   # new powerup every 15s
POWERUP_TYPES = ["speed", "shield", "rapid"]