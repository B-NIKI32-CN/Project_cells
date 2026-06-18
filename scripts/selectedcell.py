import pygame as pg
from settings import *

class Selectedcell(pg.sprite.DirtySprite):
    W = len_cell
    H = W
    size = (W, H)
    width = cell_width - 2
    def __init__(self, x, y):
        pg.sprite.DirtySprite.__init__(self)
        self.dirty = 1
        self.visible = True
        self.layer = 5
        self.x = x
        self.y = y
        self.image = pg.Surface(self.size, pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = self.x + self.W/2, self.y + self.H/2
        pg.draw.line(self.image, select_color, (0,0), (self.W, 0), width=self.width+2)
        pg.draw.line(self.image, select_color, (0 + self.W, 0), (self.W, self.H),
                     width=self.width+4)
        pg.draw.line(self.image, select_color, (self.W, self.H), (0, self.H),
                     width=self.width+4)
        pg.draw.line(self.image, select_color, (0, self.H), (0, 0), width=self.width+2)

    def change_color(self, color):
        pg.draw.line(self.image, color, (0, 0), (self.W, 0), width=self.width + 2)
        pg.draw.line(self.image, color, (0 + self.W, 0), (self.W, self.H),
                     width=self.width + 4)
        pg.draw.line(self.image, color, (self.W, self.H), (0, self.H),
                     width=self.width + 4)
        pg.draw.line(self.image, color, (0, self.H), (0, 0), width=self.width + 2)

    def go_to(self, x, y):
        self.x = x
        self.y = y
        self.rect.center = self.x + self.W / 2, self.y + self.H / 2