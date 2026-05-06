import pygame


class Constants:
    def __init__(self):
        self.physics = Constants.Physics()
        self.colors = Constants.Colors()
        self.fonts = Constants.Fonts()

    class Physics:
        @property
        def fric(self):
            return 0.82

    # --- COLORI KABUL DECADUTA ---💔💔
    class Colors:
        @property
        def ORANGE(self):
            return 255, 165, 0

        @property
        def SKIN(self):
            return 255, 200, 150

        @property
        def ASPHALT(self):
            return 60, 60, 65

        @property
        def SAND_DUST(self):
            return 190, 175, 150

        @property
        def RUBBLE_COLORS(self):
            return [(120, 110, 100), (90, 85, 80), (150, 140, 120), (50, 45, 40)]

        @property
        def BUILDING_COLORS(self):
            return [(160, 150, 130), (130, 120, 110), (180, 170, 150)]

        @property
        def WHITE(self):
            return 255, 255, 255

        @property
        def BLACK(self):
            return 15, 15, 15

        @property
        def RED(self):
            return 200, 30, 30

        @property
        def DARK_RED(self):
            return 100, 0, 0

        @property
        def BLUE(self):
            return 50, 90, 180

        @property
        def GREEN(self):
            return 30, 200, 30

        @property
        def GOLD(self):
            return 255, 215, 0

        @property
        def PURPLE(self):
            return 148, 0, 211

        @property
        def LIME(self):
            return 50, 205, 50

        @property
        def YELLOW(self):
            return 255, 255, 0

    class Fonts:
        @property
        def title(self):
            return pygame.font.SysFont("impact", 80)

        @property
        def menu(self):
            return pygame.font.SysFont("impact", 50)

        @property
        def hud(self):
            return pygame.font.SysFont("monospace", 20, True)

        @property
        def wheel(self):
            return pygame.font.SysFont("impact", 28)
