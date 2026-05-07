import pygame as pg
from settings import *

class Surface(pg.sprite.Sprite):
    width = cell_width - 2
    def __init__(self, x, y, W, H, color, type):
        pg.sprite.Sprite.__init__(self)
        self.W = W
        self.H = H
        self.size = (W, H)
        self.x = x
        self.y = y
        self.image = pg.Surface(self.size, pg.SRCALPHA)
        self.image.fill(color)
        if type == 1:
            pg.draw.line(self.image, select_color, (0, 0), (self.W, 0), width=self.width)
            pg.draw.line(self.image, select_color, (0 + self.W, 0), (self.W, self.H),
                         width=self.width + 2)
            pg.draw.line(self.image, select_color, (self.W, self.H), (0, self.H),
                         width=self.width + 2)
            pg.draw.line(self.image, select_color, (0, self.H), (0, 0), width=self.width)

    def draw(self, surface):
        surface.blit(self.image, (self.x-self.W/2, self.y-self.H/2))