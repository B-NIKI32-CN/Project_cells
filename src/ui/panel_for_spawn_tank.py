import pygame as pg
from ..core.settings import *
from .uipanel import UIPanel

class PanelForSpawnTank(UIPanel):
    def __init__(self, x, y, W, H, color, type, color_edge, width):
        super().__init__(x, y, W, H, color, type, color_edge, width)
        self.imageOrig = self.image.copy()

        self.tank = None

    def draw_tank(self, image):
        if image is None:
            self.image = self.imageOrig.copy()
        else:
            self.image.blit(image.image, (self.W*0.25, self.H*0.25))