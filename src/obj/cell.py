import pygame as pg
from ..core.settings import *


class Cell(pg.sprite.DirtySprite):
    W = len_cell
    H = W
    size = (W, H)
    width = cell_width
    color = (66,66,66)
    def __init__(self, x, y):
        pg.sprite.DirtySprite.__init__(self)
        self.visible = True
        self.dirty = 0
        self.layer = LAYER_GROUND
        self.misty = 1
        self.x = x
        self.y = y
        self.place = [self.x // self.W, self.y // self.H]
        self.image = pg.Surface(self.size, pg.SRCALPHA)
        self.image.fill((128,128,128))
        self.rect = self.image.get_rect()
        self.rect.center = self.x + self.W/2, self.y + self.H/2
        pg.draw.line(self.image, self.color, (0,0), (self.W, 0), width=self.width)
        pg.draw.line(self.image, self.color, (self.W, 0), (self.W, self.H),
                     width=self.width+2)
        pg.draw.line(self.image, self.color, (self.W, self.H), (0, self.H),
                     width=self.width+2)
        pg.draw.line(self.image, self.color, (0, self.H), (0, 0), width=self.width)

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

    def change_misty(self, misty):
        if misty != self.misty:
            self.misty = misty
            self.dirty = 1
            if misty == 1:
                self.image.fill((128, 128, 128))
                pg.draw.line(self.image, self.color, (0, 0), (self.W, 0), width=self.width)
                pg.draw.line(self.image, self.color, (self.W, 0), (self.W, self.H),
                             width=self.width + 2)
                pg.draw.line(self.image, self.color, (self.W, self.H), (0, self.H),
                             width=self.width + 2)
                pg.draw.line(self.image, self.color, (0, self.H), (0, 0), width=self.width)
            else:
                self.image.fill((255, 255, 255))
                pg.draw.line(self.image, self.color, (0, 0), (self.W, 0), width=self.width)
                pg.draw.line(self.image, self.color, (self.W, 0), (self.W, self.H),
                             width=self.width + 2)
                pg.draw.line(self.image, self.color, (self.W, self.H), (0, self.H),
                             width=self.width + 2)
                pg.draw.line(self.image, self.color, (0, self.H), (0, 0), width=self.width)