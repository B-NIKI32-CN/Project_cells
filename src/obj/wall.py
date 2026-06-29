import pygame as pg
from ..core.settings import *


class Wall(pg.sprite.DirtySprite):
    W = len_cell
    H = W
    size = (W, H)
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
        self.rect = self.image.get_rect()
        self.rect.center = self.x + self.W/2, self.y + self.H/2
        self.image.fill((0, 0, 0))
        self.place = [self.x // self.W, self.y // self.H]

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

    def change_misty(self, misty):
        if misty != self.misty:
            self.misty = misty
            self.dirty = 1