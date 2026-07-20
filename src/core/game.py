import pygame as pg

from .scene import Scene

class Game:
    def __init__(self, screen, scene: type[Scene]):
        self.onlinlocal_player_id = True
        self.screen = screen
        self._running = True
        self.set_scene(scene)

    def set_scene(self, new_scene: type[Scene]):        
        self.scene = new_scene(self)

    def iteration(self):
        self.scene.handle_events(pg.event.get())
        self.scene.update()
        self.scene.display(self.screen)

    def stop(self):
        self._running = False

    def is_running(self):
        return self._running
    
