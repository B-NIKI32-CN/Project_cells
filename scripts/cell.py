import pygame as pg
from settings import *


class Cell(pg.sprite.Sprite):
    W = len_cell
    H = W
    size = (W, H)
    width = cell_width
    color = (66,66,66)
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.place = [self.x // self.W, self.y // self.H]
        self.image = pg.Surface(self.size, pg.SRCALPHA)
        self.image.fill((255,255,255))
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