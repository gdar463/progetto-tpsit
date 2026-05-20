from enum import Enum

from src import constants

C = constants.Constants()


# nome = danno
class Weapons(Enum):
    PISTOLA = 45
    MITRAGLIETTA = 25
    PUGNI = 30

    def to_string(self) -> str:
        if self == Weapons.PISTOLA:
            return "Pistola"
        if self == Weapons.MITRAGLIETTA:
            return "Mitraglietta"
        if self == Weapons.PUGNI:
            return "Pugni"
        return ""


# nome = effetto
class AirDrops(Enum):
    MEDKIT = 60

    def to_string(self) -> str:
        if self == AirDrops.MEDKIT:
            return "Medkit"


type Color = tuple[int, int, int] | tuple[int, int, int, int]


# nome = n_nemici, min i_lvl, mult i_lvl
class Difficulty(Enum):
    FACILE = 4, 1, 1
    MEDIO = 9, 5, 2
    ESTREMO = 15, 8, 3

    def for_menu(self) -> tuple[str, Color, Color]:
        if self == Difficulty.FACILE:
            return "Facile", C.colors.GREEN, C.colors.LIME
        if self == Difficulty.MEDIO:
            return "Medio", C.colors.YELLOW, C.colors.ORANGE
        if self == Difficulty.ESTREMO:
            return "Estremo", C.colors.RED, C.colors.DARK_RED
        return "", C.colors.GOLD, C.colors.GOLD
