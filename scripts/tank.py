from importlib import reload
from scripts.functions import angle_vector, damage
from settings import *
import pygame as pg
from math import sin, cos, pi, radians, atan

class Tank(pg.sprite.Sprite):
    W = len_cell
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
                     (self.W-self.delta, self.H-self.delta), width=cell_width)
        if self.ttx[-2] == 1:
            pg.draw.circle(self.image, (0, 0, 0), (self.W / 2, self.H / 2), 5 * len_cell / 32)
        if self.ttx[-2] == 2:
            pg.draw.circle(self.image, (0, 0, 0), (self.W / 2, self.H / 2), len_cell / 4)
            pg.draw.circle(self.image, team_to_color[self.team], (self.W / 2, self.H / 2), len_cell / 8)
            pg.draw.rect(self.image, team_to_color[self.team], pg.Rect(0,0, self.W/2, self.H))
        if self.ttx[-2] == 3:
            pg.draw.line(self.image, (0, 0, 0),
                         (self.W/2, self.H/2), (self.W-self.delta, self.H/2), width=cell_width - 2)
            pg.draw.polygon(self.image, (0, 0, 0),
                            ((self.W-self.delta, self.H/2), (3/5*self.W, 2/5*self.H), (3/5*self.W, 3/5*self.H)))
        if self.ttx[-1] == 1:
            pg.draw.line(self.image, (0, 0, 0), (self.delta, 3/4*self.H),
                         (self.W/2, 3/4*self.H), width=cell_width - 2)
        if self.ttx[-1] == 2:
            pg.draw.line(self.image, (0, 0, 0), (self.delta, 11/16 * self.H),
                         (self.W / 2, 11/16 * self.H), width=cell_width - 2)
            pg.draw.line(self.image, (0, 0, 0), (self.delta, 13/16 * self.H),
                         (self.W / 2, 13/16 * self.H), width=cell_width - 2)
        if self.ttx[-1] == 3:
            pg.draw.line(self.image, (0, 0, 0), (self.delta, 5/8 * self.H),
                         (self.W / 2, 5/8 * self.H), width=cell_width - 2)
            pg.draw.line(self.image, (0, 0, 0), (self.delta, 3 / 4 * self.H),
                         (self.W / 2, 3 / 4 * self.H), width=cell_width - 2)
            pg.draw.line(self.image, (0, 0, 0), (self.delta, 7/8 * self.H),
                         (self.W / 2, 7/8 * self.H), width=cell_width - 2)

        pg.draw.line(self.image, (0, 0, 0), (self.delta, 3/4*self.H - self.ttx[-1]/12*self.H),
                     (self.delta, 3/4*self.H + self.ttx[-1]/12*self.H), width=cell_width - 2)
        pg.draw.line(self.image, (0, 0, 0), (self.W/2, 3/4*self.H - self.ttx[-1]/12*self.H),
                     (self.W/2, 3/4*self.H + self.ttx[-1]/12*self.H), width=cell_width - 2)
        self.imageOrig = self.image

        self.vis = self.ttx[0]
        self.hp = 100000#self.ttx[1]
        self.a = [self.ttx[2], self.ttx[3], self.ttx[4]]
        self.m = [100, self.ttx[6],self.ttx[7]] #self.ttx[5]
        self.dam = self.ttx[8]
        self.pen = self.ttx[9]
        self.rel = 0#self.ttx[10]
        self.dist = self.ttx[11]
        self.cost = self.ttx[12]
        self.exp = self.ttx[13]
        self.rel_dinamic = 0

    def move(self, w, a, s, d, map, select_cell):
        map[self.place[1], self.place[0]] = 0
        if w == 1 and self.m[0] >= 1:
            if self.orient == 0 and self.place[1] != 0 and map[self.place[1]-1, self.place[0]] == 0:
                self.y -= self.H
                self.place[1] -= 1
            if self.orient == 1 and self.place[0] != map_len_cells-1 and map[self.place[1], self.place[0] + 1] == 0:
                self.x += self.W
                self.place[0] += 1
            if self.orient == 2 and self.place[1] != map_len_cells-1 and map[self.place[1] + 1, self.place[0]] == 0:
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
            if self.orient == 0 and self.place[1] != map_len_cells-1 and map[self.place[1] + 1, self.place[0]] == 0:
                self.y += self.H
                self.place[1] += 1
            if self.orient == 1 and self.place[0] != 0 and map[self.place[1], self.place[0]-1] == 0:
                self.x -= self.W
                self.place[0] -= 1
            if self.orient == 2 and self.place[1] != 0 and map[self.place[1]-1, self.place[0]] == 0:
                self.y -= self.H
                self.place[1] -= 1
            if self.orient == 3 and self.place[0] != map_len_cells-1 and map[self.place[1], self.place[0] + 1] == 0:
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
        if self.rel_dinamic == 0:
            dx = m_m_pos[0] - self.rect.centerx
            dy = m_m_pos[1] - self.rect.centery
            angle = angle_vector(dx, dy)
            projectile = Projectile(self.rect.centerx, self.rect.centery, angle, self.dam, self.pen, self.team)
            all_projectiles.add(projectile)
            self.rel_dinamic = self.rel
    def get_bullet(self, bullet_angle, bullet_pos, bullet_dam, bullet_pen):
        tl = [self.rect.left - bullet_pos[0], self.rect.top - bullet_pos[1]]
        tr = [self.rect.right - bullet_pos[0], self.rect.top - bullet_pos[1]]
        br = [self.rect.right - bullet_pos[0], self.rect.bottom - bullet_pos[1]]
        bl = [self.rect.left - bullet_pos[0], self.rect.bottom - bullet_pos[1]]
        tl_angle = angle_vector(tl[0], tl[1])
        if tl_angle > 0:
            tl_angle = -tl_angle
        tr_angle = angle_vector(tr[0], tr[1])
        br_angle = angle_vector(br[0], br[1])
        bl_angle = angle_vector(bl[0], bl[1])
        bullet_angle += pi
        if bullet_angle < -pi:
            while bullet_angle < -pi:
                bullet_angle += 2 * pi
        else:
            while bullet_angle > pi:
                bullet_angle -= 2 * pi
        if tl_angle <= bullet_angle <= tr_angle:
            side=0
        if tr_angle <= bullet_angle <= br_angle:
            side=1
        if br_angle <= bullet_angle <= bl_angle:
            side=2
        if bl_angle <= bullet_angle or bullet_angle <= tl_angle:
            side=3
        if side == self.orient:
            arm = self.a[0]
        if abs(side-self.orient) == 1 or abs(side-self.orient) == 3:
            arm = self.a[1]
        if abs(side-self.orient) == 2:
            arm = self.a[2]
        if side == 0 or side == 2:
            arm /= abs(sin(bullet_angle))
        else:
            arm /= abs(cos(bullet_angle))
        self.hp -= damage(arm, bullet_pen, bullet_dam)
        if self.hp <= 0:
            self.kill()

    def draw(self, surface, team):
        surface.blit(self.image, (self.x, self.y))
        color = team_to_anticolor[self.team]
        hp_draw = font16.render(f"{int(self.hp)}", True, color)
        hp_draw.set_alpha(200)
        surface.blit(hp_draw, (self.x+self.delta/2, self.y+self.delta/2))
        if self.team == team:
            reload_draw = font16.render(f"|{self.rel_dinamic}", True, color)
            reload_draw.set_alpha(200)
            surface.blit(reload_draw, (self.x+self.W*0.8, self.y + self.delta / 2))
    def update(self):
        self.m = [self.ttx[5], self.ttx[6], self.ttx[7]]
        if self.rel_dinamic >= 1:
            self.rel_dinamic -= 1