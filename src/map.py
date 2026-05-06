import math
import random

import pygame

from src.effects import Debris
from src.enums import Weapons, AirDrops
from src.utils import mostra_testo
from src import constants

C = constants.Constants()


class Muro:
    def __init__(self, x, y, w, h, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color

    def draw(self, w, h, surface, camera):
        screen_rect = camera.apply(self.rect)
        if (
            screen_rect.right < 0
            or screen_rect.left > w
            or screen_rect.bottom < 0
            or screen_rect.top > h
        ):
            return

        ombra_rect = pygame.Rect(
            screen_rect.x + 10, screen_rect.y + 10, screen_rect.w, screen_rect.h
        )
        pygame.draw.rect(surface, (40, 35, 30), ombra_rect)
        pygame.draw.rect(surface, self.color, screen_rect)
        pygame.draw.rect(
            surface,
            (self.color[0] - 40, self.color[1] - 40, self.color[2] - 40),
            screen_rect,
            4,
        )


class Drop:
    def __init__(self, x, y, start_time):
        self.x, self.y = x, y
        self.start_time = start_time
        self.landed = False
        self.tipo = random.choice(
            [Weapons.PISTOLA, AirDrops.MEDKIT, Weapons.MITRAGLIETTA]
        )

    def draw(self, screen, camera, now, p_x, p_y):
        cx, cy = camera.apply((self.x, self.y))
        progresso = (now - self.start_time) / 3000

        if progresso < 1:
            surf_ombra = pygame.Surface((150, 150), pygame.SRCALPHA)
            pygame.draw.circle(
                surf_ombra,
                (0, 0, 0, int(150 * progresso)),
                (75, 75),
                int(60 * (1 - progresso)),
            )
            screen.blit(surf_ombra, (cx - 75, cy - 75))
        else:
            self.landed = True
            cols = {
                Weapons.PISTOLA: C.colors.PURPLE,
                AirDrops.MEDKIT: C.colors.GREEN,
                Weapons.MITRAGLIETTA: C.colors.GOLD,
            }
            rect = pygame.Rect(cx - 20, cy - 20, 40, 40)
            pygame.draw.rect(screen, cols[self.tipo], rect, 0, 5)
            pygame.draw.rect(screen, C.colors.WHITE, rect, 2, 5)

            if math.hypot(self.x - p_x, self.y - p_y) < 100:
                mostra_testo(
                    screen,
                    f"[E] RACCOGLI {self.tipo.to_string()}",
                    C.fonts.hud,
                    C.colors.GOLD,
                    cx,
                    cy - 40,
                )


def gen_objs(w, h):
    muri = []
    detriti = []
    block_size = 400
    for bx in range(100, w - 100, block_size):
        for by in range(100, h - 100, block_size):
            if random.random() < 0.9:
                c_palazzo = random.choice(C.colors.BUILDING_COLORS)
                struttura = random.choice(["U", "L", "PARALLELI"])
                if struttura == "U":
                    muri.append(Muro(bx, by, 200, 30, c_palazzo))
                    muri.append(Muro(bx, by, 30, 200, c_palazzo))
                    muri.append(Muro(bx + 170, by, 30, 200, c_palazzo))
                elif struttura == "L":
                    muri.append(Muro(bx, by, 250, 40, c_palazzo))
                    muri.append(Muro(bx, by, 40, 250, c_palazzo))
                else:
                    muri.append(Muro(bx, by, 200, 40, c_palazzo))
                    muri.append(Muro(bx, by + 160, 200, 40, c_palazzo))

                for _ in range(random.randint(10, 30)):
                    detriti.append(
                        Debris(bx + random.randint(0, 250), by + random.randint(0, 250))
                    )
    return muri, detriti
