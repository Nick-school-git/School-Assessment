"""
Sonic the Hedgehog - Python / Pygame
Controls:
  Arrow Left / Right  - move
  Z or Space          - jump (hold for higher jump)
  Down Arrow          - roll
  Escape              - quit
"""

import pygame
import math
import sys
import random

pygame.init()

# ── Constants ──────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 800, 500
FPS   = 60
TILE  = 32

# Physics
GRAVITY       = 0.4
MAX_FALL      = 16
GROUND_ACCEL  = 0.46
GROUND_FRIC   = 0.85
AIR_ACCEL     = 0.3
TOP_SPEED     = 6.0
JUMP_FORCE    = -10.5
JUMP_RELEASE  = -4.0
ROLL_DECEL    = 0.98

# Colors
SKY_TOP        = (100, 180, 255)
SKY_BTM        = (170, 220, 255)
GROUND_COLOR   = (60,  140,  60)
DIRT_COLOR     = (120,  80,  40)
RING_GOLD      = (255, 200,   0)
RING_SHINE     = (255, 240, 120)
PLATFORM_TOP   = (80,  160,  80)
PLATFORM_SIDE  = (50,  110,  50)
SPIKE_COLOR    = (180, 180, 190)
SPRING_RED     = (220,  60,  60)
SPRING_DARK    = (180,  30,  30)

Vec2 = pygame.math.Vector2


# ── Drawing helpers ────────────────────────────────────────────────────────────
def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_sonic(surface, pos: Vec2, facing: int, rolling: bool, frame: int, flash: bool):
    if flash:
        return
    x, y = int(pos.x), int(pos.y)

    BLUE  = (0, 100, 220)
    SKIN  = (255, 210, 140)
    RED   = (220, 40,  40)
    WHITE = (255, 255, 255)
    BLACK = (0,   0,   0)
    NOSE  = (220, 140,  80)

    if rolling:
        r = 14
        pygame.draw.circle(surface, BLUE,  (x, y - r), r)
        pygame.draw.circle(surface, SKIN,  (x, y - r), 5)
        return

    swing = int(math.sin(frame * 0.35) * 6)

    # Legs
    pygame.draw.rect(surface, BLUE,  (x - 6,              y - 14, 5, 8))
    pygame.draw.rect(surface, WHITE, (x - 7,              y -  6, 6, 4))
    pygame.draw.rect(surface, RED,   (x - 9 + swing,      y -  2, 10, 5))

    pygame.draw.rect(surface, BLUE,  (x + 1,              y - 14, 5, 8))
    pygame.draw.rect(surface, WHITE, (x + 1,              y -  6, 6, 4))
    pygame.draw.rect(surface, RED,   (x - 1 - swing,      y -  2, 10, 5))

    # Body
    pygame.draw.ellipse(surface, BLUE, (x - 12, y - 30, 24, 20))
    pygame.draw.ellipse(surface, SKIN, (x -  7, y - 26, 14, 12))

    # Head
    hx = x + facing * 2
    pygame.draw.circle(surface, BLUE, (hx, y - 38), 14)
    pygame.draw.ellipse(surface, SKIN, (hx + facing * 4 - 7, y - 36, 14, 10))
    pygame.draw.circle(surface, NOSE, (hx + facing * 9, y - 36), 3)

    # Eye
    pygame.draw.circle(surface, WHITE, (hx + facing * 5, y - 42), 5)
    pygame.draw.circle(surface, BLACK, (hx + facing * 7, y - 42), 3)

    # Spikes
    for i, (ox, oy) in enumerate([(-2, -50), (-8, -48), (-14, -44)]):
        pts = [
            (hx + ox,      y + oy),
            (hx + ox - 12, y + oy + 4 + i * 4),
            (hx + ox - 4,  y + oy + 12 + i * 6),
        ]
        pygame.draw.polygon(surface, BLUE, pts)

    # Arms
    arm = int(math.sin(frame * 0.35 + math.pi) * 5)
    pygame.draw.line(surface, BLUE, (x - 8, y - 26), (x - 14 + arm * facing, y - 18), 4)
    pygame.draw.line(surface, BLUE, (x + 8, y - 26), (x + 14 - arm * facing, y - 18), 4)


def draw_ring(surface, pos: Vec2, tick: int):
    x, y = int(pos.x), int(pos.y)
    squish = abs(math.cos(math.radians(tick * 3 % 360)))
    rx = max(1, int(10 * squish))
    pygame.draw.ellipse(surface, RING_GOLD,  (x - rx, y - 10, rx * 2, 20))
    pygame.draw.ellipse(surface, RING_SHINE, (x - rx, y - 10, rx * 2, 20), 2)


def draw_spike(surface, r: pygame.Rect):
    cx = r.centerx
    pygame.draw.polygon(surface, SPIKE_COLOR,    [(cx, r.top), (r.left, r.bottom), (r.right, r.bottom)])
    pygame.draw.polygon(surface, (220, 220, 230), [(cx, r.top), (cx, r.centery),   (r.right, r.bottom)])


def draw_spring(surface, r: pygame.Rect):
    pygame.draw.rect(surface, SPRING_DARK, (r.left, r.bottom - 6, r.width, 6))
    for i in range(3):
        cy = r.top + i * (r.height // 3)
        pygame.draw.rect(surface, SPRING_RED, (r.left + 2, cy, r.width - 4, 4))
    pygame.draw.rect(surface, SPRING_RED, (r.left, r.top, r.width, 4))


def draw_background(surface, cam_x: float):
    for y in range(SCREEN_H):
        pygame.draw.line(surface, lerp_color(SKY_TOP, SKY_BTM, y / SCREEN_H), (0, y), (SCREEN_W, y))
    for cx, cy in [(100, 60), (300, 40), (520, 70), (700, 50), (150, 100), (450, 90)]:
        px = int((cx - cam_x * 0.2) % (SCREEN_W + 200)) - 100
        for dx, dy, r in [(0, 0, 22), (-24, 8, 16), (24, 8, 16), (-12, -10, 14), (12, -10, 14)]:
            pygame.draw.circle(surface, (255, 255, 255), (px + dx, cy + dy), r)


# ── Level ──────────────────────────────────────────────────────────────────────
def build_level():
    tiles = []
    # Main ground
    for i in range(100):
        if i not in range(20, 23):   # gap
            tiles.append((pygame.Rect(i * TILE, SCREEN_H - TILE, TILE, TILE * 3), 'ground'))

    # Platforms
    for x1, x2, py in [
        ( 8, 12, SCREEN_H - 100), (14, 17, SCREEN_H - 140),
        (25, 28, SCREEN_H - 100), (30, 34, SCREEN_H - 130),
        (37, 41, SCREEN_H - 100), (44, 48, SCREEN_H - 150),
        (52, 55, SCREEN_H - 110), (58, 62, SCREEN_H - 140),
        (65, 69, SCREEN_H - 100), (72, 75, SCREEN_H - 160),
    ]:
        for i in range(x1, x2):
            tiles.append((pygame.Rect(i * TILE, py, TILE, TILE), 'platform'))

    # Spikes
    for i in [5, 6, 19, 42, 43, 63]:
        tiles.append((pygame.Rect(i * TILE + 4, SCREEN_H - TILE - 20, TILE - 8, 20), 'spike'))

    # Springs
    for i in [10, 27, 55]:
        tiles.append((pygame.Rect(i * TILE + 4, SCREEN_H - TILE - 24, TILE - 8, 24), 'spring'))

    return tiles


def build_rings():
    rings = []
    for xs, y in [
        (range( 8, 20), SCREEN_H - TILE - 28),
        (range(25, 30), SCREEN_H - 140  - 28),
        (range(37, 42), SCREEN_H - TILE - 28),
        (range(52, 56), SCREEN_H - 110  - 28),
        (range(65, 70), SCREEN_H - TILE - 28),
    ]:
        for xi in xs:
            rings.append(Vec2(xi * TILE + TILE // 2, y))
    return rings


# ── Particle ───────────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, pos: Vec2, vel: Vec2, color, life: int, size: int = 4):
        self.pos   = Vec2(pos)
        self.vel   = Vec2(vel)
        self.color = color
        self.life  = life
        self.max   = life
        self.size  = size

    def update(self):
        self.vel.y += 0.15
        self.pos   += self.vel
        self.life  -= 1

    def draw(self, surface, cam_x: float):
        a = self.life / self.max
        r = max(1, int(self.size * a))
        c = tuple(int(v * a) for v in self.color)
        pygame.draw.circle(surface, c, (int(self.pos.x - cam_x), int(self.pos.y)), r)


# ── Player ─────────────────────────────────────────────────────────────────────
class Sonic:
    W = 20
    H = 38
    RH = 28  # roll height

    def __init__(self, pos: Vec2):
        self.pos         = Vec2(pos)
        self.vel         = Vec2(0, 0)
        self.on_ground   = False
        self.facing      = 1
        self.rolling     = False
        self.frame       = 0
        self.rings       = 0
        self.lives       = 3
        self.score       = 0
        self.invincible  = 0
        self.jump_held   = False
        self.dead        = False
        self.spring_cd   = 0

    @property
    def height(self):
        return self.RH if self.rolling else self.H

    def rect(self):
        return pygame.Rect(int(self.pos.x) - self.W // 2,
                           int(self.pos.y) - self.height,
                           self.W, self.height)

    def handle_input(self, keys, events):
        jump_pressed = any(e.type == pygame.KEYDOWN and e.key in (pygame.K_z, pygame.K_SPACE)
                           for e in events)

        accel = GROUND_ACCEL if self.on_ground else AIR_ACCEL
        if keys[pygame.K_LEFT]:
            self.vel.x -= accel
            self.facing = -1
        if keys[pygame.K_RIGHT]:
            self.vel.x += accel
            self.facing = 1

        if abs(self.vel.x) > TOP_SPEED:
            self.vel.x = math.copysign(TOP_SPEED, self.vel.x)

        if jump_pressed and self.on_ground:
            self.vel.y     = JUMP_FORCE
            self.on_ground = False
            self.rolling   = False
            self.jump_held = True

        jump_down = keys[pygame.K_z] or keys[pygame.K_SPACE]
        if not jump_down and self.jump_held and self.vel.y < JUMP_RELEASE:
            self.vel.y     = JUMP_RELEASE
            self.jump_held = False

        if keys[pygame.K_DOWN] and self.on_ground and abs(self.vel.x) > 0.5:
            self.rolling = True
        elif self.on_ground and not keys[pygame.K_DOWN]:
            self.rolling = False

    def update(self, tiles, particles):
        if self.dead:
            self.vel.y += GRAVITY
            self.pos   += self.vel
            return

        self.vel.y = min(self.vel.y + GRAVITY, MAX_FALL)

        if self.on_ground:
            self.vel.x *= ROLL_DECEL if self.rolling else GROUND_FRIC
            if abs(self.vel.x) < 0.1:
                self.vel.x = 0

        self.pos       += self.vel
        self.on_ground  = False
        self.spring_cd  = max(0, self.spring_cd - 1)

        r = self.rect()
        for tile_rect, kind in tiles:
            if not r.colliderect(tile_rect):
                continue

            if kind == 'spike':
                self.take_hit(particles)
                continue

            if kind == 'spring' and self.spring_cd == 0:
                self.vel.y    = -16
                self.spring_cd = 20
                continue

            if kind in ('ground', 'platform'):
                ox = min(r.right, tile_rect.right)  - max(r.left,  tile_rect.left)
                oy = min(r.bottom, tile_rect.bottom) - max(r.top,   tile_rect.top)
                if ox < oy:
                    self.pos.x += ox if r.centerx > tile_rect.centerx else -ox
                    self.vel.x  = 0
                else:
                    if r.centery < tile_rect.centery:
                        self.pos.y    = tile_rect.top
                        self.vel.y    = 0
                        self.on_ground = True
                    else:
                        self.pos.y = tile_rect.bottom + self.height
                        if self.vel.y < 0:
                            self.vel.y = 0
                r = self.rect()

        if self.pos.y > SCREEN_H + 100:
            self.lose_life()

        if abs(self.vel.x) > 0.5 or not self.on_ground:
            self.frame += 1
        else:
            self.frame = 0

        self.invincible = max(0, self.invincible - 1)

    def take_hit(self, particles):
        if self.invincible > 0:
            return
        if self.rings > 0:
            for _ in range(min(self.rings, 20)):
                a = random.uniform(0, math.tau)
                s = random.uniform(2, 6)
                particles.append(Particle(
                    Vec2(self.pos),
                    Vec2(math.cos(a) * s, math.sin(a) * s - 3),
                    RING_GOLD, 60, 6
                ))
            self.rings = 0
        else:
            self.lose_life()
        self.invincible = 120
        self.vel = Vec2(-self.facing * 4, -8)

    def lose_life(self):
        self.lives -= 1
        self.dead   = True
        self.vel    = Vec2(-self.facing * 2, -10)

    def respawn(self, start: Vec2):
        self.pos        = Vec2(start)
        self.vel        = Vec2(0, 0)
        self.on_ground  = False
        self.rolling    = False
        self.frame      = 0
        self.invincible = 120
        self.dead       = False

    def draw(self, surface, cam_x: float):
        flash = self.invincible > 0 and (self.invincible // 4) % 2 == 0
        draw_sonic(surface,
                   Vec2(self.pos.x - cam_x, self.pos.y),
                   self.facing, self.rolling, self.frame, flash)


# ── HUD ────────────────────────────────────────────────────────────────────────
def draw_hud(surface, player: Sonic, time_s: float):
    big = pygame.font.SysFont("monospace", 22, bold=True)
    sm  = pygame.font.SysFont("monospace", 16)

    def txt(s, color, x, y, f=sm):
        surface.blit(f.render(s, True, (0, 0, 0)), (x + 1, y + 1))
        surface.blit(f.render(s, True, color),      (x,     y))

    txt(f"SCORE  {player.score:07d}",                (255, 255, 255), 16, 12, big)
    txt(f"RINGS  {player.rings:03d}",                (255, 210,   0), 16, 38)
    txt(f"LIVES  {player.lives}",                    (255, 255, 255), 16, 58)
    txt(f"TIME  {int(time_s//60):02d}:{int(time_s%60):02d}", (255, 255, 255), SCREEN_W - 180, 12, big)
    txt(f"SPD  {abs(player.vel.x):.1f}",             (180, 220, 255), SCREEN_W - 180, 38)


def draw_overlay_text(surface, lines, y0=160):
    big = pygame.font.SysFont("monospace", 32, bold=True)
    sm  = pygame.font.SysFont("monospace", 18)
    for i, (s, is_big) in enumerate(lines):
        f  = big if is_big else sm
        tx = f.render(s, True, (255, 255, 255))
        sh = f.render(s, True, (0, 0, 0))
        x  = SCREEN_W // 2 - tx.get_width() // 2
        y  = y0 + i * 44
        surface.blit(sh, (x + 2, y + 2))
        surface.blit(tx, (x,     y))


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Sonic the Hedgehog")
    clock  = pygame.time.Clock()

    START     = Vec2(64, SCREEN_H - TILE - 1)
    LEVEL_END = 90 * TILE

    def new_game_state():
        return {
            "tiles":     build_level(),
            "rings":     build_rings(),
            "collected": set(),
            "particles": [],
            "cam_x":     0.0,
            "time_s":    0.0,
            "tick":      0,
        }

    player = Sonic(Vec2(START))
    gs     = new_game_state()
    state  = "play"
    dead_timer = 0

    running = True
    while running:
        clock.tick(FPS)
        events = pygame.event.get()

        for e in events:
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                if state in ("dead", "gameover", "win"):
                    if e.key in (pygame.K_z, pygame.K_SPACE, pygame.K_RETURN):
                        if state == "dead" and player.lives > 0:
                            gs = new_game_state()
                            player.respawn(Vec2(START))
                            state = "play"
                        else:
                            player = Sonic(Vec2(START))
                            gs     = new_game_state()
                            state  = "play"

        # ── Update ────────────────────────────────────────────────────────────
        if state == "play":
            gs["time_s"] += 1 / FPS
            gs["tick"]   += 1

            keys = pygame.key.get_pressed()
            player.handle_input(keys, events)
            player.update(gs["tiles"], gs["particles"])

            # Smooth camera
            target = player.pos.x - SCREEN_W * 0.35
            gs["cam_x"] += (target - gs["cam_x"]) * 0.12
            gs["cam_x"]  = max(0.0, gs["cam_x"])

            # Ring collection
            pr = player.rect()
            for i, rp in enumerate(gs["rings"]):
                if i in gs["collected"]:
                    continue
                if (Vec2(rp.x - gs["cam_x"], rp.y) - Vec2(pr.centerx, pr.centery)).length() < 20:
                    gs["collected"].add(i)
                    player.rings += 1
                    player.score += 10
                    for _ in range(8):
                        a = random.uniform(0, math.tau)
                        v = Vec2(math.cos(a) * 2, math.sin(a) * 2 - 1)
                        gs["particles"].append(Particle(Vec2(rp), v, RING_GOLD, 30, 4))

            for p in gs["particles"]:
                p.update()
            gs["particles"] = [p for p in gs["particles"] if p.life > 0]

            if player.dead:
                state      = "dead"
                dead_timer = 120

            if player.pos.x >= LEVEL_END:
                player.score += max(0, int((500 - gs["time_s"]) * 100))
                state = "win"

        elif state == "dead":
            dead_timer -= 1
            player.vel.y += GRAVITY
            player.pos   += player.vel
            if dead_timer <= 0 and player.lives <= 0:
                state = "gameover"

        # ── Draw ──────────────────────────────────────────────────────────────
        cam = gs["cam_x"]
        draw_background(screen, cam)

        # Tiles
        for tile_rect, kind in gs["tiles"]:
            tx = tile_rect.x - int(cam)
            if not (-TILE * 2 < tx < SCREEN_W + TILE * 2):
                continue
            dr = pygame.Rect(tx, tile_rect.y, tile_rect.width, tile_rect.height)
            if kind == 'ground':
                pygame.draw.rect(screen, DIRT_COLOR,    dr)
                pygame.draw.rect(screen, GROUND_COLOR,  (dr.x, dr.y, dr.w, 6))
            elif kind == 'platform':
                pygame.draw.rect(screen, PLATFORM_TOP,  dr)
                pygame.draw.rect(screen, PLATFORM_SIDE, (dr.x, dr.bottom - 5, dr.w, 5))
            elif kind == 'spike':
                draw_spike(screen, dr)
            elif kind == 'spring':
                draw_spring(screen, dr)

        # Finish flag
        fx = int(LEVEL_END - cam)
        if -20 < fx < SCREEN_W + 20:
            pygame.draw.rect(screen, (255, 255, 255), (fx, SCREEN_H - TILE * 6, 4, TILE * 5))
            pygame.draw.polygon(screen, (220, 30, 30), [
                (fx + 4, SCREEN_H - TILE * 6),
                (fx + 4, SCREEN_H - TILE * 4),
                (fx + 40, SCREEN_H - TILE * 5),
            ])

        # Rings
        for i, rp in enumerate(gs["rings"]):
            if i in gs["collected"]:
                continue
            rx = int(rp.x - cam)
            if -20 < rx < SCREEN_W + 20:
                draw_ring(screen, Vec2(rx, rp.y), gs["tick"])

        # Particles
        for p in gs["particles"]:
            p.draw(screen, cam)

        # Player
        show = not (state == "dead" and dead_timer % 6 < 3 and dead_timer < 60)
        if show:
            player.draw(screen, cam)

        draw_hud(screen, player, gs["time_s"])

        # Overlays
        if state in ("dead", "gameover", "win"):
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 130))
            screen.blit(ov, (0, 0))

        if state == "dead" and dead_timer <= 0:
            draw_overlay_text(screen, [
                ("YOU DIED!", True),
                (f"Lives: {player.lives}", False),
                ("Press Z / SPACE to continue", False),
            ])
        elif state == "gameover":
            draw_overlay_text(screen, [
                ("GAME  OVER", True),
                (f"Score: {player.score}", False),
                ("Press Z / SPACE to restart", False),
            ])
        elif state == "win":
            draw_overlay_text(screen, [
                ("GOAL !!", True),
                (f"Score: {player.score:,}", False),
                (f"Rings: {player.rings}", False),
                ("Press Z / SPACE to play again", False),
            ])

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
