import pygame as pg
from ..core.settings import *
from .uipanel import UIPanel

class DamagePanel(UIPanel):

    def __init__(self, x, y, W, H, color, type, color_edge, width, time_live, damage, team):
        super().__init__(x, y, W, H, color, type, color_edge, width)

        self.time_live = time_live * FPS
        self.damage = damage
        self.team = team
        self.dam_text = font32.render(f"{int(self.damage)}", True, team_to_color[self.team])
        self.image.blit(self.dam_text, (SW/256,SH/256))

    def update(self):
        self.time_live -= 1
        if self.time_live == 0:
            self.kill()



