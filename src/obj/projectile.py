import pygame as pg
from math import sin, cos, pi, radians

from ..core.settings import *
from ..utils.functions import calclin, dist_linpoint


class Projectile(pg.sprite.DirtySprite):
    speed = projectile_speed
    def __init__(self, x, y, angle, dam, pen, dist, team):
        pg.sprite.DirtySprite.__init__(self)
        self.visible = True
        self.dirty = 2
        self.layer = LAYER_PROJECTILES
        self.team = team
        self.x = x
        self.y = y
        self.angle = angle
        self.dam = dam
        self.pen = pen
        self.dist = dist
        self.size = projectile_size
        self.dx = projectile_speed * cos(self.angle) * self.dist/len_cell
        self.dy = projectile_speed * sin(self.angle) * self.dist/len_cell
        self.image = pg.Surface((abs(self.dx)+2*self.size, abs(self.dy)+2*self.size), pg.SRCALPHA)
        # self.image.fill((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (self.x-self.dx/2, self.y-self.dy/2)

        pg.draw.line(self.image, (255,0,0), (abs(self.dx/2)+self.dx/2 + self.size, abs(self.dy/2)+self.dy/2 + self.size),
                     (abs(self.dx/2)-self.dx/2 + self.size, abs(self.dy/2)-self.dy/2 + self.size), width=self.size)

        self.solve, self.equals = calclin((self.x,self.y),(self.x + self.dx, self.y + self.dy))
        self.die = 0
        self.dmove = (self.dx**2 + self.dy**2)**0.5

    def proj_collide(self, all_walls, all_tanks, team_tanks, all_bases, map_matrix):
        wall = pg.sprite.spritecollide(self, all_walls, False)
        if len(wall) != 0:
            for w in wall:
                dist = dist_linpoint(w.rect.center, self.solve, self.equals)
                if w.rect.collidepoint(self.rect.center) or dist < len_cell*(2**0.5 / 2):
                    self.die = 1
                    return 0
        tank = pg.sprite.spritecollide(self, all_tanks, False)
        if len(tank) != 0:
            for t in tank:
                if team_tanks.has(t) == False:
                    dist = dist_linpoint(t.rect.center, self.solve, self.equals)
                    if t.rect.collidepoint(self.rect.center):
                        dam = t.get_bullet(self.angle, self.rect.center, self.dam, self.pen)
                        self.die = 1
                        return dam
                    elif dist < len_cell*(2**0.5 *0.5):
                        angle = self.angle + pi/2
                        point = t.rect.centerx + len_cell/2*cos(angle), t.rect.centery + len_cell/2*sin(angle)
                        dist_point = dist_linpoint(point, self.solve, self.equals)
                        if dist_point > len_cell/2:
                            point = t.rect.centerx - len_cell/2*cos(angle), t.rect.centery - len_cell/2*sin(angle)
                        if t.rect.collidepoint(point):
                            dam = t.get_bullet(self.angle, point, self.dam, self.pen)
                            self.die = 1
                            return dam
        base = pg.sprite.spritecollide(self, all_bases, False)
        if len(base) !=0:
            for b in base:
                dist = dist_linpoint(b.rect.center, self.solve, self.equals)
                if b.rect.collidepoint(self.rect.center) or dist < len_cell*(2**0.5 / 2):
                    self.die = 1
                    base[0].damage(self.dam)
                    return self.dam
        return 0

    def update(self, all_walls, all_tanks, team_tanks, all_bases, map_matrix):
        if self.die == 1 or self.dist <= 0:
            self.kill()
        self.x += self.dx*0.5
        self.y += self.dy*0.5
        self.dist -= self.dmove*0.5
        if self.dist < 0:
            self.x += self.dist/self.dmove * self.dx
            self.y += self.dist/self.dmove * self.dy
        self.rect.center = (self.x, self.y)
        if self.die == 0:
            dam = self.proj_collide(all_walls, all_tanks, team_tanks, all_bases, map_matrix)
            return dam
        return 0