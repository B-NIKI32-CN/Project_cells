from settings import *
import pygame as pg
from math import sin, cos, pi, radians
from scripts.functions import calclin, dist_linpoint

class Projectile(pg.sprite.Sprite):
    speed = projectile_speed
    def __init__(self, x, y, angle, dam, pen, dist, team):
        pg.sprite.Sprite.__init__(self)
        self.team = team
        self.x = x
        self.y = y
        self.angle = angle
        self.dam = dam
        self.pen = pen
        self.dist = dist
        self.size = (projectile_size, projectile_size)
        self.dx = projectile_speed * cos(self.angle)
        self.dy = projectile_speed * sin(self.angle)
        self.image = pg.Surface((abs(self.dx)+1,abs(self.dy)+1), pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = ((self.x-self.dx)/2, (self.y-self.dy)/2)
        pg.draw.line(self.image, (255,0,0), (abs(self.dx/2)+self.dx/2, abs(self.dy/2)+self.dy/2), (abs(self.dx/2)-self.dx/2, abs(self.dy/2)-self.dy/2), width=projectile_size)
        self.solve, self.equals = calclin((self.x,self.y),(self.x + self.dx, self.y + self.dy))

    def proj_collide(self, all_walls, all_tanks, team_tanks, all_bases):
        wall = pg.sprite.spritecollide(self, all_walls, False)
        if len(wall) != 0:
            for w in wall:
                dist = dist_linpoint(w.rect.center, self.solve, self.equals)
                if w.rect.collidepoint(self.rect.center) or dist < len_cell*(2**0.5 / 2):
                    self.kill()
        tank = pg.sprite.spritecollide(self, all_tanks, False)
        if len(tank) != 0:
            if team_tanks.has(tank[0]) == False:
                if tank[0].rect.collidepoint(self.rect.center):
                    tank[0].get_bullet(self.angle, self.rect.center, self.dam, self.pen)
                    self.kill()
        base = pg.sprite.spritecollide(self, all_bases, False)
        if len(base) !=0:
            for b in base:
                dist = dist_linpoint(b.rect.center, self.solve, self.equals)
                if b.rect.collidepoint(self.rect.center) or dist < len_cell*(2**0.5 / 2):
                    self.kill()
                    base[0].damage(self.dam)

    def update(self, all_walls, all_tanks, team_tanks, all_bases):
        self.proj_collide(all_walls, all_tanks, team_tanks, all_bases)
        self.x += self.dx
        self.y += self.dy
        self.dist -= (self.dx**2 + self.dy**2)**0.5
        self.rect.center = (self.x, self.y)
        if self.dist <= 0:
            self.kill()