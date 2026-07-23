from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..core.game_manager import GameManager
    

import pygame as pg

from ..core.settings import *
from ..data.maps import ID_BASE


class Base(pg.sprite.DirtySprite):
    hp = base_hp
    W = len_cell
    H = W
    size = (W, H)
    delta = 7
    def __init__(self, pos, player, tile_map, id, game_manager: GameManager):
        pg.sprite.DirtySprite.__init__(self)
        self.game_manager = game_manager
        self.id = id
        self.visible = 1
        self.dirty = 1
        self.layer = LAYER_OBJECTS
        self.misty = 0
        self.team = player.team
        self.player = player
        self.player.base = self
        self.place = pos
        self.x = self.place[0] * self.W
        self.y = self.place[1] * self.H
        tile_map[self.place[1], self.place[0]] = ID_BASE
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

        self.drowed_stats = False
        self.imageOrig = self.image.copy()
        
        self.damage(0)

    # def draw(self, surface):
    #     surface.blit(self.image, (self.x, self.y))
    #     color = team_to_anticolor[self.team]
    #     hp_draw = font16.render(f"{self.hp}", True, color)
    #     hp_draw.set_alpha(200)
    #     surface.blit(hp_draw, (self.x + self.delta / 2, self.y + self.delta / 2))

    def damage(self, damage):
        self.drowed_stats = False
        self.hp -= damage
        self.player.hp = self.hp
        if self.hp <= 0:
            self.game_manager.delete_id(self.id)
            self.kill()
            self.player.hp = 0

    def change_misty(self, misty):
        if misty != self.misty:
            self.misty = misty
            self.dirty = 1
            if misty == 1:
                self.visible = 0
            else:
                self.visible = 1
    
    def draw_stats(self):
        if not self.drowed_stats:
            color = team_to_anticolor[self.team]
            hp_draw = font16.render(f"{int(self.hp)}", True, color)
            hp_draw.set_alpha(200)
            self.dirty = 1
            self.image = self.imageOrig.copy()
            self.image.blit(hp_draw, (self.delta/2+self.W*0.1, self.delta/2))

        self.drowed_stats = True