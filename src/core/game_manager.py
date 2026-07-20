import pygame as pg

from ..core.settings import *
from .. import core, data, obj, ui, utils
from ..utils.functions import get_world_mouse_pos


class GameManager():
    def __init__(self):

        self.all_walls = pg.sprite.LayeredDirty()
        self.all_cells = pg.sprite.LayeredDirty()
        self.all_bases = pg.sprite.LayeredDirty()
        self.all_tanks = pg.sprite.LayeredDirty()
        self.all_projectiles = pg.sprite.LayeredDirty()

        self.id_dict = {}
        self.id_cnt = 0

    
    def get_tile_map(self, tile_map):
        self.tile_map = tile_map

    def spawn_base(self, place, player):

        base = obj.base.Base(place, player, self.tile_map, self.id_cnt)
        player.mist_matrix[place[1], place[0]] = 1
        self.all_bases.add(base)
        self.id_dict[self.id_cnt] = base
        self.id_cnt += 1 
        return base

    def spawn_tank(self, place, player):
        if player.spawn_tank_buff is None:
            print("пиздос где имг танк этот")
            exit()
        if player.base is None:
            print("ну ахуеть и где база")
            exit()
        spawn_distance = ((int(player.base.x) / len_cell - place[0]) ** 2 + 
                        (int(player.base.y) / len_cell - place[1]) ** 2) ** 0.5
        if player.resources < player.spawn_tank_buff.resource or player.exp < player.spawn_tank_buff.exp:
            pass
        elif spawn_distance > max_spawn_distance:
            pass
        else:

            tank = obj.tank.Tank(place, 1, player.spawn_tank_buff.ttc, player, self.tile_map, self.id_cnt)
            player.resources -= player.spawn_tank_buff.resource
            player.spawn_tank_buff = None
            self.all_tanks.add(tank)
            self.id_dict[self.id_cnt] = tank
            self.id_cnt += 1 
            return tank
        
        return None

    def spawn_projectile(self, player, world_mouse_pos):
        projectile = player.selected_tank.shot(self.all_projectiles, world_mouse_pos, 
                         obj.projectile.Projectile, self.id_cnt)
        self.id_dict[self.id_cnt] = projectile
        self.id_cnt += 1
        return projectile

    def move_tank(self):