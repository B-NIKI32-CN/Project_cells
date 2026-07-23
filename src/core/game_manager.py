import pygame as pg

from ..core.settings import *
from ..core.player import Player
from ..data.ttc import tank_types
from ..obj.base import Base
from ..obj.tank import Tank
from ..obj.projectile import Projectile
from ..utils.functions import cell_distribution, resources_profit


class GameManager():
    
    def __init__(self):

        self.all_walls = pg.sprite.LayeredDirty()
        self.all_cells = pg.sprite.LayeredDirty()
        self.all_bases = pg.sprite.LayeredDirty()
        self.all_tanks = pg.sprite.LayeredDirty()
        self.all_projectiles = pg.sprite.LayeredDirty()
        self.cnt_rounds = 0
        

        self.id_dict = {}
        self.id_cnt = 0

        self.players: list[Player] = []
        for i in range(QNT_PLAYERS):
            self.players.append(Player(i, INITIAL_RESOURCES))
        self.cur_player_id = 0
        self.cur_player = self.players[self.cur_player_id]

    
    def set_tile_map(self, tile_map):
        self.tile_map = tile_map

    def spawn_base(self, place, all_world_sprites):

        base = Base(place, self.cur_player, self.tile_map, self.id_cnt, self)
        self.cur_player.mist_matrix[place[1], place[0]] = 1
        self.all_bases.add(base)
        self.id_dict[self.id_cnt] = base
        self.id_cnt += 1 
        all_world_sprites.add(base)
        return base

    def spawn_tank(self, tank_type_id, place, all_world_sprites):

        if self.cur_player.base is None:
            print("ну ахуеть и где база")
            exit()

        ttc = tank_types[tank_type_id]
        spawn_distance = ((int(self.cur_player.base.x) / len_cell - place[0]) ** 2 + 
                        (int(self.cur_player.base.y) / len_cell - place[1]) ** 2) ** 0.5
        if self.cur_player.resources < ttc["resource"] or self.cur_player.exp < ttc["exp"]:
            pass
        elif spawn_distance > max_spawn_distance:
            pass
        else:

            
            tank = Tank(self.id_cnt, place, 1, ttc, self.cur_player, self)
            self.cur_player.resources -= ttc["resource"]
            self.cur_player.spawn_tank_buff = None
            self.all_tanks.add(tank)
            self.id_dict[self.id_cnt] = tank
            self.id_cnt += 1 
            all_world_sprites.add(tank)
            return tank
        
        return None

    def spawn_projectile(self, tank_id, world_mouse_pos, all_world_sprites):

        if not isinstance(self.id_dict[tank_id], Tank): return None
        projectile = self.id_dict[tank_id].shot(self.all_projectiles, world_mouse_pos, 
                                                Projectile, self.id_cnt, self)
        self.id_dict[self.id_cnt] = projectile
        self.id_cnt += 1
        all_world_sprites.add(projectile)
        return projectile

    def move_tank(self, tank_id, direction: str):
        if not isinstance(self.id_dict[tank_id], Tank): return None
        return self.id_dict[tank_id].move(direction)

    def delete_id(self, id):
        self.id_dict.pop(id)

    def change_turn(self):
        if self.cnt_rounds >= QNT_PLAYERS:
            self.cur_player.exp += cell_distribution(QNT_PLAYERS, self.cur_player.team, self.all_tanks)
            self.cur_player.resources += resources_profit(len(self.cur_player.tanks.sprites()))
        self.cnt_rounds += 1
        self.cur_player.tanks.update()
        print()
        print(self.cur_player_id)
        self.cur_player_id = (self.cur_player_id + 1) % QNT_PLAYERS
        print(self.cur_player_id)
        self.cur_player = self.players[self.cur_player_id]

