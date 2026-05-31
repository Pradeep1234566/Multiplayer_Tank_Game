# 🎮 Tank Battle — Online Multiplayer Game

A real-time **2-player online multiplayer tank game** built from scratch in Python using Pygame and TCP sockets. Two players connect over the internet, control tanks, shoot bouncing projectiles, and compete to reach the win score.

![Tank Battle Screenshot](assets/screenshot.png)

---

## ✨ Features

- **Real-time online multiplayer** — Two players connect over the internet via TCP sockets
- **Client-server architecture** — Dedicated server handles game state, hit detection, and synchronization
- **Power-up system** — Speed boost, Shield, and Rapid Fire power-ups spawn on the field
- **Spawn shield** — 2.5 second invincibility after respawning
- **Screen shake** — Dynamic camera shake on hits and explosions
- **Visual effects** — Muzzle flash, bullet trails, explosions, and kill notifications
- **Health system** — 3 HP per tank with color-coded health bars (green → yellow → red)
- **Score tracking** — First to 10 kills wins
- **Obstacle map** — Strategic wall placements for tactical gameplay
- **Hit flash** — Red tint animation when tank takes damage
- **Smooth rendering** — 60 FPS with layered rendering and drop shadows

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Game Engine | Pygame |
| Networking | Python `socket` (TCP) |
| Serialization | Python `pickle` |
| Architecture | Client-Server with threading |
| Language | Python 3.10+ |
| Tunneling (for online play) | Playit.gg |

---

## 🏗️ Architecture

```
├── main.py          # Game loop, rendering, input handling (client)
├── server.py        # Game server — state management, hit detection, sync
├── network.py       # TCP socket client wrapper
├── settings.py      # Game constants (speed, FPS, colors, etc.)
├── classes/
│   ├── tank.py      # Tank class — movement, drawing, hit flash
│   ├── bullet.py    # Bullet class — physics, glow rendering
│   ├── obstacle.py  # Obstacle class — metallic wall rendering
│   └── UI/
│       └── Ui.py    # HUD, score, explosions, power-up UI
└── assets/
    └── Tank_top.png # Tank sprite
```

### How the networking works:
1. Server runs on port 5555, waits for 2 players
2. Each client sends its position, angle, and bullet data every frame
3. Server processes hit detection, power-ups, and scoring authoritatively
4. Server sends back enemy state, health, score, and game events
5. Client renders both tanks based on server response

---

## 🎮 Controls

| Action | Player 1 | Player 2 |
|---|---|---|
| Move | `W A S D` | `W A S D` |
| Rotate Left | `Q` | `Q` |
| Rotate Right | `E` | `E` |
| Shoot | `SPACE` | `SPACE` |
| Restart | `R` | `R` |

> In online mode, each player uses the same keys on their own machine.

---

## ⚡ Power-ups

| Power-up | Effect | Duration |
|---|---|---|
| 🟡 Speed | 1.8x movement speed | 8 seconds |
| 🔵 Shield | Absorbs one hit | 8 seconds |
| 🔴 Rapid Fire | Reduced shoot cooldown | 8 seconds |

Power-ups spawn in the center of the map every 15 seconds (max 3 at a time).

---

## 🚀 How to Run

### Prerequisites
```bash
pip install pygame
```

### Local Network (Same WiFi)
```bash
# Terminal 1 — Start server
python server.py

# Terminal 2 & 3 — Start clients
python main.py
```

### Online Multiplayer (via Playit.gg)
1. Download [Playit.gg](https://playit.gg)
2. Host creates a TCP tunnel on port 5555
3. Share the tunnel address with the other player
4. In `network.py`, update `SERVER` to the tunnel address
5. Both players run `python main.py`

---

## 🔧 Configuration

Edit `settings.py` to customize:

```python
FPS          = 60      # Frame rate
TANK_SPEED   = 3       # Tank movement speed
BULLET_SPEED = 9       # Projectile speed
MAX_BULLETS  = 3       # Max bullets in flight per player
WIN_SCORE    = 10      # Score to win
MAX_HEALTH   = 3       # HP per tank
SPAWN_SHIELD_MS = 2500 # Spawn invincibility in ms
```

---

## 🧠 What I Learned

- TCP socket programming and client-server architecture in Python
- Real-time game state synchronization across the network
- Authoritative server design for multiplayer games (server owns game logic)
- Thread-safe shared state using Python `threading.Lock`
- Pygame rendering pipeline — layered surfaces, alpha blending, sprite rotation
- Object-oriented game architecture with separate classes for each game entity

---

## 📋 Known Limitations

- No UDP support yet (TCP can cause latency on poor connections)
- Requires Playit.gg or port forwarding for internet play
- Single map — more maps planned

---

## 🔮 Planned Features

- [ ] UDP networking for lower latency
- [ ] Multiple maps
- [ ] Lobby system
- [ ] Sound effects
- [ ] Mobile support

---

## 👤 Author

**Pradeep Pawar** — [GitHub](https://github.com/Pradeep1234566) | [LinkedIn](https://linkedin.com/in/pradeep-pawar-64345126a)
