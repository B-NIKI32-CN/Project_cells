import pygame as pg

from .core.settings import *
from .core.scene_manager import SceneManager
from .scenes.main_menu_scene import MainMenuScene
from .net.our_net import SoftServer, SoftClient


k = input("S/C:")
if k in ['s','S','ы','Ы']:
    net_module = SoftServer()
elif k in ['c','C','с','С']:
    net_module = SoftClient()
else:
    net_module = None

display_name = "tank game: "
if isinstance(net_module, SoftServer):
    display_name += "SERVER"
elif isinstance(net_module, SoftClient):
    display_name += "Client"
else:
    display_name += "offline"


pg.init()

screen = pg.display.set_mode((SW, SH), vsync=1) # pg.display.set_mode((SW, SH), pg.FULLSCREEN, vsync=1)
pg.display.set_caption(display_name)

clock = pg.time.Clock()
old_fps_val = 0 # для вывода FPS

scene_manager = SceneManager(screen, MainMenuScene, net_module)

while scene_manager.is_running():
    scene_manager.iteration()
    
    # if clock.get_fps() != old_fps_val:
    #     old_fps_val = clock.get_fps()
    #     print(old_fps_val)

    clock.tick(FPS)
    pg.display.flip()

pg.quit()
