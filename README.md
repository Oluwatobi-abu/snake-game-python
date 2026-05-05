# 🐍 SNAKE — A Classic Snake Game

> A professionally engineered Snake game built in Python and Pygame, featuring advanced gameplay mechanics and structured JSON-based data annotation for performance tracking.

**Author:** Oluwatobi | **GitHub:** [@Oluwatobi-abu](https://github.com/Oluwatobi-abu)

---

## 🎮 Demo

| Feature | Preview |
|---|---|
| Particle burst on eat | ✅ Explosion of color every time you eat |
| Combo multiplier | ✅ Chain up to x8 for massive points |
| Bonus golden food | ✅ Timed food that disappears if you're too slow |
| Snake gradient | ✅ Head-to-tail color fade so you always know direction |
| Game over screen | ✅ Animated overlay with final score and best |

---

## ✨ Features

- 🎇 **Particle System** — physics-based burst effects on every eat and on death
- 🔥 **Combo Scoring** — eat within 3 seconds to chain multipliers up to x8
- ⭐ **Bonus Food** — golden star food spawns randomly and vanishes if ignored
- ⚡ **3 Difficulty Levels** — Easy, Normal, and Hard with switchable speed
- 💾 **Structured JSON Data Storage** — high scores stored in a well-defined schema including metadata, timestamps, and performance labels
- 🎨 **Snake Gradient** — linear-interpolated head-to-tail color
- 🖥️ **60 FPS Game Loop** — delta-time updates, decoupled logic and rendering
- 🎯 **Score Popups** — floating "+points" text on every eat

---

## 🕹️ Controls

| Key | Action |
|---|---|
| `Arrow Keys` / `WASD` | Move the snake |
| `P` | Pause / Unpause |
| `1` / `2` / `3` | Switch difficulty (Easy / Normal / Hard) |
| `R` | Restart after game over |
| `ESC` | Quit |

---

## 🚀 How to Run

### ▶️ Option 1 — Download the Executable (No Python needed)

A prebuilt Windows executable is available on the [**Releases page**](https://github.com/Oluwatobi-abu/snake-game-python/releases/latest).

1. Go to the [Releases page](https://github.com/Oluwatobi-abu/snake-game-python/releases/latest)
2. Download `snake_game.exe` under **Assets**
3. Double-click to run — no installation needed

> ⚠️ Windows may show a SmartScreen warning since the `.exe` is unsigned. Click **"More info" → "Run anyway"** to proceed.

---

### 🐍 Option 2 — Run from Source (Python)

#### Requirements
- Python 3.10 or newer — [download here](https://www.python.org/downloads/)
- Pygame library

#### Installation

```bash
pip install pygame
```

#### Run

```bash
python snake_game.py
```

---

## 🏗️ Code Architecture

The project is structured around clean separation of concerns:

| Class | Responsibility |
|---|---|
| `Snake` | Body list, direction queuing, self-collision detection |
| `ParticleSystem` | Emits, updates, and draws burst particles with gravity |
| `ScoreManager` | Points, combo multipliers, flash popups, JSON high score I/O |
| `Food` | Grid position, type (Normal / Bonus), TTL countdown |
| `Renderer` | All pygame draw calls — completely separate from game logic |
| `Game` | Top-level controller — game loop, state machine, spawning |

This architecture means any system can be extended or swapped independently — a pattern used in professional game studios.

---

## 🧾 JSON Data & Annotation

Beyond simple persistence, this project uses a structured JSON format to simulate real-world data annotation workflows. Each session is recorded with a performance label derived from the score, mirroring how labeled datasets are built for supervised machine learning.

### Schema

```json
{
  "player_id": "demo_user",
  "highscore": 180,
  "metadata": {
    "last_updated": "2026-05-05T18:30:00",
    "game": "snake"
  },
  "performance": {
    "level": "advanced"
  },
  "history": [
    {
      "score": 120,
      "label": "intermediate"
    },
    {
      "score": 180,
      "label": "advanced"
    }
  ]
}
```

### Annotation Labels

| Score Range | Label |
|---|---|
| 0 – 99 | `beginner` |
| 100 – 159 | `intermediate` |
| 160+ | `advanced` |

Each session appended to `history` acts as a labeled data point — useful for analytics, leaderboards, or training a performance prediction model.

---

## 🧮 Scoring System

| Action | Points |
|---|---|
| Eat normal food | 10 × combo multiplier |
| Eat bonus (golden) food | 20 × combo multiplier |
| Eat within 3 seconds | Combo increases (up to x8) |
| Miss the window | Combo resets to x1 |

**Maximum possible:** 160 points per bite at x8 combo on bonus food.

---

## 📁 Project Structure

```
snake-game-python/
├── snake_game.py             # Full game source — single file, fully modular
└── README.md                 # This file
```

> The Windows executable (`snake_game.exe`) is available separately on the [Releases page](https://github.com/Oluwatobi-abu/snake-game-python/releases/latest) and is not tracked in the repository.

---

## 🛠️ Built With

- **Python 3** — core language
- **Pygame** — rendering, input, and game loop
- **PyInstaller** — packaged into a standalone Windows `.exe`
- **JSON** — structured data storage with metadata and derived annotations
- **OOP Design** — Snake, Food, ParticleSystem, ScoreManager, Renderer, Game

---

## 📬 Contact

Built as a portfolio project targeting game industry roles.

- GitHub: [github.com/Oluwatobi-abu](https://github.com/Oluwatobi-abu)
