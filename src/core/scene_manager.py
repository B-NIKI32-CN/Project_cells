from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..net.our_net import SoftServer, SoftClient


import pygame as pg

from .scene import Scene


class SceneManager:
    def __init__(self, screen, scene: type[Scene], net_module: None | SoftServer | SoftClient = None, debug=False):
        
        self.net_module = net_module
        self.local_player_id = 0

        self.debug = False
        if self.net_module is not None:
            self.net_module.debug = self.debug

        self.screen = screen
        self.running = True
        self.set_scene(scene)

    def set_scene(self, new_scene: type[Scene]):        
        self.scene = new_scene(self)

    def iteration(self):
        self.scene.handle_events(pg.event.get())
        self.scene.update()
        self.scene.display(self.screen)

    def stop(self):
        self.running = False

    def is_running(self):
        return self.running
    
