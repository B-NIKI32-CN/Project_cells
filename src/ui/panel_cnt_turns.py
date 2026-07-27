import pygame as pg

from ..core.settings import *
from .uipanel import UIPanel

class PanelCntTurns(UIPanel):
    def __init__(self, x, y, W, H, color, type, color_edge, width, player, cnt_rounds, qnt_players):
        super().__init__(x, y, W, H, color, type, color_edge, width)
        self.imageOrig = self.image.copy()
        self.update(player, cnt_rounds, qnt_players)

    def update(self, player, cnt_rounds, qnt_players):
        self.image =  self.imageOrig.copy()
        text_turns = font48.render(f"Turn: {cnt_rounds//qnt_players + 1}", True, team_to_color[player.team])
        self.image.blit(text_turns, (self.width*2, self.width*2))
        