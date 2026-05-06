from settings import *
import pygame as pg
from math import sin, cos, pi, radians

class Projectile(pg.sprite.Sprite):
    speed = projectile_speed
    def __init__(self, x, y, angle, dam, pen, team):
        pg.sprite.Sprite.__init__(self)
        self.team = team
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

    def proj_collide(self, all_walls, all_tanks, team_tanks, all_bases):
        if pg.sprite.spritecollide(self, all_walls, False):
            self.kill()
        tank = pg.sprite.spritecollide(self, all_tanks, False)
        if len(tank) != 0:
            if team_tanks.has(tank[0]) == False:
                if tank[0].rect.collidepoint(self.rect.center):
                    tank[0].get_bullet(self.angle, self.rect.center, self.dam, self.pen)
                    self.kill()
        base = pg.sprite.spritecollide(self, all_bases, False)
        if len(base) !=0:
            base[0].damage(self.dam)
            self.kill()

    def update(self, all_walls, all_tanks, team_tanks, all_bases):
        self.x += projectile_speed * cos(self.angle)
        self.y += projectile_speed * sin(self.angle)
        self.rect.center = (self.x, self.y)
        self.proj_collide(all_walls, all_tanks, team_tanks, all_bases)
