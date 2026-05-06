from enum import Enum


# nome = danno
class Weapons(Enum):
    PISTOLA = 45
    MITRAGLIETTA = 25
    PUGNI = 40

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
        return ""
