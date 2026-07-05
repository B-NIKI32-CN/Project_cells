import pygame as pg
from math import sin, cos, pi, radians

from ..core.settings import *
from ..utils.functions import calclin, dist_linpoint, calclinspount, segment_collide


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
                if w.rect.collidepoint(self.rect.center):
                    self.die = 1
                    return 0
                sides = [w.rect.topleft, w.rect.topright, w.rect.bottomleft, w.rect.bottomright]
                projectile_last_pos = self.x - self.dx*0.5, self.y - self.dy*0.5
                top_point = segment_collide((self.x, self.y), projectile_last_pos, sides[0], sides[1])
                if any(top_point):
                    self.die = 1
                    return 0
                right_point = segment_collide((self.x, self.y), projectile_last_pos, sides[1], sides[2])
                if any(right_point):
                    self.die = 1
                    return 0
                bottom_point = segment_collide((self.x, self.y), projectile_last_pos, sides[2], sides[3])
                if any(bottom_point):
                    self.die = 1
                    return 0
                left_point = segment_collide((self.x, self.y), projectile_last_pos, sides[3], sides[0])
                if any(left_point):
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
                    sides = [t.rect.topleft, t.rect.topright, t.rect.bottomleft, t.rect.bottomright]
                    projectile_last_pos = self.x - self.dx * 0.5, self.y - self.dy * 0.5
                    top_point = segment_collide((self.x, self.y), projectile_last_pos, sides[0], sides[1])
                    if any(top_point):
                        dam = t.get_bullet(self.angle, top_point, self.dam, self.pen)
                        self.die = 1
                        return dam
                    right_point = segment_collide((self.x, self.y), projectile_last_pos, sides[1], sides[2])
                    if any(right_point):
                        dam = t.get_bullet(self.angle, right_point, self.dam, self.pen)
                        self.die = 1
                        return dam
                    bottom_point = segment_collide((self.x, self.y), projectile_last_pos, sides[2], sides[3])
                    if any(bottom_point):
                        dam = t.get_bullet(self.angle, bottom_point, self.dam, self.pen)
                        self.die = 1
                        return dam
                    left_point = segment_collide((self.x, self.y), projectile_last_pos, sides[3], sides[0])
                    if any(left_point):
                        dam = t.get_bullet(self.angle, left_point, self.dam, self.pen)
                        self.die = 1
                        return dam
                    
        base = pg.sprite.spritecollide(self, all_bases, False)
        if len(base) !=0:
            for b in base:
                if b.rect.collidepoint(self.rect.center):
                    damage = self.dam
                    self.die = 1
                    return damage
                sides = [b.rect.topleft, b.rect.topright, b.rect.bottomleft, b.rect.bottomright]
                projectile_last_pos = self.x - self.dx*0.5, self.y - self.dy*0.5
                top_point = segment_collide((self.x, self.y), projectile_last_pos, sides[0], sides[1])
                if any(top_point):
                    damage = self.dam
                    self.die = 1
                    return damage
                right_point = segment_collide((self.x, self.y), projectile_last_pos, sides[1], sides[2])
                if any(right_point):
                    damage = self.dam
                    self.die = 1
                    return damage
                bottom_point = segment_collide((self.x, self.y), projectile_last_pos, sides[2], sides[3])
                if any(bottom_point):
                    damage = self.dam
                    self.die = 1
                    return damage
                left_point = segment_collide((self.x, self.y), projectile_last_pos, sides[3], sides[0])
                if any(left_point):
                    damage = self.dam
                    self.die = 1
                    return damage
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