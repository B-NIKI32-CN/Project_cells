import pygame as pg

from .core.settings import *
from .core.scene_manager import SceneManager
from .scenes.main_menu_scene import MainMenuScene
from .net.our_net import SoftServer, SoftClient





# # 127.0.0.1:1234 10.26.229.242:1234 10.26.229.165:1234




pg.init()

screen = pg.display.set_mode((SW, SH), vsync=1) # pg.display.set_mode((SW, SH), pg.FULLSCREEN, vsync=1)

pg.display.set_caption("Project_cells")

clock = pg.time.Clock()


scene_manager = SceneManager(MainMenuScene, None, debug=False)

# if isinstance(net_module, SoftServer):
#     scene_manager.max_qnt_players = max_qnt_players


while scene_manager.is_running():

    scene_manager.handle_events(pg.event.get())
    scene_manager.update()
    scene_manager.display(screen)

    clock.tick(FPS)
    pg.display.flip()

pg.quit()
