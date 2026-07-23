import pygame as pg
from ..core.settings import *


class ImgTank(pg.sprite.DirtySprite):
    W = len_cell
    H = W
    size = (W, H)
    delta = 7
    def __init__(self, x, y, team, orient, ttc, *groups):
        super().__init__(*groups)
        self.visible = 1
        self.dirty = 2
        self.layer = LAYER_UI
        self.ttc = ttc.copy()
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
        if self.ttc["class"] == 1:
            pg.draw.circle(self.image, (0, 0, 0), (self.W / 2, self.H / 2), 5 * len_cell / 32)
        if self.ttc["class"] == 2:
            pg.draw.circle(self.image, (0, 0, 0), (self.W / 2, self.H / 2), len_cell / 4)
            pg.draw.circle(self.image, team_to_color[self.team], (self.W / 2, self.H / 2), len_cell / 8)
            pg.draw.rect(self.image, team_to_color[self.team], pg.Rect(0,0, self.W/2, self.H))
        if self.ttc["class"] == 3:
            pg.draw.line(self.image, (0, 0, 0),
                         (self.W/2, self.H/2), (self.W-self.delta, self.H/2), width=cell_width - 2)
            pg.draw.polygon(self.image, (0, 0, 0),
                            ((self.W-self.delta, self.H/2), (3/5*self.W, 2/5*self.H), (3/5*self.W, 3/5*self.H)))
        if self.ttc["stage"] == 1:
            pg.draw.line(self.image, (0, 0, 0), (self.delta, 3/4*self.H),
                         (self.W/2, 3/4*self.H), width=cell_width - 2)
        if self.ttc["stage"] == 2:
            pg.draw.line(self.image, (0, 0, 0), (self.delta, 11/16 * self.H),
                         (self.W / 2, 11/16 * self.H), width=cell_width - 2)
            pg.draw.line(self.image, (0, 0, 0), (self.delta, 13/16 * self.H),
                         (self.W / 2, 13/16 * self.H), width=cell_width - 2)
        if self.ttc["stage"] == 3:
            pg.draw.line(self.image, (0, 0, 0), (self.delta, 5/8 * self.H),
                         (self.W / 2, 5/8 * self.H), width=cell_width - 2)
            pg.draw.line(self.image, (0, 0, 0), (self.delta, 3 / 4 * self.H),
                         (self.W / 2, 3 / 4 * self.H), width=cell_width - 2)
            pg.draw.line(self.image, (0, 0, 0), (self.delta, 7/8 * self.H),
                         (self.W / 2, 7/8 * self.H), width=cell_width - 2)

        pg.draw.line(self.image, (0, 0, 0), (self.delta, 3/4*self.H - self.ttc["stage"]/12*self.H),
                     (self.delta, 3/4*self.H + self.ttc["stage"]/12*self.H), width=cell_width - 2)
        pg.draw.line(self.image, (0, 0, 0), (self.W/2, 3/4*self.H - self.ttc["stage"]/12*self.H),
                     (self.W/2, 3/4*self.H + self.ttc["stage"]/12*self.H), width=cell_width - 2)
        self.imageOrig = self.image

        self.id = self.ttc["id"]
        self.viewing = self.ttc["viewing"]
        self.health = self.ttc["health"]  # self.ttx[1]
        self.armor = self.ttc["armor"]
        self.mobility = self.ttc["mobility"]  # self.ttx[5]
        self.damage = self.ttc["damage"]
        self.penetration = self.ttc["penetration"]
        self.cooldown = self.ttc["cooldown"]
        self.distance = self.ttc["distance"]
        self.resource = self.ttc["resource"]
        self.exp = self.ttc["exp"]
        self.reload_time_left = 0

        text_cost = font16.render(f"{self.resource}", True, team_to_anticolor[self.team])
        text_exp = font16.render(f"{self.exp}", True, team_to_anticolor[self.team])

        self.image.blit(text_cost, (self.W*0.1, self.H*0.1))
        self.image.blit(text_exp, (self.W*0.1,self.H/4+self.H*0.1))

    def mk_dirty2(self):
        self.dirty = 2