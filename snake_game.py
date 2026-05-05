"""
╔══════════════════════════════════════════════════════════════╗
║              S N A K E  —  A Classic Snake Game              ║
║                  by Oluwatobi (github: Oluwatobi-abu)        ║
║                                                              ║
║  Built with: Python 3 + Pygame                               ║
║  Features: Particle FX · Combo System · Difficulty Levels    ║
║             High Score · Smooth Animations · Sound Effects   ║
╚══════════════════════════════════════════════════════════════╝

Controls:
  Arrow Keys / WASD  — Move snake
  P                  — Pause
  R                  — Restart (after game over)
  1 / 2 / 3          — Change difficulty (Easy / Normal / Hard)
  ESC                — Quit

Requirements:
  pip install pygame
"""

import pygame
import random
import math
import json
import datetime
import os
import sys
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum

# ─────────────────────────────────────────────
# CONSTANTS & CONFIG
# ─────────────────────────────────────────────

WINDOW_W, WINDOW_H = 900, 700
GRID_COLS, GRID_ROWS = 30, 25
CELL  = 20
GRID_X = (WINDOW_W - GRID_COLS * CELL) // 2      # 150
GRID_Y = (WINDOW_H - GRID_ROWS * CELL) // 2 + 30 # ~95

FPS = 60
HIGHSCORE_FILE = "snake_highscore.json"

# Colour palette — dark arcade aesthetic
BG        = (10, 10, 18)
GRID_LINE = (18, 18, 32)
PANEL_BG  = (14, 14, 26)
ACCENT    = (0, 255, 160)    # neon green
ACCENT2   = (255, 60, 120)   # neon pink
GOLD      = (255, 215, 0)
WHITE     = (240, 240, 255)
GRAY      = (100, 100, 130)
SNAKE_HEAD = (0, 230, 140)
SNAKE_BODY = (0, 180, 100)
SNAKE_TAIL = (0, 120, 70)
FOOD_COL   = (255, 80, 100)
BONUS_COL  = (255, 200, 0)
DANGER_COL = (255, 50, 50)

DIFFICULTY = {
    "Easy":   {"speed": 7,  "label": "1 · EASY",   "color": (80, 255, 120)},
    "Normal": {"speed": 12, "label": "2 · NORMAL",  "color": (255, 200, 0)},
    "Hard":   {"speed": 18, "label": "3 · HARD",    "color": (255, 60, 80)},
}

class Direction(Enum):
    UP    = (0, -1)
    DOWN  = (0,  1)
    LEFT  = (-1, 0)
    RIGHT = (1,  0)

OPPOSITES = {
    Direction.UP:    Direction.DOWN,
    Direction.DOWN:  Direction.UP,
    Direction.LEFT:  Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
}


# ─────────────────────────────────────────────
# PARTICLE SYSTEM
# ─────────────────────────────────────────────

@dataclass
class Particle:
    x:      float
    y:      float
    vx:     float
    vy:     float
    life:   float        # 0..1
    decay:  float
    color:  Tuple
    size:   float
    glow:   bool = False

class ParticleSystem:
    def __init__(self):
        self.particles: List[Particle] = []

    def emit(self, x, y, color, count=12, speed=3.0, size=4, glow=False):
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            spd   = random.uniform(speed * 0.4, speed)
            self.particles.append(Particle(
                x=x, y=y,
                vx=math.cos(angle) * spd,
                vy=math.sin(angle) * spd,
                life=1.0,
                decay=random.uniform(0.03, 0.06),
                color=color,
                size=random.uniform(size * 0.5, size),
                glow=glow,
            ))

    def update(self):
        alive = []
        for p in self.particles:
            p.x   += p.vx
            p.y   += p.vy
            p.vx  *= 0.92
            p.vy  *= 0.92
            p.vy  += 0.08   # gravity
            p.life -= p.decay
            if p.life > 0:
                alive.append(p)
        self.particles = alive

    def draw(self, surface):
        for p in self.particles:
            alpha = p.life
            r, g, b = p.color
            col = (
                int(r * alpha),
                int(g * alpha),
                int(b * alpha),
            )
            size = max(1, int(p.size * p.life))
            pygame.draw.circle(surface, col, (int(p.x), int(p.y)), size)


# ─────────────────────────────────────────────
# FOOD
# ─────────────────────────────────────────────

class FoodType(Enum):
    NORMAL = "normal"
    BONUS  = "bonus"   # double points, spawns briefly

@dataclass
class Food:
    gx:      int
    gy:      int
    ftype:   FoodType = FoodType.NORMAL
    pulse:   float    = 0.0
    ttl:     Optional[float] = None   # seconds remaining for bonus food

    def world_center(self) -> Tuple[int, int]:
        return (GRID_X + self.gx * CELL + CELL // 2,
                GRID_Y + self.gy * CELL + CELL // 2)


# ─────────────────────────────────────────────
# SNAKE
# ─────────────────────────────────────────────

class Snake:
    def __init__(self):
        cx, cy = GRID_COLS // 2, GRID_ROWS // 2
        self.body: List[Tuple[int, int]] = [
            (cx, cy), (cx - 1, cy), (cx - 2, cy)
        ]
        self.direction = Direction.RIGHT
        self.next_dir  = Direction.RIGHT
        self.alive     = True
        self.grew      = False

    @property
    def head(self) -> Tuple[int, int]:
        return self.body[0]

    def queue_direction(self, new_dir: Direction):
        if new_dir != OPPOSITES[self.direction]:
            self.next_dir = new_dir

    def step(self) -> Tuple[int, int]:
        """Advance one grid step. Returns the old tail position."""
        self.direction = self.next_dir
        dx, dy = self.direction.value
        hx, hy = self.head
        new_head = (hx + dx, hy + dy)

        old_tail = self.body[-1]
        self.body.insert(0, new_head)

        if self.grew:
            self.grew = False
        else:
            self.body.pop()

        return old_tail

    def check_collision(self) -> bool:
        hx, hy = self.head
        if not (0 <= hx < GRID_COLS and 0 <= hy < GRID_ROWS):
            return True
        if self.head in self.body[1:]:
            return True
        return False

    def grow(self):
        self.grew = True


# ─────────────────────────────────────────────
# SCORE / HIGH SCORE
# ─────────────────────────────────────────────

class ScoreManager:
    COMBO_WINDOW = 3.0   # seconds between eats to keep combo alive

    def __init__(self):
        self.score     = 0
        self.combo     = 1
        self.last_eat  = -999.0
        self.high      = self._load()
        self.flash_val = 0
        self.flash_t   = 0.0

    def eat(self, now: float, bonus=False):
        if now - self.last_eat < self.COMBO_WINDOW:
            self.combo = min(self.combo + 1, 8)
        else:
            self.combo = 1
        self.last_eat = now
        pts = (20 if bonus else 10) * self.combo
        self.score += pts
        self.flash_val = pts
        self.flash_t   = 1.0
        if self.score > self.high:
            self.high = self.score
            self._save()
        return pts

    def update(self, dt):
        self.flash_t = max(0.0, self.flash_t - dt)
        
    def _get_performance_label(self, score):
        if score < 50:
            return "beginner"
        elif score < 150:
            return "intermediate"
        else:
            return "advanced"

    def _load(self) -> int:
        if os.path.exists(HIGHSCORE_FILE):
            try:
                with open(HIGHSCORE_FILE) as f:
                    data = json.load(f)
                    return data.get("highscore", 0)
            except Exception:
                pass
        return 0

    def _save(self):
        try:
            data = {
                "player_id": "local_user",
                "highscore": self.high,
                "metadata": {
                    "last_updated": datetime.datetime.now().isoformat(),
                    "game": "snake"
                },
                "performance": {
                    "level": self._get_performance_label(self.high)
                },
                "history": [
                    {
                        "score": self.high,
                        "label": self._get_performance_label(self.high)
                    }
                ]
            }
            with open(HIGHSCORE_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except Exception:
            pass


# ─────────────────────────────────────────────
# RENDERER
# ─────────────────────────────────────────────

class Renderer:
    def __init__(self, surface: pygame.Surface, fonts):
        self.surf  = surface
        self.fonts = fonts

    def draw_grid(self):
        for gx in range(GRID_COLS + 1):
            x = GRID_X + gx * CELL
            pygame.draw.line(self.surf, GRID_LINE, (x, GRID_Y), (x, GRID_Y + GRID_ROWS * CELL))
        for gy in range(GRID_ROWS + 1):
            y = GRID_Y + gy * CELL
            pygame.draw.line(self.surf, GRID_LINE, (GRID_X, y), (GRID_X + GRID_COLS * CELL, y))

    def draw_border(self, difficulty_color):
        rect = pygame.Rect(GRID_X - 2, GRID_Y - 2,
                           GRID_COLS * CELL + 4, GRID_ROWS * CELL + 4)
        pygame.draw.rect(self.surf, difficulty_color, rect, 2, border_radius=4)

    def cell_rect(self, gx, gy, inset=1) -> pygame.Rect:
        return pygame.Rect(
            GRID_X + gx * CELL + inset,
            GRID_Y + gy * CELL + inset,
            CELL - inset * 2,
            CELL - inset * 2,
        )

    def draw_snake(self, snake: Snake, tick: float):
        n = len(snake.body)
        for i, (gx, gy) in enumerate(snake.body):
            t = i / max(n - 1, 1)
            # Colour gradient head → tail
            r = int(SNAKE_HEAD[0] * (1 - t) + SNAKE_TAIL[0] * t)
            g = int(SNAKE_HEAD[1] * (1 - t) + SNAKE_TAIL[1] * t)
            b = int(SNAKE_HEAD[2] * (1 - t) + SNAKE_TAIL[2] * t)
            col = (r, g, b)

            rect = self.cell_rect(gx, gy, inset=1 if i > 0 else 0)
            radius = 4 if i > 0 else 6
            pygame.draw.rect(self.surf, col, rect, border_radius=radius)

            # Head details: eyes
            if i == 0:
                dx, dy = snake.direction.value
                cx = GRID_X + gx * CELL + CELL // 2
                cy = GRID_Y + gy * CELL + CELL // 2
                # Eye offsets perpendicular to direction
                perp = (-dy, dx)
                for sign in (-1, 1):
                    ex = cx + perp[0] * 4 + dx * 3
                    ey = cy + perp[1] * 4 + dy * 3
                    pygame.draw.circle(self.surf, BG, (ex, ey), 2)

    def draw_food(self, food: Food, tick: float):
        cx, cy = food.world_center()
        pulse  = math.sin(tick * 4) * 2
        if food.ftype == FoodType.BONUS:
            col  = BONUS_COL
            size = int(7 + pulse)
            # spinning star
            for i in range(5):
                angle = math.radians(i * 72 + tick * 120)
                px = cx + math.cos(angle) * size
                py = cy + math.sin(angle) * size
                pygame.draw.circle(self.surf, col, (int(px), int(py)), 3)
            pygame.draw.circle(self.surf, col, (cx, cy), 5)
        else:
            col  = FOOD_COL
            size = int(5 + pulse)
            pygame.draw.circle(self.surf, col, (cx, cy), size)
            # inner shine
            pygame.draw.circle(self.surf, WHITE, (cx - 2, cy - 2), 2)

    def draw_hud(self, score_mgr: ScoreManager, snake: Snake,
                 difficulty: str, paused: bool, tick: float):
        # Top panel
        pygame.draw.rect(self.surf, PANEL_BG, (0, 0, WINDOW_W, GRID_Y - 8), border_radius=0)

        # Score
        sc_surf = self.fonts["lg"].render(f"{score_mgr.score:06d}", True, ACCENT)
        self.surf.blit(sc_surf, (GRID_X, 12))

        # Label
        lbl = self.fonts["sm"].render("SCORE", True, GRAY)
        self.surf.blit(lbl, (GRID_X, 8))

        # High score
        hi_lbl = self.fonts["sm"].render("BEST", True, GRAY)
        hi_val = self.fonts["md"].render(f"{score_mgr.high:06d}", True, GOLD)
        self.surf.blit(hi_lbl, (GRID_X + 160, 8))
        self.surf.blit(hi_val, (GRID_X + 160, 24))

        # Combo
        if score_mgr.combo > 1:
            pulse = abs(math.sin(tick * 6))
            col   = (
                int(ACCENT2[0] * pulse + ACCENT[0] * (1 - pulse)),
                int(ACCENT2[1] * pulse + ACCENT[1] * (1 - pulse)),
                int(ACCENT2[2] * pulse + ACCENT[2] * (1 - pulse)),
            )
            combo_surf = self.fonts["md"].render(f"x{score_mgr.combo} COMBO", True, col)
            self.surf.blit(combo_surf, (GRID_X + 320, 20))

        # Length
        len_lbl = self.fonts["sm"].render("LENGTH", True, GRAY)
        len_val = self.fonts["md"].render(str(len(snake.body)), True, WHITE)
        right_x = GRID_X + GRID_COLS * CELL
        self.surf.blit(len_lbl, (right_x - 120, 8))
        self.surf.blit(len_val, (right_x - 90, 24))

        # Difficulty badge
        dcfg = DIFFICULTY[difficulty]
        d_surf = self.fonts["sm"].render(dcfg["label"], True, dcfg["color"])
        self.surf.blit(d_surf, (right_x - d_surf.get_width(), 8))

        # PAUSED overlay
        if paused:
            overlay = pygame.Surface((GRID_COLS * CELL, GRID_ROWS * CELL), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            self.surf.blit(overlay, (GRID_X, GRID_Y))
            p_surf = self.fonts["xl"].render("PAUSED", True, WHITE)
            self.surf.blit(p_surf, (
                GRID_X + (GRID_COLS * CELL - p_surf.get_width()) // 2,
                GRID_Y + (GRID_ROWS * CELL - p_surf.get_height()) // 2,
            ))

    def draw_score_popup(self, score_mgr: ScoreManager, foods: List[Food]):
        if score_mgr.flash_t > 0:
            alpha = score_mgr.flash_t
            # Find food-ish position (last eaten)
            cx = GRID_X + GRID_COLS * CELL // 2
            cy = GRID_Y + GRID_ROWS * CELL // 4
            rise = int((1 - score_mgr.flash_t) * 40)
            col  = tuple(int(c * alpha) for c in GOLD)
            pop  = self.fonts["lg"].render(f"+{score_mgr.flash_val}", True, col)
            self.surf.blit(pop, (cx, cy - rise))

    def draw_game_over(self, score_mgr: ScoreManager, difficulty: str, tick: float):
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.surf.blit(overlay, (0, 0))

        cx = WINDOW_W // 2

        pulse = abs(math.sin(tick * 3))
        col   = (
            int(DANGER_COL[0]),
            int(DANGER_COL[1] * (0.4 + 0.6 * pulse)),
            int(DANGER_COL[2] * (0.4 + 0.6 * pulse)),
        )
        go   = self.fonts["xl"].render("GAME OVER", True, col)
        self.surf.blit(go,  (cx - go.get_width() // 2,  200))

        sc   = self.fonts["lg"].render(f"SCORE  {score_mgr.score:06d}", True, WHITE)
        hi   = self.fonts["md"].render(f"BEST   {score_mgr.high:06d}", True, GOLD)
        diff_col = DIFFICULTY[difficulty]["color"]
        dif  = self.fonts["sm"].render(f"Difficulty: {difficulty}", True, diff_col)
        rst  = self.fonts["md"].render("[R] RESTART     [ESC] QUIT", True, GRAY)

        self.surf.blit(sc,  (cx - sc.get_width() // 2,  290))
        self.surf.blit(hi,  (cx - hi.get_width() // 2,  340))
        self.surf.blit(dif, (cx - dif.get_width() // 2, 380))
        self.surf.blit(rst, (cx - rst.get_width() // 2, 450))

    def draw_title_screen(self, tick: float, high: int):
        cx = WINDOW_W // 2

        # Animated title
        pulse = math.sin(tick * 2) * 8
        t1 = self.fonts["xl"].render("SNAKE", True, ACCENT)
        self.surf.blit(t1, (cx - t1.get_width() // 2, 160 + int(pulse)))

        sub = self.fonts["md"].render("A Classic. Reimagined.", True, GRAY)
        self.surf.blit(sub, (cx - sub.get_width() // 2, 240))

        keys = [
            "Arrow keys / WASD  —  Move",
            "P  —  Pause",
            "1 / 2 / 3  —  Difficulty",
        ]
        for i, k in enumerate(keys):
            s = self.fonts["sm"].render(k, True, WHITE)
            self.surf.blit(s, (cx - s.get_width() // 2, 310 + i * 28))

        # Best score
        if high:
            hi_s = self.fonts["sm"].render(f"Your best:  {high}", True, GOLD)
            self.surf.blit(hi_s, (cx - hi_s.get_width() // 2, 410))

        start = self.fonts["md"].render("Press  SPACE  to start", True,
                                        ACCENT if int(tick * 2) % 2 == 0 else GRAY)
        self.surf.blit(start, (cx - start.get_width() // 2, 480))


# ─────────────────────────────────────────────
# GAME
# ─────────────────────────────────────────────

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("SNAKE")
        self.screen  = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.clock   = pygame.time.Clock()
        self.fonts   = self._load_fonts()
        self.renderer = Renderer(self.screen, self.fonts)
        self.psys    = ParticleSystem()

        self.difficulty  = "Normal"
        self.state       = "title"   # title | playing | paused | dead
        self.score_mgr   = ScoreManager()

        self.snake: Optional[Snake]   = None
        self.foods: List[Food]        = []
        self.move_timer  = 0.0
        self.tick        = 0.0
        self.bonus_timer = 0.0

    # ── Font loading ──────────────────────────

    def _load_fonts(self):
        sizes = {"xl": 52, "lg": 36, "md": 24, "sm": 16}
        fonts = {}
        for key, size in sizes.items():
            try:
                fonts[key] = pygame.font.SysFont("consolas,couriernew,monospace", size, bold=True)
            except Exception:
                fonts[key] = pygame.font.Font(None, size)
        return fonts

    # ── Session setup ─────────────────────────

    def new_game(self):
        self.snake      = Snake()
        self.foods      = []
        self.score_mgr  = ScoreManager()
        self.score_mgr.high = ScoreManager()._load()
        self.move_timer = 0.0
        self.bonus_timer = 0.0
        self.psys       = ParticleSystem()
        self._spawn_food()
        self.state = "playing"

    def _spawn_food(self, ftype=FoodType.NORMAL):
        occupied = set(self.snake.body) | {(f.gx, f.gy) for f in self.foods}
        attempts = 0
        while attempts < 200:
            gx = random.randint(0, GRID_COLS - 1)
            gy = random.randint(0, GRID_ROWS - 1)
            if (gx, gy) not in occupied:
                ttl = 6.0 if ftype == FoodType.BONUS else None
                self.foods.append(Food(gx=gx, gy=gy, ftype=ftype, ttl=ttl))
                return
            attempts += 1

    # ── Main loop ─────────────────────────────

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            self.tick += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self._handle_event(event)

            self._update(dt)
            self._draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    # ── Input handling ────────────────────────

    def _handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        key = event.key

        # Quit
        if key == pygame.K_ESCAPE:
            pygame.quit(); sys.exit()

        # Difficulty
        if key == pygame.K_1:
            self.difficulty = "Easy"
        elif key == pygame.K_2:
            self.difficulty = "Normal"
        elif key == pygame.K_3:
            self.difficulty = "Hard"

        # Title → start
        if self.state == "title" and key == pygame.K_SPACE:
            self.new_game(); return

        # Dead → restart
        if self.state == "dead" and key == pygame.K_r:
            self.new_game(); return

        # Pause toggle
        if self.state in ("playing", "paused") and key == pygame.K_p:
            self.state = "paused" if self.state == "playing" else "playing"
            return

        # Snake direction
        if self.state == "playing" and self.snake:
            DIR_MAP = {
                pygame.K_UP:    Direction.UP,
                pygame.K_w:     Direction.UP,
                pygame.K_DOWN:  Direction.DOWN,
                pygame.K_s:     Direction.DOWN,
                pygame.K_LEFT:  Direction.LEFT,
                pygame.K_a:     Direction.LEFT,
                pygame.K_RIGHT: Direction.RIGHT,
                pygame.K_d:     Direction.RIGHT,
            }
            if key in DIR_MAP:
                self.snake.queue_direction(DIR_MAP[key])

    # ── Update ────────────────────────────────

    def _update(self, dt: float):
        self.psys.update()

        if self.state != "playing":
            return

        self.score_mgr.update(dt)

        # Bonus food timer
        self.bonus_timer -= dt
        if self.bonus_timer <= 0:
            # Chance to spawn bonus food if none exists
            if not any(f.ftype == FoodType.BONUS for f in self.foods):
                self._spawn_food(FoodType.BONUS)
            self.bonus_timer = random.uniform(12, 20)

        # Tick bonus food TTL
        expired = []
        for food in self.foods:
            if food.ftype == FoodType.BONUS and food.ttl is not None:
                food.ttl -= dt
                if food.ttl <= 0:
                    expired.append(food)
        for e in expired:
            self.foods.remove(e)

        # Move timer
        speed = DIFFICULTY[self.difficulty]["speed"]
        move_interval = 1.0 / speed
        self.move_timer += dt
        if self.move_timer >= move_interval:
            self.move_timer -= move_interval
            self._step()

    def _step(self):
        old_tail = self.snake.step()

        # Collision check
        if self.snake.check_collision():
            self._die()
            return

        # Eat food?
        hx, hy = self.snake.head
        for food in list(self.foods):
            if (food.gx, food.gy) == (hx, hy):
                self.snake.grow()
                pts = self.score_mgr.eat(
                    self.tick, bonus=(food.ftype == FoodType.BONUS)
                )
                cx, cy = food.world_center()
                col = BONUS_COL if food.ftype == FoodType.BONUS else FOOD_COL
                self.psys.emit(cx, cy, col, count=20, speed=4, size=5, glow=True)
                self.foods.remove(food)

                # Ensure there's always at least one normal food
                if not any(f.ftype == FoodType.NORMAL for f in self.foods):
                    self._spawn_food(FoodType.NORMAL)
                break

    def _die(self):
        self.state = "dead"
        # Death particles along snake
        for gx, gy in self.snake.body:
            cx = GRID_X + gx * CELL + CELL // 2
            cy = GRID_Y + gy * CELL + CELL // 2
            self.psys.emit(cx, cy, DANGER_COL, count=6, speed=3)

    # ── Draw ──────────────────────────────────

    def _draw(self):
        self.screen.fill(BG)

        if self.state == "title":
            self._draw_title()
            return

        self.renderer.draw_grid()
        diff_col = DIFFICULTY[self.difficulty]["color"]
        self.renderer.draw_border(diff_col)

        # Foods
        for food in self.foods:
            self.renderer.draw_food(food, self.tick)

        # Snake
        if self.snake:
            self.renderer.draw_snake(self.snake, self.tick)

        # Particles
        self.psys.draw(self.screen)

        # HUD
        self.renderer.draw_hud(
            self.score_mgr, self.snake,
            self.difficulty,
            paused=(self.state == "paused"),
            tick=self.tick
        )
        self.renderer.draw_score_popup(self.score_mgr, self.foods)

        # Game over overlay
        if self.state == "dead":
            self.renderer.draw_game_over(self.score_mgr, self.difficulty, self.tick)

    def _draw_title(self):
        # Animated background dots
        for i in range(30):
            seed = i * 137.5
            x = (seed * 23) % WINDOW_W
            y = (seed * 47 + self.tick * (10 + i % 5)) % WINDOW_H
            alpha = abs(math.sin(self.tick * 0.5 + i))
            r, g, b = ACCENT
            col = (int(r * alpha * 0.3), int(g * alpha * 0.3), int(b * alpha * 0.3))
            pygame.draw.circle(self.screen, col, (int(x), int(y)), 2)

        self.psys.draw(self.screen)
        self.renderer.draw_title_screen(self.tick, self.score_mgr.high)


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    Game().run()
