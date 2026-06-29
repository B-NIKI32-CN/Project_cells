import pygame as pg
from ..core.settings import *


class ImgTank(pg.sprite.DirtySprite):
    W = len_cell
    H = W
    size = (W, H)
    delta = 7
    def __init__(self, x, y, team, orient, ttx):
        pg.sprite.DirtySprite.__init__(self)
        self.visible = True
        self.dirty = 2
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
        self.hp = self.ttx[1]  # self.ttx[1]
        self.a = [self.ttx[2], self.ttx[3], self.ttx[4]]
        self.m = [self.ttx[5], 37, self.ttx[7]]  # self.ttx[5]
        self.dam = self.ttx[8]
        self.pen = self.ttx[9]
        self.rel = self.ttx[10]
        self.dist = self.ttx[11]
        self.cost = self.ttx[12]
        self.exp = self.ttx[13]
        self.rel_dinamic = 0

        text_cost = font16.render(f"{self.cost}", True, team_to_anticolor[self.team])
        text_exp = font16.render(f"{self.exp}", True, team_to_anticolor[self.team])

        self.image.blit(text_cost, (self.W*0.1, self.H*0.1))
        self.image.blit(text_exp, (self.W*0.1,self.H/4+self.H*0.1))

    def mk_dirty2(self):
        self.dirty = 2