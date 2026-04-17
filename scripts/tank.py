from settings import *
import pygame as pg
from math import sin, cos, pi, radians, atan


class Tank(pg.sprite.Sprite):
    W = lencell
    H = W
    size = (W, H)
    delta = 7
    def __init__(self, x, y, team, orient, ttx):
        pg.sprite.Sprite.__init__(self)
        self.ttx = ttx
        self.team = team
        self.orient = orient
        self.x = x
        self.y = y
        self.place = [self.x//self.W, self.y//self.H]
        self.image = pg.Surface(self.size, pg.SRCALPHA)
        self.imageOrig = self.image
        self.rect = self.image.get_rect()
        self.rect.center = self.x + self.W / 2, self.y + self.H / 2
        self.image.fill(team_to_color[self.team])
        pg.draw.line(self.image, (0, 0, 0), (self.W-self.delta, self.delta),
                     (self.W-self.delta, self.H-self.delta),width=cellwidth)
        if self.ttx[-2] == 1:
            pg.draw.circle(self.image, (0, 0, 0), (self.W / 2, self.H / 2), 5*lencell/32)
        if self.ttx[-2] == 2:
            pg.draw.circle(self.image, (0, 0, 0), (self.W / 2, self.H / 2), lencell/4)
            pg.draw.circle(self.image, team_to_color[self.team], (self.W / 2, self.H / 2), lencell/8)
            pg.draw.rect(self.image, team_to_color[self.team], pg.Rect(0,0, self.W/2, self.H))
        if self.ttx[-2] == 3:
            pg.draw.line(self.image, (0, 0, 0),
                         (self.W/2, self.H/2), (self.W-self.delta, self.H/2),width=cellwidth-2)
            pg.draw.polygon(self.image, (0, 0, 0),
                            ((self.W-self.delta, self.H/2), (3/5*self.W, 2/5*self.H), (3/5*self.W, 3/5*self.H)))
        if self.ttx[-1] == 1:
            pg.draw.line(self.image, (0, 0, 0),(self.delta, 3/4*self.H),
                         (self.W/2, 3/4*self.H), width=cellwidth-2)
        if self.ttx[-1] == 2:
            pg.draw.line(self.image, (0, 0, 0), (self.delta, 11/16 * self.H),
                         (self.W / 2, 11/16 * self.H), width=cellwidth - 2)
            pg.draw.line(self.image, (0, 0, 0), (self.delta, 13/16 * self.H),
                         (self.W / 2, 13/16 * self.H), width=cellwidth - 2)
        if self.ttx[-1] == 3:
            pg.draw.line(self.image, (0, 0, 0), (self.delta, 5/8 * self.H),
                         (self.W / 2, 5/8 * self.H), width=cellwidth - 2)
            pg.draw.line(self.image, (0, 0, 0), (self.delta, 3 / 4 * self.H),
                         (self.W / 2, 3 / 4 * self.H), width=cellwidth - 2)
            pg.draw.line(self.image, (0, 0, 0), (self.delta, 7/8 * self.H),
                         (self.W / 2, 7/8 * self.H), width=cellwidth - 2)

        pg.draw.line(self.image, (0, 0, 0), (self.delta, 3/4*self.H - self.ttx[-1]/12*self.H),
                     (self.delta, 3/4*self.H + self.ttx[-1]/12*self.H), width=cellwidth-2)
        pg.draw.line(self.image, (0, 0, 0), (self.W/2, 3/4*self.H - self.ttx[-1]/12*self.H),
                     (self.W/2, 3/4*self.H + self.ttx[-1]/12*self.H), width=cellwidth-2)
        self.imageOrig = self.image

        self.vis = self.ttx[1]
        self.hp = self.ttx[1]
        self.a = [self.ttx[2], self.ttx[3], self.ttx[4]]
        self.m = [self.ttx[5], 32,self.ttx[7]]
        self.dam = self.ttx[8]
        self.pen = self.ttx[9]
        self.rel = 0                #self.ttx[10]
        self.dist = self.ttx[11]
        self.cost = self.ttx[12]

    def move(self, w, a, s, d, map, select_cell):
        map[self.place[1], self.place[0]] = 0
        if w == 1 and self.m[0] >= 1:
            if self.orient == 0 and self.place[1] != 0 and map[self.place[1]-1, self.place[0]] == 0:
                self.y -= self.H
                self.place[1] -= 1
            if self.orient == 1 and self.place[0] != maplenincells-1 and map[self.place[1], self.place[0]+1] == 0:
                self.x += self.W
                self.place[0] += 1
            if self.orient == 2 and self.place[1] != maplenincells-1 and map[self.place[1]+1, self.place[0]] == 0:
                self.y += self.H
                self.place[1] += 1
            if self.orient == 3 and self.place[0] != 0 and map[self.place[1], self.place[0]-1] == 0:
                self.x -= self.W
                self.place[0] -= 1
            self.m[0] -= 1
        if a == 1 and self.m[1] >= 1:
            self.orient -= 1
            if self.orient < 0:
                self.orient = 3
            self.m[1] -= 1
        if s == 1 and self.m[2] >= 1:
            if self.orient == 0 and self.place[1] != maplenincells-1 and map[self.place[1]+1, self.place[0]] == 0:
                self.y += self.H
                self.place[1] += 1
            if self.orient == 1 and self.place[0] != 0 and map[self.place[1], self.place[0]-1] == 0:
                self.x -= self.W
                self.place[0] -= 1
            if self.orient == 2 and self.place[1] != 0 and map[self.place[1]-1, self.place[0]] == 0:
                self.y -= self.H
                self.place[1] -= 1
            if self.orient == 3 and self.place[0] != maplenincells-1 and map[self.place[1], self.place[0]+1] == 0:
                self.x += self.W
                self.place[0] += 1
            self.m[3] -= 1
        if d == 1 and self.m[1] >= 1:
            self.orient += 1
            if self.orient > 3:
                self.orient = 0
            self.m[1] -= 1
        map[self.place[1], self.place[0]] = 2
        self.image = pg.transform.rotate(pg.transform.scale(self.imageOrig, self.size), -90*(self.orient-1))
        self.rect = self.image.get_rect()
        self.rect.center = self.x + self.W / 2, self.y + self.H / 2
        select_cell.rect.center = self.x + self.W / 2, self.y + self.H / 2

    def shot(self, all_projectiles, m_m_pos, Projectile):
        if self.rel == 0:
            angle = atan((m_m_pos[1] - self.rect.centery) / (m_m_pos[0] - self.rect.centerx))
            projectile = Projectile(self.rect.centerx, self.rect.centery, angle, self.dam, self.pen)
            all_projectiles.add(projectile)


    def update(self):
        self.m = [self.ttx[5], self.ttx[6], self.ttx[7]]
        if self.rel >= 1:
            self.rel -= 1