import pygame as pg

from .core.game import Game
from .core.settings import *
from .scenes.main_menu_scene import MainMenuScene

pg.init()
# pg.mixer.init()

# screen = pg.display.set_mode((SW, SH), pg.FULLSCREEN, vsync=1)
screen = pg.display.set_mode((SW, SH), vsync=1)

clock = pg.time.Clock()
old_fps_val = 0 # для вывода FPS

game = Game(screen, MainMenuScene)

while game.is_running():
    game.iteration()
    
    # if clock.get_fps() != old_fps_val:
    #     old_fps_val = clock.get_fps()
    #     print(old_fps_val)

    clock.tick(FPS)
    pg.display.flip()

pg.quit()
