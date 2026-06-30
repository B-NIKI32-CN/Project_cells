import pygame as pg

from .scene import Scene
from ..scenes.main_menu_scene import MainMenuScene

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.scene = MainMenuScene(self)

    def set_scene(self, new_scene: type[Scene]):        
        self.scene = new_scene(self)

    def loop(self):
        pass
