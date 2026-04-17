from settings import *
import pygame as pg
from math import sin, cos, pi, radians

class Projectile(pg.sprite.Sprite):
    speed = projectile_speed
    def __init__(self, x, y, angle, dam, pen):
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.angle = angle
        self.dam = dam
        self.pen = pen
        self.size = (projectile_size, projectile_size)
        self.image = pg.Surface(self.size, pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        pg.draw.circle(self.image, (255,0,0), (projectile_size/2, projectile_size/2), projectile_size/2)

    def update(self):
        self.x += projectile_speed * cos(self.angle)
        self.y += projectile_speed * sin(self.angle)
        self.rect.center = (self.x, self.y)
