import random


def mostra_testo(screen, t, f, c, x, y):
    s = f.render(t, True, c)
    screen.blit(s, s.get_rect(center=(x, y)))

def rand_bool():
    return True if random.randint(0,1) else False