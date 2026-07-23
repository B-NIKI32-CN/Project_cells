from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import pygame as pg
    from .scene_manager import SceneManager


class Scene:
    def __init__(self, scene_manager: SceneManager):
        self.scene_manager = scene_manager

    def handle_events(self, _all_events: list[pg.event.Event]):
        pass

    def update(self):
        pass

    def display(self, _screen: pg.Surface):
        pass
    