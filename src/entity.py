import math

import pygame
from pygame.math import clamp

from src import constants
from src.enums import Weapons

C = constants.Constants()


class Entity:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = 0.0, 0.0
        self.radius = 18
        self.angle = 0
        self.max_hp = 100
        self.hp = self.max_hp
        self.is_player = False
        self.arma: Weapons = Weapons.PUGNI
        self.walk_timer = 0
        self.is_sprinting = False
        self.in_cover = False
        self.cover_wall = None
        self.punch_ext = 0
        self.color = C.colors.RED

    def get_rect(self):
        return pygame.Rect(
            self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2
        )

    def update_physics(self, dt, map_dim, muri, input_x, input_y, is_sprinting, acc=0.8):
        fric = C.physics.FRIC

        if self.in_cover:
            acc = 0.3
            self.is_sprinting = False

        self.vx += input_x * acc * dt
        self.vy += input_y * acc * dt
        self.vx *= fric
        self.vy *= fric

        if abs(self.vx) < 0.1:
            self.vx = 0
        if abs(self.vy) < 0.1:
            self.vy = 0

        speed_mag = math.hypot(self.vx, self.vy)
        if speed_mag > 0.5:
            self.walk_timer += speed_mag * 0.15 * dt
        else:
            self.walk_timer = 0

        self.x = clamp(self.x + self.vx * dt, 0, map_dim[0])
        r_x = self.get_rect()
        for m in muri:
            if r_x.colliderect(m.rect):
                if self.vx > 0:
                    self.x = m.rect.left - self.radius
                elif self.vx < 0:
                    self.x = m.rect.right + self.radius
                self.vx = 0

        self.y = clamp(self.y + self.vy * dt, 0, map_dim[1])
        r_y = self.get_rect()
        for m in muri:
            if r_y.colliderect(m.rect):
                if self.vy > 0:
                    self.y = m.rect.top - self.radius
                elif self.vy < 0:
                    self.y = m.rect.bottom + self.radius
                self.vy = 0

    def draw_character(self, surface, camera, is_aiming=False):
        cx, cy = camera.apply((self.x, self.y))
        size = 100
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cent = size // 2

        swing = math.sin(self.walk_timer) * (12 if self.is_sprinting else 8)
        color = (
            self.color
            if not self.in_cover
            else (self.color[0] // 2, self.color[1] // 2, self.color[2] // 2)
        )

        pygame.draw.rect(
            surf, (30, 30, 30), (cent - 10 + swing, cent - 12, 18, 10), 0, 3
        )
        pygame.draw.rect(
            surf, (30, 30, 30), (cent - 10 - swing, cent + 2, 18, 10), 0, 3
        )

        corpo_rect = pygame.Rect(cent - 15, cent - 14, 30, 28)
        if self.in_cover:
            corpo_rect = pygame.Rect(cent - 10, cent - 14, 20, 28)
        pygame.draw.rect(surf, color, corpo_rect, 0, 6)

        if self.arma in [Weapons.PISTOLA, Weapons.MITRAGLIETTA]:
            if is_aiming or not self.is_player:
                pygame.draw.rect(surf, color, (cent + 5, cent - 16, 25, 8), 0, 4)
                pygame.draw.rect(
                    surf,
                    (40, 40, 40),
                    (
                        cent + 20,
                        cent - 18,
                        25 if self.arma == Weapons.MITRAGLIETTA else 15,
                        10,
                    ),
                )
            else:
                pygame.draw.rect(surf, color, (cent, cent - 16, 20, 8), 0, 4)
                pygame.draw.rect(
                    surf, color, (cent - 10 - swing, cent + 10, 20, 8), 0, 4
                )
        else:
            dx_p = self.punch_ext if self.punch_ext > 0 else -swing
            sx_p = swing
            pygame.draw.rect(surf, color, (cent + dx_p, cent - 16, 20, 8), 0, 4)
            pygame.draw.circle(surf, C.colors.SKIN, (cent + 20 + dx_p, cent - 12), 6)
            pygame.draw.rect(surf, color, (cent + sx_p, cent + 8, 20, 8), 0, 4)
            pygame.draw.circle(surf, C.colors.SKIN, (cent + 20 + sx_p, cent + 12), 6)

        pygame.draw.circle(surf, C.colors.SKIN, (cent, cent), 12)
        pygame.draw.circle(
            surf,
            (40, 20, 10),
            (cent - 2, cent),
            11,
            draw_top_right=True,
            draw_bottom_right=True,
        )

        ruotato = pygame.transform.rotate(surf, -math.degrees(self.angle))
        rect_ruotato = ruotato.get_rect(center=(cx, cy))
        surface.blit(ruotato, rect_ruotato.topleft)
