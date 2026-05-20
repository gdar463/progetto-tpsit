# --- EFFETTI E AMBIENTE ---
import math
import random

import pygame

from src.entity import Entity
from src import constants

C = constants.Constants()


class Debris:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.points = []
        num_points = random.randint(3, 5)
        radius = random.uniform(2, 12)
        for i in range(num_points):
            ang = (math.pi * 2 / num_points) * i + random.uniform(-0.5, 0.5)
            self.points.append((math.cos(ang) * radius, math.sin(ang) * radius))
        self.color = random.choice(C.colors.RUBBLE_COLORS)

    def draw(self, w, h, surface, camera):
        cx, cy = camera.apply((self.x, self.y))
        if 0 < cx < w and 0 < cy < h:
            screen_points = [(cx + px, cy + py) for px, py in self.points]
            pygame.draw.polygon(surface, self.color, screen_points)


class Particle:
    timer: int

    def update(self, dt):
        pass

    def draw(self, surface, camera):
        pass


class Blood(Particle):
    def __init__(self, x, y):
        self.x, self.y = x, y
        ang = random.uniform(0, math.pi * 2)
        vel = random.uniform(1, 5)
        self.vx, self.vy = math.cos(ang) * vel, math.sin(ang) * vel
        self.timer = random.randint(20, 60)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.9
        self.vy *= 0.9
        self.timer -= 1 * dt

    def draw(self, surface, camera):
        if self.timer > 0:
            cx, cy = camera.apply((self.x, self.y))
            pygame.draw.rect(
                surface,
                C.colors.DARK_RED,
                (cx, cy, random.randint(2, 5), random.randint(2, 5)),
            )


class Attack(Particle):
    def __init__(self, e: Entity):
        self.x, self.y = e.x, e.y
        self.timer = random.randint(20, 60)

    def update(self, dt):
        self.timer -= 2 * dt

    def draw(self, surface, camera):
        if self.timer > 0:
            cx, cy = camera.apply((self.x, self.y))
            pygame.draw.line(
                surface, C.colors.ATTACK, (cx - 13, cy + 13), (cx - 5, cy + 5), 3
            )
            pygame.draw.line(
                surface, C.colors.ATTACK, (cx - 13, cy - 13), (cx - 5, cy - 5), 3
            )
            pygame.draw.line(
                surface, C.colors.ATTACK, (cx + 5, cy - 5), (cx + 13, cy - 13), 3
            )
            pygame.draw.line(
                surface, C.colors.ATTACK, (cx + 5, cy + 5), (cx + 13, cy + 13), 3
            )


class Proiettile:
    def __init__(self, x, y, angle, owner):
        self.x, self.y = x, y
        self.vx, self.vy = math.cos(angle) * 35, math.sin(angle) * 35
        self.owner = owner
        self.active = True

    def update(self, dt, muri):
        self.x += self.vx * dt
        self.y += self.vy * dt
        r = pygame.Rect(self.x - 2, self.y - 2, 4, 4)
        for m in muri:
            if m.rect.colliderect(r):
                self.active = False
                break

    def draw(self, surface, camera):
        cx, cy = camera.apply((self.x, self.y))
        pygame.draw.circle(
            surface,
            C.colors.GOLD if self.owner == "p" else C.colors.RED,
            (int(cx), int(cy)),
            3,
        )
