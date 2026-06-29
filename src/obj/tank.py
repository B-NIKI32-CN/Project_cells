import pygame as pg
import numpy as np
from math import sin, cos, pi, radians, atan

from ..core.settings import *
from ..utils.functions import angle_vector, damage

class Tank(pg.sprite.DirtySprite):
    W = len_cell
    H = W
    size = (W, H)
    delta = 7
    def __init__(self, x, y, team, orient, ttc, player, Mist, map):
        pg.sprite.DirtySprite.__init__(self)
        self.visible = True
        self.dirty = 1
        self.layer = LAYER_OBJECTS
        self.misty = 0
        self.ttc = ttc
        self.team = team
        self.player = player
        self.orient = orient
        self.Mist = Mist
        self.map = map
        self.x = x
        self.y = y
        self.drowed_stats = False
        self.place = [self.x//self.W, self.y//self.H]
        self.image = pg.Surface(self.size, pg.SRCALPHA)
        self.imageOrig = self.image
        self.rect = self.image.get_rect()
        self.rect.center = self.x + self.W / 2, self.y + self.H / 2
        self.image.fill(team_to_color[self.team])
        pg.draw.line(self.image, (0, 0, 0), (self.W-self.delta, self.delta),
                     (self.W-self.delta, self.H-self.delta), width=cell_width)
        if self.ttc[-2] == 1:
            pg.draw.circle(self.image, (0, 0, 0), (self.W / 2, self.H / 2), 5 * len_cell / 32)
        if self.ttc[-2] == 2:
            pg.draw.circle(self.image, (0, 0, 0), (self.W / 2, self.H / 2), len_cell / 4)
            pg.draw.circle(self.image, team_to_color[self.team], (self.W / 2, self.H / 2), len_cell / 8)
            pg.draw.rect(self.image, team_to_color[self.team], pg.Rect(0,0, self.W/2, self.H))
        if self.ttc[-2] == 3:
            pg.draw.line(self.image, (0, 0, 0),
                         (self.W/2, self.H/2), (self.W-self.delta, self.H/2), width=cell_width - 2)
            pg.draw.polygon(self.image, (0, 0, 0),
                            ((self.W-self.delta, self.H/2), (3/5*self.W, 2/5*self.H), (3/5*self.W, 3/5*self.H)))
        if self.ttc[-1] == 1:
            pg.draw.line(self.image, (0, 0, 0), (self.delta, 3/4*self.H),
                         (self.W/2, 3/4*self.H), width=cell_width - 2)
        if self.ttc[-1] == 2:
            pg.draw.line(self.image, (0, 0, 0), (self.delta, 11/16 * self.H),
                         (self.W / 2, 11/16 * self.H), width=cell_width - 2)
            pg.draw.line(self.image, (0, 0, 0), (self.delta, 13/16 * self.H),
                         (self.W / 2, 13/16 * self.H), width=cell_width - 2)
        if self.ttc[-1] == 3:
            pg.draw.line(self.image, (0, 0, 0), (self.delta, 5/8 * self.H),
                         (self.W / 2, 5/8 * self.H), width=cell_width - 2)
            pg.draw.line(self.image, (0, 0, 0), (self.delta, 3 / 4 * self.H),
                         (self.W / 2, 3 / 4 * self.H), width=cell_width - 2)
            pg.draw.line(self.image, (0, 0, 0), (self.delta, 7/8 * self.H),
                         (self.W / 2, 7/8 * self.H), width=cell_width - 2)

        pg.draw.line(self.image, (0, 0, 0), (self.delta, 3 / 4 * self.H - self.ttc[-1] / 12 * self.H),
                     (self.delta, 3 / 4 * self.H + self.ttc[-1] / 12 * self.H), width=cell_width - 2)
        pg.draw.line(self.image, (0, 0, 0), (self.W / 2, 3 / 4 * self.H - self.ttc[-1] / 12 * self.H),
                     (self.W / 2, 3 / 4 * self.H + self.ttc[-1] / 12 * self.H), width=cell_width - 2)
        pg.draw.line(self.image, team_to_anticolor[self.team], (0, 0), (self.W, 0), width=cell_width)
        pg.draw.line(self.image, team_to_anticolor[self.team], (0 + self.W, 0), (self.W, self.H),
                     width=cell_width + 2)
        pg.draw.line(self.image, team_to_anticolor[self.team], (self.W, self.H), (0, self.H),
                     width=cell_width + 2)
        pg.draw.line(self.image, team_to_anticolor[self.team], (0, self.H), (0, 0), width=cell_width)
        self.imageOrig = self.image.copy()
        self.image_for_stats = self.image.copy()


        self.vis = self.ttc[0]
        self.hp = 100000  #self.ttx[1]
        self.a = [self.ttc[2], self.ttc[3], self.ttc[4]]
        self.m = [1000, 37, self.ttc[7]] #self.ttx[5]
        self.dam = self.ttc[8]
        self.pen = self.ttc[9]
        self.rel = 0#self.ttx[10]
        self.dist = self.ttc[11]
        self.cost = self.ttc[12]
        self.exp = self.ttc[13]
        self.rel_dinamic = 0

        radius2 = self.vis**2
        i, j = np.indices((self.vis*2 + 1, self.vis*2 + 1))
        dist_in2 = (self.vis - i)**2 + (self.vis - j)**2-1
        pos = np.where(dist_in2 <= radius2)
        dist_in2[:,:] = 0
        dist_in2[pos] = 1
        self.mist_matrix = dist_in2

    def move(self, w, a, s, d, select_cell):
        self.map[self.place[1], self.place[0]] = 0
        if w == 1 and self.m[0] >= 1:
            if self.orient == 0 and self.place[1] != 0 and self.map[self.place[1]-1, self.place[0]] == 0:
                self.y -= self.H
                self.place[1] -= 1
            if self.orient == 1 and self.place[0] != map_len_cells-1 and self.map[self.place[1], self.place[0] + 1] == 0:
                self.x += self.W
                self.place[0] += 1
            if self.orient == 2 and self.place[1] != map_len_cells-1 and self.map[self.place[1] + 1, self.place[0]] == 0:
                self.y += self.H
                self.place[1] += 1
            if self.orient == 3 and self.place[0] != 0 and self.map[self.place[1], self.place[0]-1] == 0:
                self.x -= self.W
                self.place[0] -= 1
            self.m[0] -= 1
        if a == 1 and self.m[1] >= 1:
            self.orient -= 1
            if self.orient < 0:
                self.orient = 3
            self.m[1] -= 1
        if s == 1 and self.m[2] >= 1:
            if self.orient == 0 and self.place[1] != map_len_cells-1 and self.map[self.place[1] + 1, self.place[0]] == 0:
                self.y += self.H
                self.place[1] += 1
            if self.orient == 1 and self.place[0] != 0 and self.map[self.place[1], self.place[0]-1] == 0:
                self.x -= self.W
                self.place[0] -= 1
            if self.orient == 2 and self.place[1] != 0 and self.map[self.place[1]-1, self.place[0]] == 0:
                self.y -= self.H
                self.place[1] -= 1
            if self.orient == 3 and self.place[0] != map_len_cells-1 and self.map[self.place[1], self.place[0] + 1] == 0:
                self.x += self.W
                self.place[0] += 1
            self.m[2] -= 1
        if d == 1 and self.m[1] >= 1:
            self.orient += 1
            if self.orient > 3:
                self.orient = 0
            self.m[1] -= 1
        if a == 1 or w == 1 or s == 1 or d == 1:
            self.map[self.place[1], self.place[0]] = 2
            self.image = pg.transform.rotate(pg.transform.scale(self.imageOrig, self.size), -90*(self.orient-1))
            self.image_for_stats = pg.transform.rotate(pg.transform.scale(self.imageOrig, self.size), -90*(self.orient-1))
            self.rect = self.image.get_rect()
            self.rect.center = self.x + self.W / 2, self.y + self.H / 2
            select_cell.rect.center = self.x + self.W / 2, self.y + self.H / 2
            select_cell.dirty = 1
            self.dirty = 1
            self.drowed_stats = False

    def shot(self, all_projectiles, all_sprites, m_m_pos, Projectile):
        if self.rel_dinamic == 0:
            dx = m_m_pos[0] - self.rect.centerx
            dy = m_m_pos[1] - self.rect.centery
            angle = angle_vector(dx, dy)
            projectile = Projectile(self.rect.centerx, self.rect.centery, angle, self.dam, self.pen, (self.dist+0.5)*len_cell + 1, self.team)  # можно и self.H но они равны
            all_projectiles.add(projectile)
            all_sprites.add(projectile)
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

        print(f"side: {side}, arm: {arm}\n tl_angle: {180/pi*tl_angle}\n"
              f" tr_angle: {180/pi*tr_angle}\n br_angle: {180/pi*br_angle}\n"
              f" bl_angle: {180/pi*bl_angle}\n bullet_angle: {180/pi*bullet_angle}\n"
              f"rect_b: {self.rect.bottom}, bul_pos: {bullet_pos}\n\n\n ")
        dam = damage(arm, bullet_pen, bullet_dam)
        self.hp -= dam
        if self.hp <= 0:
            self.map[self.place[1], self.place[0]] = 0
            self.dirty = 1
            self.kill()
        self.drowed_stats = False

        return dam

    def draw_stats(self, team):
        color = team_to_anticolor[self.team]
        hp_draw = font16.render(f"{int(self.hp)}", True, color)
        hp_draw.set_alpha(200)
        if self.drowed_stats == False:
            self.dirty = 1
            self.image = self.image_for_stats.copy()
            if self.team == team:
                reload_draw = font16.render(f"|{self.rel_dinamic}", True, color)
                reload_draw.set_alpha(200)
                self.image.blit(reload_draw, (self.W*0.7, self.delta / 2))

            self.image.blit(hp_draw, (self.delta/2+self.W*0.1, self.delta/2))

        self.drowed_stats = True

    def update(self):
        self.m = [self.ttc[5], self.ttc[6], self.ttc[7]]
        if self.rel_dinamic >= 1:
            self.rel_dinamic -= 1

    def change_misty(self, misty):
        if misty != self.misty:
            self.misty = misty
            self.dirty = 1
            if misty == 1:
                self.visible = False
            else:
                self.visible = True