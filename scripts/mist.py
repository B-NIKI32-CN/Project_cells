import pygame as pg
from settings import *

color = (100, 100, 100)
alpha = 128

class Mist(pg.sprite.DirtySprite): # класс тумана, чисто визуальный эффект (не факт, возможно буду не рисовать танки от него), чтобы понимать где игрок не видим
    W = len_cell
    H = W
    size = (W, H)
    def __init__(self, x, y):
        pg.sprite.DirtySprite.__init__(self)
        self.visible = True
        self.dirty = 1
        self.x = x
        self.y = y
        self.image = pg.Surface(self.size)
        self.rect = self.image.get_rect()
        self.rect.center = self.x + self.W/2, self.y + self.H/2
        self.image.fill(color)
        self.image.set_alpha(alpha)