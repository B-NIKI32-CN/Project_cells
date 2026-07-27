from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..core.scene_manager import SceneManager


import pygame as pg
import numpy as np

from ..core.settings import *
from ..data import maps
from ..core.game_manager import GameManager
from ..core.scene import Scene
from ..obj.cell import Cell
from ..obj.wall import Wall
from ..ui.base_hp_bar import BaseHpBar
from ..ui.cell_border import CellBorder
from ..ui.damage_panel import DamagePanel
from ..ui.market import Market
from ..ui.panel_for_spawn_tank import PanelForSpawnTank
from ..ui.panel_resourses import PanelResourses
from ..ui.panel_cnt_turns import PanelCntTurns
from ..ui.button_turn_switch import ButtonTurnSwitch
from ..utils.functions import collidespritepoint, get_cell_mouse_pos, get_world_mouse_pos, builder, mist_doting3000

from ..net import signals_collector
from ..net.our_net import SoftServer


class GameScene(Scene):
    
    tank_move_keys = {
        pg.K_w: "forward", 
        pg.K_s: "backward", 
        pg.K_a: "left", 
        pg.K_d: "right"
    }
    
    def __init__(self, scene_manager: SceneManager):
        super().__init__(scene_manager)

        self.scene_manager = scene_manager
        self.game_manager = GameManager(self.scene_manager.max_qnt_players)

        # Игрок, который обрабатывается сценой
        if self.scene_manager.net_module is not None:
            self.active_player = self.game_manager.players[self.scene_manager.local_player_id]
        else:
            self.active_player = self.game_manager.cur_player
        
        self.is_active_player_turn = (self.active_player.team == self.game_manager.cur_player_id)

        # Состояния
        self.curtain_is_raisen = False

        self.is_spawning_base = True
        self.is_spawning_tank = False

        self.cam_is_blocked = False

        # UI на карте
        self.cell_border = CellBorder(0,0)
        self.close_select_cell()
        

        # Группы
        self.all_world_sprites = pg.sprite.LayeredDirty(_time_threshold = float("inf")) #_time_threshold = float("inf")
        self.all_cell_borders = pg.sprite.LayeredDirty()
        self.map_objs_matrix = np.empty((map_len_cells, map_len_cells), dtype=object)
        self.all_UI = pg.sprite.LayeredDirty()
        self.all_damage_panels = pg.sprite.LayeredDirty()

        # Первичное заполнение групп
        self.all_cell_borders.add(self.cell_border)
        self.all_world_sprites.add(self.cell_border)
        
        # Данные
        self.market: Market | None = None 
        self.selected_cell = None
        # self.cur_player_id = 0

        # UI экран
        self.panel_cnt_turns = PanelCntTurns(SW*15/16 - SW*1/16, SH*13.5/16 - SH*1/32, SW*1/8, SH*1/16, (128,128,128), 1, (255,128,0), int(SW*5/1280),
                                                                 self.active_player, self.game_manager.cur_player_id, self.scene_manager.max_qnt_players)
        self.panel_resources = PanelResourses(SW/2 - SW*15/128, SH*3/80 - SH*8/160, SW*15/64, SH*8/80, (128,128,128), 1, color_select, int(SW*2/1280),
                                                                  self.active_player)
        self.base_hp_bar = BaseHpBar(SW/64 - SW/64, SH/2 - SH/4, SW/32, SH/2, (255,255,255), 1, (255,128,0), int(SW*5/1280), self.active_player)
        self.panel_for_spawn_tank = PanelForSpawnTank(0, SH - len_cell*2,  len_cell*2, len_cell*2, (128,128,128), 1, (255,128,0), 5)
        self.button_turn_switch = ButtonTurnSwitch(self)

        self.all_UI.add(self.button_turn_switch, self.panel_resources, self.panel_cnt_turns, self.base_hp_bar, self.panel_for_spawn_tank)

        # Генерация карты
        self.tile_map = maps.memorial.tile_map.copy() # тайловая карта - по сетке

        builder(self.tile_map, Cell, maps.ID_VOID, self.game_manager.all_cells, self.all_world_sprites, self.map_objs_matrix)
        builder(self.tile_map, Wall, maps.ID_WALL, self.game_manager.all_walls, self.all_world_sprites, self.map_objs_matrix)

        self.game_manager.set_tile_map(self.tile_map)

        virtual_screen_size = map_len_cells * len_cell
        self.map_screen = pg.Surface((virtual_screen_size, virtual_screen_size))
        self.background = self.map_screen.copy()
        self.game_manager.all_cells.draw(self.background, self.background)
        self.game_manager.all_walls.draw(self.background, self.background)


    def handle_events(self, all_events: list[pg.event.Event]):
        
        for event in all_events:
            # Глобальные развилки
            if event.type == pg.QUIT:
                self.scene_manager.stop()

            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                from .main_menu_scene import MainMenuScene
                self.scene_manager.set_scene(MainMenuScene)

            if self.market is not None:
                self.market.handle_event(event)
                continue
            
            elif self.curtain_is_raisen:
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    self.curtain_is_raisen = False
                continue
            
            # Нажатия мыши
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                # UI
                if collidespritepoint(self.button_turn_switch, event.pos) and self.is_active_player_turn:
                    if not self.is_spawning_base:
                        self.change_turn()
                elif collidespritepoint(self.panel_for_spawn_tank, event.pos):
                    self.panel_for_spawn_tank.draw_tank(None)
                    self.active_player.spawn_tank_buff = None
                    self.is_spawning_tank = False
                
                # Нажатия на клетки
                else:
                    self.close_select_cell()

                    cell_mouse_pos = get_cell_mouse_pos(self.active_player, event.pos, len_cell)
                    self.cell_border.goto(cell_mouse_pos)
                    
                    self.active_player.selected_tank = None
                    self.selected_cell = self.game_manager.tile_map[cell_mouse_pos[1], cell_mouse_pos[0]]
            
                    # нажатие на танк
                    if self.selected_cell == maps.ID_TANK:
                        for tank in self.active_player.tanks:
                            if tuple(tank.place) == cell_mouse_pos:
                                self.active_player.selected_tank = tank
                                self.cam_is_blocked = True
                                break
                    
                    # открытие магазина
                    elif self.selected_cell == maps.ID_BASE:
                        if self.active_player.base is not None:
                            if tuple(self.active_player.base.place) == cell_mouse_pos:
                                self.market = Market(self, self.active_player)
                                self.close_select_cell()
                    
                    # нажатие на пустую клетку
                    elif self.selected_cell == maps.ID_VOID and self.is_active_player_turn:
                        # Спавн базы
                        if self.is_spawning_base:
                            base = self.game_manager.spawn_base(self.cell_border.place, self.all_world_sprites)

                            self.close_select_cell()

                            self.is_spawning_base = False
                            
                            ### NET
                            if self.scene_manager.net_module is not None:
                                signal = signals_collector.spawn_base(tuple(base.place))
                                self.scene_manager.net_module.add(signal)
                        
                        # Спавн танка
                        elif self.is_spawning_tank:
                            if self.active_player.spawn_tank_buff is None:
                                print("блин где img_tank((")
                                exit()
                            tank = self.game_manager.spawn_tank(self.active_player.spawn_tank_buff.id, self.cell_border.place, self.all_world_sprites)
                            if tank is not None:
                                self.panel_for_spawn_tank.draw_tank(None)

                                self.active_player.mist_matrix = mist_doting3000(self.active_player.tanks, self.active_player.base, self.map_objs_matrix, 
                                                                                            self.game_manager.all_tanks, self.game_manager.all_bases, self.active_player.team)
                                
                                self.close_select_cell()

                                self.is_spawning_tank = False

                                ### NET
                                if self.scene_manager.net_module is not None:
                                    signal = signals_collector.spawn_tank(tank.ttc["id"], tuple(tank.place))
                                    self.scene_manager.net_module.add(signal)

            # Изменения выбранной клетки
            if self.selected_cell is not None:
                # Управление танком
                if self.selected_cell == maps.ID_TANK and self.is_active_player_turn:
                    if self.active_player.selected_tank is None:
                        pass
                    elif event.type == pg.KEYDOWN:
                        if event.key == pg.K_SPACE:
                            world_mouse_pos = get_world_mouse_pos(self.active_player, pg.mouse.get_pos())
                            projectile = self.game_manager.spawn_projectile(self.active_player.selected_tank.id, world_mouse_pos, self.all_world_sprites)
                            
                            
                            ### NET
                            if self.scene_manager.net_module is not None:
                                signal = signals_collector.spawn_projectile(self.active_player.selected_tank.id, world_mouse_pos)
                                self.scene_manager.net_module.add(signal)

                        elif event.key in self.tank_move_keys:
                            direction = self.tank_move_keys[event.key]
                            is_move = self.game_manager.move_tank(self.active_player.selected_tank.id, direction)

                            self.cell_border.goto(self.active_player.selected_tank.place)
                            self.active_player.mist_matrix = mist_doting3000(
                                self.active_player.tanks, self.active_player.base, self.map_objs_matrix, self.game_manager.all_tanks, self.game_manager.all_bases, self.active_player.team)

                            ### NET
                            if self.scene_manager.net_module is not None:
                                if is_move:
                                    signal = signals_collector.tank_move(self.active_player.selected_tank.id, direction)
                                    self.scene_manager.net_module.add(signal)


    def update(self):
        
        for tank in self.game_manager.all_tanks:
            tank.draw_stats(self.active_player.team)
        for base in self.game_manager.all_bases:
            base.draw_stats()

        self.panel_cnt_turns.update(self.active_player, self.game_manager.cur_player_id, self.scene_manager.max_qnt_players)
        self.panel_resources.update(self.active_player)
        self.base_hp_bar.update(self.active_player)
        self.button_turn_switch.update()
        
        # if self.selected_cell in (None, maps.ID_VOID, maps.ID_WALL):
        if not self.cam_is_blocked:
            self.active_player.move(pg.key.get_pressed())
            
        for projectile in self.game_manager.all_projectiles:
            damage = projectile.update(self.game_manager.all_walls, self.game_manager.all_tanks, self.game_manager.cur_player.tanks, self.game_manager.all_bases, self.map_objs_matrix)
            if damage != 0:
                damage_panel = DamagePanel(projectile.x, projectile.y, SW/24,
                                            SH/32, (255, 255, 255), 1, (0,0,0), 4, DAMAGE_PANEL_TIMELIVE, damage, projectile.team)
                self.all_damage_panels.add(damage_panel)
                self.all_world_sprites.add(damage_panel)
        self.all_damage_panels.update()

        ### NET
        if self.scene_manager.net_module is not None:
            json_signals = self.scene_manager.net_module.soft_recv()
            signals = signals_collector.decode_list(json_signals)

            for signal in signals:
                is_done = self.signal_processing(signal)
                if not is_done:
                    print(f"сигнал поганый: {signal}")
                elif isinstance(self.scene_manager.net_module, SoftServer):
                    self.scene_manager.net_module.add(signals_collector.encode(signal))

            self.scene_manager.net_module.soft_send()


    def display(self, screen: pg.Surface):
        if self.curtain_is_raisen:
            screen.fill((66, 66, 66))
            return
        
        # Рисуется карта
        self.all_world_sprites.draw(self.map_screen, self.background)

        dest = (-self.active_player.cam_pos[0], -self.active_player.cam_pos[1] )
        screen.fill((0,0,0))
        screen.blit(self.map_screen, dest)

        # UI
        self.all_UI.draw(screen)

        if self.market is not None:
            self.market.draw(screen)


    def change_turn(self):
        
        self.close_market()
        self.close_select_cell()
        
        self.all_cell_borders.empty()
        self.all_world_sprites.remove(self.all_damage_panels)
        self.all_damage_panels.empty()

        self.game_manager.change_turn()

        if self.scene_manager.net_module is None:
            self.curtain_is_raisen = True
            self.active_player = self.game_manager.cur_player
    
        for tank in self.active_player.tanks:
            tank.drowed_stats = False
        
        self.is_active_player_turn = (self.active_player.team == self.game_manager.cur_player_id)
        
        self.active_player.mist_matrix = mist_doting3000(self.active_player.tanks, self.active_player.base, self.map_objs_matrix, 
                                                                      self.game_manager.all_tanks, self.game_manager.all_bases, self.active_player.team)

        # if self.active_player.base is None:
        #     self.is_spawning_base = True

        ### NET
        if self.scene_manager.net_module is not None:
            signal = signals_collector.change_turn(self.game_manager.cur_player_id)
            self.scene_manager.net_module.add(signal)

    
    ### NET
    def signal_processing(self, signal: dict):
        if "global" not in signal: return False
        
        if signal["global"] == "game":

            if "namespase" not in signal: return False
            if "command" not in signal: return False

            if signal["namespase"] == "spawn":

                if "args" not in signal: return False

                if signal["command"] == "base":

                    if "pos" not in signal["args"] or (len(signal["args"]["pos"]) != 2): return False
                    if not self.is_active_player_turn:
                        self.game_manager.spawn_base(signal["args"]["pos"], self.all_world_sprites)
                        self.active_player.mist_matrix = mist_doting3000(self.active_player.tanks, self.active_player.base, self.map_objs_matrix, 
                                                                                              self.game_manager.all_tanks, self.game_manager.all_bases, self.active_player.team)
                    return True

                if signal["command"] == "tank":

                    if "pos" not in signal["args"] or (len(signal["args"]["pos"]) != 2): return False
                    if "tank_type_id" not in signal["args"]: return False
                    if not self.is_active_player_turn:
                        self.game_manager.spawn_tank(signal["args"]["tank_type_id"], signal["args"]["pos"], self.all_world_sprites)
                        self.active_player.mist_matrix = mist_doting3000(self.active_player.tanks, self.active_player.base, self.map_objs_matrix, 
                                                                                              self.game_manager.all_tanks, self.game_manager.all_bases, self.active_player.team)
                    return True

                if signal["command"] == "projectile":

                    if "direction" not in signal["args"] or (len(signal["args"]["direction"]) != 2): return False
                    if "tank_id" not in signal["args"]: return False
                    if not self.is_active_player_turn:
                        self.game_manager.spawn_projectile(signal["args"]["tank_id"], signal["args"]["direction"], self.all_world_sprites)
                        self.active_player.mist_matrix = mist_doting3000(self.active_player.tanks, self.active_player.base, self.map_objs_matrix, 
                                                                                              self.game_manager.all_tanks, self.game_manager.all_bases, self.active_player.team)
                    return True

            if signal["namespase"] == "mutate":

                if "args" not in signal: return False

                if signal["command"] == "move":
                    if "direction" not in signal["args"]: return False
                    if "tank_id" not in signal["args"]: return False
                    if not self.is_active_player_turn:
                        self.game_manager.move_tank(signal["args"]["tank_id"], signal["args"]["direction"])
                        self.active_player.mist_matrix = mist_doting3000(self.active_player.tanks, self.active_player.base, self.map_objs_matrix, 
                                                                                              self.game_manager.all_tanks, self.game_manager.all_bases, self.active_player.team)
                    return True
                
            if signal["namespase"] == "turn":

                if "args" not in signal: return False

                if signal["command"] == "change":

                    if "new_player_id" not in signal["args"]: return False
                    if self.game_manager.cur_player_id != signal["args"]["new_player_id"]:
                        self.game_manager.change_turn()

                        for tank in self.active_player.tanks:
                            tank.drowed_stats = False
                                                
                        self.is_active_player_turn = (self.active_player.team == self.game_manager.cur_player_id)
                                
                        self.active_player.mist_matrix = mist_doting3000(self.active_player.tanks, self.active_player.base, self.map_objs_matrix, 
                                                                                              self.game_manager.all_tanks, self.game_manager.all_bases, self.active_player.team)
                        
                    return True
                
        return False


    def close_market(self):
        self.market = None


    def close_select_cell(self):
        self.selected_cell = None
        self.cell_border.visible = 0
        self.cam_is_blocked = False
