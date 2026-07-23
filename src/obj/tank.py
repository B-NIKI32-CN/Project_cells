from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..core.player import Player
    from ..core.game_manager import GameManager


import pygame as pg
import numpy as np
from math import sin, cos, pi


from ..core.settings import *
from ..data.maps import ID_TANK
from ..utils.functions import angle_vector, damage


class Tank(pg.sprite.DirtySprite):
    W = len_cell
    H = W
    size = (W, H)
    delta = 7
    def __init__(self, id, pos, orient, ttc, player: Player, game_manager: GameManager, *groups):
        super().__init__(*groups)
        self.game_manager = game_manager
        self.id = id
        self.visible = 1
        self.dirty = 1
        self.layer = LAYER_OBJECTS
        self.misty = 0
        self.ttc = ttc.copy()
        self.team = player.team
        player.tanks.add(self)
        self.orient = orient
        self.tile_map = game_manager.tile_map
        self.drowed_stats = False
        self.place = list(pos)
        self.x = self.place[0] * self.W
        self.y = self.place[1] * self.H
        self.tile_map[self.place[1], self.place[0]] = ID_TANK
        self.image = pg.Surface(self.size, pg.SRCALPHA)
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

        pg.draw.line(self.image, (0, 0, 0), (self.delta, 3 / 4 * self.H - self.ttc["stage"] / 12 * self.H),
                     (self.delta, 3 / 4 * self.H + self.ttc["stage"] / 12 * self.H), width=cell_width - 2)
        pg.draw.line(self.image, (0, 0, 0), (self.W / 2, 3 / 4 * self.H - self.ttc["stage"] / 12 * self.H),
                     (self.W / 2, 3 / 4 * self.H + self.ttc["stage"] / 12 * self.H), width=cell_width - 2)
        pg.draw.line(self.image, team_to_anticolor[self.team], (0, 0), (self.W, 0), width=cell_width)
        pg.draw.line(self.image, team_to_anticolor[self.team], (0 + self.W, 0), (self.W, self.H),
                     width=cell_width + 2)
        pg.draw.line(self.image, team_to_anticolor[self.team], (self.W, self.H), (0, self.H),
                     width=cell_width + 2)
        pg.draw.line(self.image, team_to_anticolor[self.team], (0, self.H), (0, 0), width=cell_width)
        self.imageOrig = self.image.copy()
        self.image_for_stats = self.image.copy()


        self.viewing = self.ttc["viewing"]
        self.health = 100000  # self.ttc[health]
        self.armor_list = self.ttc["armor"].copy()
        self.movement_balance_list = [1000, 37, self.ttc["mobility"][2]] # self.ttc["mobility"].copy()
        self.damage = self.ttc["damage"]
        self.penetration = self.ttc["penetration"]
        self.cooldown = 0 # self.ttx[10]
        self.distance = self.ttc["distance"]
        self.resource = self.ttc["resource"]
        self.exp = self.ttc["exp"]
        self.reload_time_left = 0

        radius2 = self.viewing**2
        i, j = np.indices((self.viewing*2 + 1, self.viewing*2 + 1))
        dist_in2 = (self.viewing - i)**2 + (self.viewing - j)**2-1
        pos = np.where(dist_in2 <= radius2)
        dist_in2[:,:] = 0
        dist_in2[pos] = 1
        self.mist_matrix = dist_in2

    def move(self, direction):
        if direction not in ("forward", "left", "backward", "right"):
            return False

        old_place = self.place.copy()
        if direction == "forward":
            if self.movement_balance_list[0] <= 0:
                return False
            elif self.orient == 0 and self.place[1] != 0 and self.tile_map[self.place[1]-1, self.place[0]] == 0:
                self.y -= self.H
                self.place[1] -= 1
            elif self.orient == 1 and self.place[0] != map_len_cells-1 and self.tile_map[self.place[1], self.place[0] + 1] == 0:
                self.x += self.W
                self.place[0] += 1
            elif self.orient == 2 and self.place[1] != map_len_cells-1 and self.tile_map[self.place[1] + 1, self.place[0]] == 0:
                self.y += self.H
                self.place[1] += 1
            elif self.orient == 3 and self.place[0] != 0 and self.tile_map[self.place[1], self.place[0]-1] == 0:
                self.x -= self.W
                self.place[0] -= 1
            else:
                return False
            self.movement_balance_list[0] -= 1
        elif direction == "left":
            if self.movement_balance_list[1] <= 0:
                return False
            self.orient = (self.orient - 1) % 4
            self.movement_balance_list[1] -= 1
        elif direction == "backward":
            if self.movement_balance_list[2] <= 0:
                return False
            elif self.orient == 0 and self.place[1] != map_len_cells-1 and self.tile_map[self.place[1] + 1, self.place[0]] == 0:
                self.y += self.H
                self.place[1] += 1
            elif self.orient == 1 and self.place[0] != 0 and self.tile_map[self.place[1], self.place[0]-1] == 0:
                self.x -= self.W
                self.place[0] -= 1
            elif self.orient == 2 and self.place[1] != 0 and self.tile_map[self.place[1]-1, self.place[0]] == 0:
                self.y -= self.H
                self.place[1] -= 1
            elif self.orient == 3 and self.place[0] != map_len_cells-1 and self.tile_map[self.place[1], self.place[0] + 1] == 0:
                self.x += self.W
                self.place[0] += 1
            else:
                return False
            self.movement_balance_list[2] -= 1
        elif direction == "right":
            if self.movement_balance_list[1] <= 0:
                return False
            self.orient = (self.orient + 1) % 4
            self.movement_balance_list[1] -= 1

        self.tile_map[old_place[1], old_place[0]] = 0
        self.tile_map[self.place[1], self.place[0]] = 2
        self.image = pg.transform.rotate(pg.transform.scale(self.imageOrig, self.size), -90*(self.orient-1))
        self.image_for_stats = pg.transform.rotate(pg.transform.scale(self.imageOrig, self.size), -90*(self.orient-1))
        self.rect = self.image.get_rect()
        self.rect.center = self.x + self.W / 2, self.y + self.H / 2
        self.dirty = 1
        self.drowed_stats = False
        return True


    def shot(self, all_projectiles, m_m_pos, Projectile, id, game_manager):
        if self.reload_time_left == 0:
            dx = m_m_pos[0] - self.rect.centerx
            dy = m_m_pos[1] - self.rect.centery
            angle = angle_vector(dx, dy)
            projectile = Projectile(self.rect.centerx, self.rect.centery, angle,
                                     self.damage, self.penetration,
                                       (self.distance+0.5)*len_cell + 1, self.team,
                                         id, game_manager)  # можно и self.H но они равны
            all_projectiles.add(projectile)
            self.reload_time_left = self.cooldown
            self.drowed_stats = False
            return projectile

    def bullet_collide(self, bullet_angle, bullet_pos, bullet_dam, bullet_pen):
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
        elif tr_angle <= bullet_angle <= br_angle:
            side=1
        elif br_angle <= bullet_angle <= bl_angle:
            side=2
        else: #bl_angle <= bullet_angle or bullet_angle <= tl_angle
            side=3
        if side == self.orient:
            arm = self.armor_list[0]
        elif abs(side-self.orient) == 1 or abs(side-self.orient) == 3:
            arm = self.armor_list[1]
        else:  #abs(side-self.orient) == 2
            arm = self.armor_list[2]
        if side == 0 or side == 2:
            arm /= abs(sin(bullet_angle))
        else:
            arm /= abs(cos(bullet_angle))

        # print(f"side: {side}, arm: {arm}\n tl_angle: {180/pi*tl_angle}\n"
        #       f" tr_angle: {180/pi*tr_angle}\n br_angle: {180/pi*br_angle}\n"
        #       f" bl_angle: {180/pi*bl_angle}\n bullet_angle: {180/pi*bullet_angle}\n"
        #       f"rect_b: {self.rect.bottom}, bul_pos: {bullet_pos}\n\n")
        dam = damage(arm, bullet_pen, bullet_dam)
        self.health -= dam
        if self.health <= 0:
            self.tile_map[self.place[1], self.place[0]] = 0
            self.dirty = 1
            self.game_manager.delete_id(self.id)
            self.kill()
        self.drowed_stats = False

        return dam

    def draw_stats(self, team):
        if self.drowed_stats == False:
            color = team_to_anticolor[self.team]
            hp_draw = font16.render(f"{int(self.health)}", True, color)
            hp_draw.set_alpha(200)
            self.dirty = 1
            self.image = self.image_for_stats.copy()
            if self.team == team:
                reload_draw = font16.render(f"|{self.reload_time_left}", True, color)
                reload_draw.set_alpha(200)
                self.image.blit(reload_draw, (self.W*0.7, self.delta / 2))

            self.image.blit(hp_draw, (self.delta/2+self.W*0.1, self.delta/2))

        self.drowed_stats = True

    def update(self):
        self.movement_balance_list = self.ttc["mobility"].copy()
        if self.reload_time_left >= 1:
            self.reload_time_left -= 1

    def change_misty(self, misty):
        if misty != self.misty:
            self.misty = misty
            self.dirty = 1
            if misty == 1:
                self.visible = 0
            else:
                self.visible = 1

    # def kill(self):
    #     super().kill()
    #     game_manager.delete_tank()
