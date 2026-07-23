import pygame as pg

from ..core.settings import *
from .uipanel import UIPanel

class PanelResourses(UIPanel):
    def __init__(self, x, y, W, H, color, type, color_edge, width, player, scene):
        super().__init__(x, y, W, H, color, type, color_edge, width)
        self.imageOrig = self.image.copy()
        self.update(player, scene)

    def update(self, player, scene):
        self.image =  self.imageOrig.copy()
        text_turns = font48.render(f"Turn: {scene.cnt_rounds//QNT_PLAYERS + 1}", True, team_to_color[player.team])
        self.image.blit(text_turns, (self.width*2, self.width*2))
        