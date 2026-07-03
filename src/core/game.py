import pygame as pg

from .scene import Scene

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.game_running = True

    def set_scene(self, new_scene: type[Scene]):        
        self.scene = new_scene(self)

    def loop(self):
        while self.game_running:
            self.scene.handle_events(pg.event.get())
            self.scene.update()
            self.scene.display(self.screen)

    def stop(self):
        self.game_running = False
