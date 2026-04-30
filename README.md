# 🐍 SNAKE — A Classic Snake Game

> A professionally engineered Snake game built from scratch in Python and Pygame, featuring a custom particle system, real-time combo scoring, bonus food mechanics, and a polished dark-arcade aesthetic.

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
- 💾 **Persistent High Score** — saved to a local JSON file across sessions
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

### Requirements
- Python 3.10 or newer — [download here](https://www.python.org/downloads/)
- Pygame library

### Installation

```bash
pip install pygame
```

### Run the game

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
serpent/
├── snake_game.py       # Full game source — single file, fully modular
├── README.md           # This file
└── serpent_highscore.json  # Auto-generated when you play
```

---

## 🛠️ Built With

- **Python 3** — core language
- **Pygame** — rendering, input, and game loop
- **JSON** — lightweight high score persistence
- **OOP Design** — Snake, Food, ParticleSystem, ScoreManager, Renderer, Game

---

## 📬 Contact

Built as a portfolio project targeting game industry roles.

- GitHub: [github.com/Oluwatobi-abu](https://github.com/Oluwatobi-abu)
