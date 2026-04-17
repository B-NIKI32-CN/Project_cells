from settings import *
import pygame as pg


class ImgTank(pg.sprite.Sprite):
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