import pygame as pg
# from settings import *

class Button(pg.sprite.Sprite):
    def __init__(self, x, y, W, H, color):
        pg.sprite.Sprite.__init__(self)
        self.W = W
        self.H = H
        self.size = (W, H)
        self.x = x
        self.y = y
        self.image = pg.Surface(self.size, pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = self.x, self.y
        self.image.fill(color)