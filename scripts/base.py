import pygame as pg
# from settings import *
import settings


class Base(pg.sprite.Sprite):
    hp = 2000
    W = settings.lencell
    H = W
    size = (W, H)
    def __init__(self, x, y, team):
        pg.sprite.Sprite.__init__(self)
        self.team = team
        self.x = x
        self.y = y
        self.image = pg.Surface(self.size, pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = self.x + self.W/2, self.y + self.H/2
        self.image.fill(settings.team_to_color[self.team])
        pg.draw.rect(self.image, (0, 0, 0), pg.Rect(self.W/4, self.H/4, self.W/2, self.H/2))