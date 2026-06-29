import pygame as pg
from ..core.settings import *


class Surface(pg.sprite.DirtySprite):
    def __init__(self, x, y, W, H, color, type, color_edge, width):
        pg.sprite.DirtySprite.__init__(self)
        self.dirty = 1
        self.visible = True
        self.layer = LAYER_UI
        self.W = W
        self.H = H
        self.size = (W, H)
        self.width = width
        self.color = color
        self.color_edge = color_edge
        self.x = x
        self.y = y
        self.image = pg.Surface(self.size, pg.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x + self.W*0.5, self.y + self.H*0.5)
        # self.rect.center = (self.x, self.y)
        if type == 1:
            pg.draw.line(self.image, self.color_edge, (0, 0), (self.W, 0), width=self.width*2)
            pg.draw.line(self.image, self.color_edge, (0 + self.W, 0), (self.W, self.H),
                         width=self.width*2 + 2)
            pg.draw.line(self.image, self.color_edge, (self.W, self.H), (0, self.H),
                         width=self.width*2 + 2)
            pg.draw.line(self.image, self.color_edge, (0, self.H), (0, 0), width=self.width*2)

    def draw(self, surface): # рисовка по центру
        surface.blit(self.image, (self.x-self.W/2, self.y-self.H/2))

    def draw_by_edge(self, surface):
        surface.blit(self.image, (self.x, self.y))