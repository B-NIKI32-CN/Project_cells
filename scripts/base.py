import pygame as pg
from settings import *


class Base(pg.sprite.Sprite):
    hp = base_hp
    W = len_cell
    H = W
    size = (W, H)
    delta = 7
    def __init__(self, x, y, team, player):
        pg.sprite.Sprite.__init__(self)
        self.team = team
        self.player = player
        self.x = x
        self.y = y
        self.place = [self.x // self.W, self.y // self.H]
        self.image = pg.Surface(self.size, pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = self.x + self.W/2, self.y + self.H/2
        self.image.fill(team_to_color[self.team])
        pg.draw.rect(self.image, (0, 0, 0), pg.Rect(self.W/4, self.H/4, self.W/2, self.H/2))
        pg.draw.line(self.image, team_to_anticolor[self.team], (0, 0), (self.W, 0), width=cell_width)
        pg.draw.line(self.image, team_to_anticolor[self.team], (0 + self.W, 0), (self.W, self.H),
                     width=cell_width + 2)
        pg.draw.line(self.image, team_to_anticolor[self.team], (self.W, self.H), (0, self.H),
                     width=cell_width + 2)
        pg.draw.line(self.image, team_to_anticolor[self.team], (0, self.H), (0, 0), width=cell_width)

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))
        color = team_to_anticolor[self.team]
        hp_draw = font16.render(f"{self.hp}", True, color)
        hp_draw.set_alpha(200)
        surface.blit(hp_draw, (self.x + self.delta / 2, self.y + self.delta / 2))

    def damage(self, damage):
        self.hp -= damage
        self.player.hp = self.hp
        if self.hp <= 0:
            self.kill()
            self.player.hp = 0