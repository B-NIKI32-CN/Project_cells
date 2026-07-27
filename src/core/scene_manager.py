from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pygame import Surface
    from pygame.event import Event
    from ..net.our_net import SoftServer, SoftClient
    from .scene import Scene





class SceneManager:
    def __init__(self, scene: type[Scene], net_module: None | SoftServer | SoftClient = None, debug=False):

        self.net_module = net_module

        self.local_player_id = 0

        self.debug = False
        if self.net_module is not None:
            self.net_module.debug = self.debug

        self.running = True
        self.max_qnt_players = 0

        self.cur_map_id = 0

        self.set_scene(scene)

    def handle_events(self, events: list[Event]):
        self.scene.handle_events(events)

    def update(self):
        self.scene.update()

    def display(self, screen: Surface):
        self.scene.display(screen)


    def set_scene(self, new_scene: type[Scene]):        
        self.scene = new_scene(self)

    def is_running(self):
        return self.running
    
    def stop(self):
        self.running = False
    
