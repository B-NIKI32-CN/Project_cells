import pygame as pg

from ..core.scene import Scene
from .. import ui
from ..core.settings import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..core.game import Game
        

class MainMenuScene(Scene):    
    text_on_button = font48.render("Proceed", True, (0, 0, 0))
    
    def __init__(self, game: Game):
        super().__init__(game)
        self.background = pg.Surface((SW, SH))
        self.background.fill((255,255,255))
        self.button_start_game = ui.uipanel.UIPanel(SW/2 - SW/16, SH/2 - SH/16, SW/8, SH/8, (0,255,255), 1, (255,128,0), 5)
        self.button_start_game.image.blit(self.text_on_button, (self.button_start_game.size[0]/16, self.button_start_game.size[1]/3))
        self.all_buttons = pg.sprite.LayeredDirty()
        self.all_buttons.add(self.button_start_game)

    def handle_events(self, all_events: list[pg.event.Event]):
        for event in all_events:
            if event.type == pg.K_ESCAPE:
                self.game.stop()

            elif event.type == pg.MOUSEBUTTONDOWN:
                if self.button_start_game.rect.collidepoint(event.pos):    
                    
                    from .game_scene import GameScene
                    self.game.set_scene(GameScene)
                    self.all_buttons.empty()

    def update(self):
        pass

    def display(self, screen: pg.Surface):
        self.all_buttons.draw(screen, self.background)
