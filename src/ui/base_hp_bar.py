import pygame as pg

from ..core.settings import *
from .uipanel import UIPanel

class BaseHpBar(UIPanel):
    def __init__(self, x, y, W, H, color, type, color_edge, width, player):
        super().__init__(x, y, W, H, color, type, color_edge, width)
        self.imageOrig = self.image.copy()
        self.update(player)
    
    def update(self, player):
        self.image = self.imageOrig.copy()
        self.panel_hp_bar = UIPanel(0, 0, self.W - 2*self.width, (self.H - 2*self.width) * (player.hp/base_hp),
                                            (128+(team_to_color[player.team][0]-128)*(player.hp/base_hp),
                                             128+(team_to_color[player.team][1]-128)*(player.hp/base_hp),
                                             128+(team_to_color[player.team][2]-128)*(player.hp/base_hp)), 0, 0, 0)
        self.image.blit(self.panel_hp_bar.image, (self.width, self.width))


