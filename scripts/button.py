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

    def edges(self, color, width):
        pg.draw.line(self.image, color, (0, 0), (self.W, 0), width=width*2)
        pg.draw.line(self.image, color, (0 + self.W, 0), (self.W, self.H),
                     width=width*2 + 2)
        pg.draw.line(self.image, color, (self.W, self.H), (0, self.H),
                     width=width*2 + 2)
        pg.draw.line(self.image, color, (0, self.H), (0, 0), width=width*2)