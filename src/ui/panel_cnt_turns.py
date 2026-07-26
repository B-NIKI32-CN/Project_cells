import pygame as pg

from ..core.settings import *
from .uipanel import UIPanel

class PanelCntTurns(UIPanel):
    def __init__(self, x, y, W, H, color, type, color_edge, width, player, cnt_rounds):
        super().__init__(x, y, W, H, color, type, color_edge, width)
        self.imageOrig = self.image.copy()
        self.update(player, cnt_rounds)

    def update(self, player, cnt_rounds):
        self.image =  self.imageOrig.copy()
        text_turns = font48.render(f"Turn: {cnt_rounds//DEFAULT_MAX_QNT_PLAYERS + 1}", True, team_to_color[player.team])
        self.image.blit(text_turns, (self.width*2, self.width*2))
        