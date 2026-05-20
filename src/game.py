import math
import platform
import random
import sys

import pygame

import constants
import fonts as resizable_fonts
from effects import Proiettile, Blood, Particle, Attack
from entity import Entity
from enums import Weapons, AirDrops, Difficulty
from map import Drop, gen_objs
from player import Player
from utils import mostra_testo, rand_bool

C = constants.Constants()

# --- SETUP ---
pygame.init()
icon = pygame.image.load("../assets/icon.ico")
if platform.system() == "Windows":
    import ctypes

    myappid = "gdar463.progetto.1.0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
pygame.display.set_icon(icon)
pygame.display.set_caption("ASH R6: Fuga da Kabul EFN")
info = pygame.display.Info()
# WIDTH, HEIGHT = info.current_w // 4 * 3, info.current_h // 4 * 3
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
clock = pygame.time.Clock()

PIXELS_PER_METER = 40


# --- SISTEMA TELECAMERA ---
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width, self.height = width, height

    def apply(self, entity):
        if isinstance(entity, pygame.Rect):
            return entity.move(self.camera.topleft)
        return entity[0] + self.camera.x, entity[1] + self.camera.y

    def update(self, target_x, target_y):
        x = -target_x + WIDTH // 2
        y = -target_y + HEIGHT // 2
        x = min(0, max(-(self.width - WIDTH), x))
        y = min(0, max(-(self.height - HEIGHT), y))
        self.camera = pygame.Rect(x, y, self.width, self.height)


def disegna_menu_radiale(surface, mx, my, inv_armi, arma_attiva):
    cx, cy = WIDTH // 2, HEIGHT // 2

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    pygame.draw.circle(surface, (30, 30, 30), (cx, cy), 200)
    pygame.draw.circle(surface, C.colors.GOLD, (cx, cy), 200, 4)

    dx, dy = mx - cx, my - cy
    mouse_angle = (math.degrees(math.atan2(dy, dx)) + 360) % 360

    num_items = len(inv_armi)
    slice_angle = 360 / max(1, num_items)

    selezione = -1
    for i, arma in enumerate(inv_armi):
        start_ang = (i * slice_angle - slice_angle / 2) % 360
        end_ang = (i * slice_angle + slice_angle / 2) % 360

        is_hover = False
        if start_ang < end_ang:
            if start_ang <= mouse_angle <= end_ang:
                is_hover = True
        else:
            if mouse_angle >= start_ang or mouse_angle <= end_ang:
                is_hover = True

        if is_hover and math.hypot(dx, dy) > 30:
            selezione = i

        text_ang = math.radians(i * slice_angle)
        tx = cx + math.cos(text_ang) * 120
        ty = cy + math.sin(text_ang) * 120

        col = C.colors.GOLD if is_hover else C.colors.WHITE
        if arma == arma_attiva and not is_hover:
            col = C.colors.GREEN
        mostra_testo(screen, arma.name.upper(), C.fonts.wheel, col, tx, ty)

    return inv_armi[selezione] if selezione != -1 else arma_attiva


def sfondo():
    screen.fill(C.colors.BLACK)
    # Sfondo griglia tematico
    for i in range(0, WIDTH, 50):
        pygame.draw.line(screen, (30, 25, 25), (i, 0), (i, HEIGHT))
    for i in range(0, HEIGHT, 50):
        pygame.draw.line(screen, (30, 25, 25), (0, i), (WIDTH, i))


# --- MENU PRINCIPALI ---
def menu_principale():
    sel = 0
    opzioni = ["INIZIA FUGA", "ESCI"]
    while True:
        sfondo()

        mostra_testo(
            screen,
            "ASH R6: FUGA DA KABUL",
            C.fonts.title,
            C.colors.RED,
            WIDTH // 2,
            HEIGHT // 3,
        )
        mostra_testo(
            screen,
            "Premi SHIFT per Correre, CTRL per Ripararti, TAB per le Armi",
            C.fonts.hud,
            C.colors.GOLD,
            WIDTH // 2,
            HEIGHT // 3 + 60,
        )

        for i, opt in enumerate(opzioni):
            col = C.colors.GOLD if i == sel else C.colors.WHITE
            mostra_testo(
                screen, opt, C.fonts.menu, col, WIDTH // 2, HEIGHT // 2 + 50 + i * 80
            )

        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return None
            if e.type == pygame.KEYDOWN:
                if e.key in [pygame.K_UP, pygame.K_w]:
                    sel = (sel - 1) % len(opzioni)
                if e.key in [pygame.K_DOWN, pygame.K_s]:
                    sel = (sel + 1) % len(opzioni)
                if e.key == pygame.K_RETURN:
                    return sel
                if e.key == pygame.K_ESCAPE:
                    return None


def menu_livelli():
    sel = 0
    livelli = [
        Difficulty.FACILE,
        Difficulty.FACILE,
        Difficulty.FACILE,
        Difficulty.FACILE,
        Difficulty.MEDIO,
        Difficulty.MEDIO,
        Difficulty.MEDIO,
        Difficulty.ESTREMO,
        Difficulty.ESTREMO,
        Difficulty.ESTREMO,
    ]
    while True:
        sfondo()

        mostra_testo(
            screen,
            "MAPPA TATTICA - SCEGLI ZONA",
            C.fonts.title,
            C.colors.WHITE,
            WIDTH // 2,
            80,
        )

        for i, l in enumerate(livelli):
            x, y = WIDTH // 2 - 450 + (i % 5) * 220, 250 + (i // 5) * 200
            diff = l.for_menu()

            rect = pygame.Rect(x - 100, y - 80, 200, 160)
            pygame.draw.rect(
                screen, C.colors.GOLD if i == sel else (40, 40, 40), rect, 0, 10
            )
            pygame.draw.rect(screen, C.colors.WHITE, rect, 3, 10)

            mostra_testo(
                screen,
                f"LIVELLO {i + 1}",
                C.fonts.menu,
                C.colors.WHITE if i != sel else C.colors.BLACK,
                x,
                y - 20,
            )
            mostra_testo(
                screen,
                f"{diff[0]}",
                C.fonts.hud,
                diff[1] if i != sel else diff[2],
                x,
                y + 30,
            )

        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return -1, None
            if e.type == pygame.KEYDOWN:
                if e.key in [pygame.K_RIGHT, pygame.K_d]:
                    sel = (sel + 1) % len(livelli)
                if e.key in [pygame.K_LEFT, pygame.K_a]:
                    sel = (sel - 1) % len(livelli)
                if e.key in [pygame.K_DOWN, pygame.K_s] and sel < 5:
                    sel += 5
                if e.key in [pygame.K_UP, pygame.K_w] and sel >= 5:
                    sel -= 5
                if e.key == pygame.K_RETURN:
                    return sel + 1, livelli[sel]
                if e.key == pygame.K_ESCAPE:
                    return -1, None


# --- MOTORE GIOCO ---
# noinspection PyPep8Naming
def esegui_gioco(n_lvl, diff: Difficulty):
    metri = 50
    WORLD_W = WORLD_H = metri * PIXELS_PER_METER
    camera = Camera(WORLD_W, WORLD_H)

    giocatore = Player(WORLD_W // 2, WORLD_H // 2)
    inv: list[Weapons] = [Weapons.PUGNI, Weapons.PISTOLA, Weapons.MITRAGLIETTA]
    munizioni = {Weapons.PISTOLA: 1000, Weapons.MITRAGLIETTA: 1000}

    nemici = []
    n_nemici = diff.value[0] + (diff.value[1] - n_lvl) * diff.value[2]
    for _ in range(n_nemici):
        x = random.randint(0, WORLD_W // 2 - C.SPAWN_RADIUS)
        if rand_bool():  # inverte pos
            x = WORLD_W - x

        y = random.randint(0, WORLD_H // 2 - C.SPAWN_RADIUS)
        if rand_bool():
            y = WORLD_H - y

        n = Entity(x, y)
        n.arma = random.choice([Weapons.PISTOLA, Weapons.MITRAGLIETTA])
        n.last_shot = random.randint(0, 1000)
        nemici.append(n)

    proiettili: list[Proiettile] = []
    airdrops: list[Drop] = []
    particelle: list[Particle] = []
    particelle_dopo: list[Particle] = []
    last_drop = pygame.time.get_ticks()
    last_shot_p = 0
    radial_open = False

    muri, detriti = gen_objs(WORLD_W, WORLD_H)

    run = True
    while run:
        now = pygame.time.get_ticks()
        m_x, m_y = pygame.mouse.get_pos()
        m_btn = pygame.mouse.get_pressed()
        keys = pygame.key.get_pressed()
        mods = pygame.key.get_mods()

        dt = clock.tick(60) / 16.66
        if radial_open:
            dt *= 0.01
        elif m_btn[2] and giocatore.arma != Weapons.PUGNI:
            dt *= 0.4

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return None
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return None  # Torna al menu
                if e.key == pygame.K_TAB:
                    radial_open = True

                if e.key in [pygame.K_LCTRL, pygame.K_RCTRL] or (
                    mods & pygame.KMOD_META and not mods & pygame.KMOD_ALT
                ):
                    if giocatore.in_cover:
                        giocatore.in_cover = False
                        giocatore.cover_wall = None
                    else:
                        gr = giocatore.get_rect()
                        gr.inflate_ip(40, 40)
                        for m in muri:
                            if gr.colliderect(m.rect):
                                giocatore.in_cover = True
                                giocatore.cover_wall = m
                                break

                if e.key == pygame.K_e:
                    for a in airdrops:
                        if (
                            a.landed
                            and math.hypot(giocatore.x - a.x, giocatore.y - a.y) < 100
                        ):
                            if a.tipo == AirDrops.MEDKIT:
                                giocatore.hp = min(100, giocatore.hp + a.tipo.value)
                            elif isinstance(a.tipo, Weapons):
                                if a.tipo not in inv:
                                    inv.append(a.tipo)
                                munizioni[a.tipo] += 30
                                giocatore.arma = a.tipo
                            airdrops.remove(a)

            if e.type == pygame.KEYUP:
                if e.key == pygame.K_TAB:
                    radial_open = False

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and not radial_open:
                if giocatore.arma == Weapons.PUGNI and giocatore.punch_ext <= 0:
                    giocatore.punch_ext = 12
                elif (
                    giocatore.arma in [Weapons.PISTOLA, Weapons.MITRAGLIETTA]
                    and munizioni[giocatore.arma] > 0
                ):
                    cooldown = 400 if giocatore.arma == Weapons.PISTOLA else 100
                    if now - last_shot_p > cooldown:
                        spread = (
                            random.uniform(-0.05, 0.05)
                            if giocatore.arma == Weapons.MITRAGLIETTA
                            else 0
                        )
                        proiettili.append(
                            Proiettile(
                                giocatore.x, giocatore.y, giocatore.angle + spread, "p"
                            )
                        )
                        munizioni[giocatore.arma] -= 1
                        last_shot_p = now

        if (
            m_btn[0]
            and giocatore.arma == Weapons.MITRAGLIETTA
            and munizioni[Weapons.MITRAGLIETTA] > 0
            and not radial_open
        ):
            if now - last_shot_p > 100:
                spread = random.uniform(-0.1, 0.1)
                proiettili.append(
                    Proiettile(giocatore.x, giocatore.y, giocatore.angle + spread, "p")
                )
                munizioni[Weapons.MITRAGLIETTA] -= 1
                last_shot_p = now

        if giocatore.punch_ext > 0:
            if int(giocatore.punch_ext) == 8:
                for n in nemici:
                    if math.hypot(giocatore.x - n.x, giocatore.y - n.y) < 80:
                        n.hp -= giocatore.arma.value
                        for _ in range(5):
                            particelle.append(Blood(n.x, n.y))
                        particelle_dopo.append(Attack(n))
            giocatore.punch_ext -= 1 * dt

        ix, iy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            iy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            iy = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            ix = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            ix = 1

        is_sprinting = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

        giocatore.update_physics(dt, (WORLD_W, WORLD_H), muri, ix, iy, is_sprinting)

        if not radial_open:
            c_x, c_y = camera.apply((giocatore.x, giocatore.y))
            giocatore.angle = math.atan2(m_y - c_y, m_x - c_x)

        camera.update(giocatore.x, giocatore.y)

        for n in nemici:
            dist = math.hypot(giocatore.x - n.x, giocatore.y - n.y)
            n.angle = math.atan2(giocatore.y - n.y, giocatore.x - n.x)

            nx, ny = 0, 0
            if 200 < dist < 800:
                nx = math.cos(n.angle)
                ny = math.sin(n.angle)
            elif dist < 150 and n.hp <= 50:
                nx = -math.cos(n.angle)
                ny = -math.sin(n.angle)

            n.update_physics(dt, (WORLD_W, WORLD_H), muri, nx, ny, is_sprinting=False)

            if dist < 600 and now - getattr(n, "last_shot", 0) > (
                300 if n.arma == Weapons.MITRAGLIETTA else 1000
            ):
                proiettili.append(
                    Proiettile(n.x, n.y, n.angle + random.uniform(-0.1, 0.1), "e")
                )
                n.last_shot = now

            if n.hp <= 0:
                nemici.remove(n)

        if len(airdrops) >= 2:
            last_drop += 5000
        if now - last_drop > 15000:
            dx = max(100, min(WORLD_W - 100, giocatore.x + random.randint(-300, 300)))
            dy = max(100, min(WORLD_H - 100, giocatore.y + random.randint(-300, 300)))
            airdrops.append(Drop(dx, dy, now))
            last_drop = now

        for b in proiettili:
            b.update(dt, muri)
            if not b.active or not (0 < b.x < WORLD_W and 0 < b.y < WORLD_H):
                proiettili.remove(b)
                continue

            if b.owner == "p":
                for n in nemici:
                    if math.hypot(b.x - n.x, b.y - n.y) < (n.radius + 5):
                        n.hp -= giocatore.arma.value
                        for _ in range(8):
                            particelle.append(Blood(n.x, n.y))
                        particelle_dopo.append(Attack(n))
                        proiettili.remove(b)
                        break
            else:
                if math.hypot(b.x - giocatore.x, b.y - giocatore.y) < giocatore.radius:
                    danno = 10
                    if giocatore.in_cover:
                        ang_diff = abs(b.vx / 35 - math.cos(giocatore.angle))
                        if ang_diff > 1:
                            danno = 2

                    giocatore.hp -= danno
                    giocatore.last_hit = 0
                    for _ in range(10):
                        particelle.append(Blood(giocatore.x, giocatore.y))
                    proiettili.remove(b)

        for p in particelle:
            p.update(dt)
            if p.timer <= 0:
                particelle.remove(p)
        for p in particelle_dopo:
            p.update(dt)
            if p.timer <= 0:
                particelle_dopo.remove(p)

        screen.fill(C.colors.SAND_DUST)

        for i in range(0, WORLD_W, 400):
            r = camera.apply(pygame.Rect(i - 50, 0, 100, WORLD_H))
            pygame.draw.rect(screen, C.colors.ASPHALT, r)
        for i in range(0, WORLD_H, 400):
            r = camera.apply(pygame.Rect(0, i - 50, WORLD_W, 100))
            pygame.draw.rect(screen, C.colors.ASPHALT, r)

        for d in detriti:
            d.draw(WIDTH, HEIGHT, screen, camera)
        for a in airdrops:
            a.draw(screen, camera, now, giocatore.x, giocatore.y)
        for p in particelle:
            p.draw(screen, camera)
        for m in muri:
            m.draw(WIDTH, HEIGHT, screen, camera)
        for b in proiettili:
            b.draw(screen, camera)

        for n in nemici:
            n.draw_character(screen, camera)

        giocatore.draw_character(screen, camera, m_btn[2])

        for p in particelle_dopo:
            p.draw(screen, camera)

        if radial_open:
            giocatore.arma = disegna_menu_radiale(screen, m_x, m_y, inv, giocatore.arma)

        if not radial_open:
            #                                                           140, 300, 120
            pygame.draw.rect(screen, C.colors.BLACK, (20, HEIGHT - 175, 400, 155), 0, 8)

            pygame.draw.rect(screen, C.colors.RED, (30, HEIGHT - 160, 380, 30), 0, 5)
            if giocatore.hp > 0:
                pygame.draw.rect(
                    screen,
                    C.colors.GREEN,
                    (30, HEIGHT - 160, (giocatore.hp / giocatore.max_hp) * 380, 30),
                    0,
                    5,
                )

            pygame.draw.rect(screen, (50, 50, 50), (30, HEIGHT - 125, 380, 10), 0, 3)
            pygame.draw.rect(
                screen,
                C.colors.WHITE,
                (
                    30,
                    HEIGHT - 125,
                    (giocatore.stamina / giocatore.max_stamina) * 380,
                    10,
                ),
                0,
                3,
            )
            mostra_testo(
                screen,
                f"ARMA: {giocatore.arma.name}",
                resizable_fonts.hud(30),
                C.colors.GOLD,
                225,
                HEIGHT - 90,
            )
            if giocatore.arma != Weapons.PUGNI:
                mostra_testo(
                    screen,
                    f"AMMO: {munizioni[giocatore.arma]}",
                    resizable_fonts.hud(30),
                    C.colors.WHITE,
                    225,
                    HEIGHT - 55,
                )

            if giocatore.in_cover:
                mostra_testo(
                    screen,
                    "IN COPERTURA (DANNO RIDOTTO)",
                    C.fonts.hud,
                    C.colors.PURPLE,
                    WIDTH // 2,
                    HEIGHT - 100,
                )

            mostra_testo(
                screen,
                f"NEMICI: {len(nemici)}",
                resizable_fonts.hud(40),
                C.colors.RED,
                WIDTH // 2,
                40,
            )

        pygame.display.flip()

        if giocatore.hp <= 0:
            return False  # Perso
        if len(nemici) == 0:
            return True  # Vinto
    return None


def screen_vittoria():
    while True:
        sfondo()

        rect = screen.get_rect()
        mostra_testo(
            screen,
            "VITTORIA",
            resizable_fonts.hud(60),
            C.colors.LIME,
            rect.centerx,
            rect.centery,
        )
        mostra_testo(
            screen,
            "Premi Invio per tornare al menu",
            C.fonts.hud,
            C.colors.WHITE,
            rect.centerx,
            rect.bottom - 40,
        )

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return -1
            if e.type == pygame.KEYDOWN:
                if e.key in [pygame.K_RETURN, pygame.K_ESCAPE]:
                    return 0

        pygame.display.flip()


def screen_sconfitta():
    while True:
        sfondo()

        rect = screen.get_rect()
        mostra_testo(
            screen,
            "SCONFITTA",
            resizable_fonts.hud(60),
            C.colors.RED,
            rect.centerx,
            rect.centery,
        )
        mostra_testo(
            screen,
            "Premi Invio per tornare al menu",
            C.fonts.hud,
            C.colors.WHITE,
            rect.centerx,
            rect.bottom - 40,
        )

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return -1
            if e.type == pygame.KEYDOWN:
                if e.key in [pygame.K_RETURN, pygame.K_ESCAPE]:
                    return 0

        pygame.display.flip()


# --- ESECUZIONE PRINCIPALE ---
def main():
    scelta_menu = menu_principale()

    while scelta_menu is not None and scelta_menu != 1:
        lvl, diff = menu_livelli()
        if lvl == -1:  # Premuto ESC per tornare indietro
            break

        esito = esegui_gioco(lvl, diff)
        if esito is None:  # Premuto ESC in game
            break
        elif esito:
            end = screen_vittoria()
            if end == -1:
                break
        elif not esito:
            end = screen_sconfitta()
            if end == -1:
                break

    pygame.quit()
    sys.exit()

    # efn 💔

if __name__ == '__main__':
    main()