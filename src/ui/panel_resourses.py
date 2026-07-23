import pygame as pg

from ..core.settings import *
from .uipanel import UIPanel

class PanelResourses(UIPanel):
    def __init__(self, x, y, W, H, color, type, color_edge, width, player):
        super().__init__(x, y, W, H, color, type, color_edge, width)
        self.imageOrig = self.image.copy()
        self.update(player)

    def update(self, player):
        self.image =  self.imageOrig.copy()
        text_resouces = font48.render(f"Resources : {player.resources}", True, team_to_color[player.team])
        text_exp = font48.render(f"Сapture : {player.exp}", True, team_to_color[player.team])
        self.image.blit(text_resouces, (self.width*3, self.width*3))
        self.image.blit(text_exp, (self.width*3, self.width*3 + SH*3/80))