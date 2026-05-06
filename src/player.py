from src import entity
from src import constants

C = constants.Constants()


class Player(entity.Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.is_player = True
        self.color = C.colors.BLUE
        self.hp_regen = 2
        self.last_hit = 0.0
        self.regen_after_hit = 300.0  # in frames

    def update_physics(self, dt, muri, input_x, input_y, is_sprinting):
        if is_sprinting and (input_x != 0 or input_y != 0):
            self.stamina = max(0.0, self.stamina - 0.5 * dt)
        elif self.stamina < 200:
            self.stamina += 0.2 * dt

        self.last_hit += dt
        if self.last_hit >= self.regen_after_hit:
            self.hp += self.hp_regen * dt
            self.last_hit -= 60
        super().update_physics(dt, muri, input_x, input_y, is_sprinting)
