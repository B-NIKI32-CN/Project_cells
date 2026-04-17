import pygame as pg
from settings import *


class Wall(pg.sprite.Sprite):
    W = lencell
    H = W
    size = (W, H)
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pg.Surface(self.size, pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = self.x + self.W/2, self.y + self.H/2
        self.image.fill((0, 0, 0))

