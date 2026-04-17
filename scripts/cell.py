import pygame as pg
from settings import *



class Cell(pg.sprite.Sprite):
    W = lencell
    H = W
    size = (W, H)
    width = cellwidth
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pg.Surface(self.size, pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = self.x + self.W/2, self.y + self.H/2
        pg.draw.line(self.image, (0, 0, 0), (0,0), (self.W, 0), width=self.width)
        pg.draw.line(self.image, (0, 0, 0), (self.W, 0), (self.W, self.H),
                     width=self.width+2)
        pg.draw.line(self.image, (0, 0, 0), (self.W, self.H), (0, self.H),
                     width=self.width+2)
        pg.draw.line(self.image, (0, 0, 0), (0, self.H), (0, 0), width=self.width)