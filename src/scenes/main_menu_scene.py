import pygame as pg

from ..core.scene import Scene
from .. import ui
from ..core.settings import font48
from ..core.game import Game
# from .game_scene import GameScene


class MainMenuScene(Scene):    
    text_start = font48.render("Proceed", True, (0, 0, 0))
    all_buttons_menu = pg.sprite.LayeredDirty()
    

    def __init__(self, game: Game):
        super().__init__()
        self.game = game
        self.background = pg.Surface((SW, SH))
        self.background.fill(255,255,255)
        self.b_start = ui.surface.Surface(SW/2 - SW/16, SH/2 - SH/16, SW/8, SH/8, (0,255,255), 1, (255,128,0), 5)
        self.b_start.image.blit(self.text_start, (self.b_start.size[0]/16, self.b_start.size[1]/3))
        self.all_buttons_menu.add(self.b_start)

    def handle_events(self, all_events):
        for event in all_events:
            if event.type == pg.K_ESCAPE:
                running = False

    def update(self):
        if keys_click[pg.K_ESCAPE]:
            running = False

        if mouse_click[MOUSE_LMB] and self.b_start.rect.collidepoint(pg.mouse.get_pos()):
            mouse_click[MOUSE_LMB] = False
            self.game.set_scene(GameScene)
            self.all_buttons_menu.empty()

    def display(self, screen):
        all_buttons_menu.draw(screen, background)
        

# scene = MainMenuScene(game)
# while running:
#         scene.handle_events(all_events)
#         scene.update(scene)
#         scene.display(screen)