import pygame as pg
import numpy as np

from ..core.scene import Scene
from ..core.player import Player
from .. import core, data, obj, ui, utils
from ..core.settings import *
from ..core.game import Game
from ..utils.functions import collidespritepoint, get_cell_mouse_pos, get_world_mouse_pos

# def spawn_base(place, player, tile_map):
#     base = obj.base.Base(place, player, tile_map)
#     player.mist_matrix[place[1], place[0]] = 1
#     return base

# def spawn_tank(place, player: Player, tile_map):
#     if player.spawn_tank_buff is None:
#         print("пиздос где имг танк этот")
#         exit()
#     if player.base is None:
#         print("ну ахуеть и где база")
#         exit()
#     spawn_distance = ((int(player.base.x) / len_cell - place[0]) ** 2 + 
#                     (int(player.base.y) / len_cell - place[1]) ** 2) ** 0.5
#     if player.resources < player.spawn_tank_buff.resource or player.exp < player.spawn_tank_buff.exp:
#         pass
#     elif spawn_distance > max_spawn_distance:
#         pass
#     else:

#         tank = obj.tank.Tank(place, 1, player.spawn_tank_buff.ttc, player, tile_map)
#         player.resources -= player.spawn_tank_buff.resource
#         player.spawn_tank_buff = None
#         return tank
    
#     return None


class GameScene(Scene):

    button_turn_switch = ui.uipanel.UIPanel(SW*15/16 - SW/16, SH*15/16 - SH/16, SW*1/8, SH*1/8, (0,255,255), 1, (255,128,0), 5)
    
    def __init__(self, game: Game):
        super().__init__(game)

        self.game_manager = core.game_manager.GameManager()

        # Игроки
        self.players: list[core.player.Player] = []
        for i in range(QNT_PLAYERS):
            self.players.append(core.player.Player(i, INITIAL_RESOURCES))
        self.cur_player_id = 0
        self.cur_player = self.players[self.cur_player_id]


        
        # Состояния
        self.curtain_is_raisen = False

        self.is_spawning_base = True
        self.is_spawning_tank = False

        # UI на карте
        # self.damage_panel = None
        self.cell_border = ui.cell_border.CellBorder(0,0)
        self.cell_border.visible = False
        

        # Группы
        self.all_world_sprites = pg.sprite.LayeredDirty(_time_threshold = float("inf")) #_time_threshold = float("inf")
        # self.all_walls = pg.sprite.LayeredDirty()
        # self.all_cells = pg.sprite.LayeredDirty()
        # self.all_bases = pg.sprite.LayeredDirty()
        # self.all_tanks = pg.sprite.LayeredDirty()
        self.all_cell_borders = pg.sprite.LayeredDirty()
        # self.all_projectiles = pg.sprite.LayeredDirty()
        self.map_objs_matrix = np.empty((map_len_cells, map_len_cells), dtype=object)
        # self.all_buttons = pg.sprite.LayeredDirty()
        self.all_UI = pg.sprite.LayeredDirty()
        self.all_damage_panels = pg.sprite.LayeredDirty()

        # Первичное заполнение групп
        self.all_cell_borders.add(self.cell_border)
        self.all_world_sprites.add(self.cell_border)
        
        # Данные
        self.market: ui.market.Market | None = None 
        self.selected_cell = None
        self.cnt_rounds = 0
        # self.cur_player_id = 0

        # UI экран
        self.panel_cnt_turns = ui.panel_cnt_turns.PanelResourses(SW*15/16 - SW*1/16, SH*13.5/16 - SH*1/32, SW*1/8, SH*1/16, (128,128,128), 1, (255,128,0), int(SW*5/1280),
                                                                 self.cur_player, self)
        self.panel_resources = ui.panel_resourses.PanelResourses(SW/2 - SW*15/128, SH*3/80 - SH*8/160, SW*15/64, SH*8/80, (128,128,128), 1, color_select, int(SW*2/1280),
                                                                  self.cur_player)
        self.base_hp_bar =  ui.base_hp_bar.BaseHpBar(SW/64 - SW/64, SH/2 - SH/4, SW/32, SH/2, (255,255,255), 1, (255,128,0), int(SW*5/1280), self.cur_player)
        self.panel_for_spawn_tank = ui.panel_for_spawn_tank.PanelForSpawnTank(0, SH*0.75, SW*0.25, SH*0.25, (128,128,128), 1, (255,128,0), 5)
        self.all_UI.add(self.button_turn_switch, self.panel_resources, self.panel_cnt_turns, self.base_hp_bar, self.panel_for_spawn_tank)

        # Генерация карты
        self.tile_map = data.maps.squares.tile_map.copy() # тайловая карта - по сетке

        utils.functions.builder(self.tile_map, obj.cell.Cell, data.maps.ID_VOID, self.game_manager.all_cells, self.all_world_sprites, self.map_objs_matrix)
        utils.functions.builder(self.tile_map, obj.wall.Wall, data.maps.ID_WALL, self.game_manager.all_walls, self.all_world_sprites, self.map_objs_matrix)

        self.game_manager.get_tile_map(self.tile_map)

        virtual_screen_size = map_len_cells * len_cell
        self.map_screen = pg.Surface((virtual_screen_size, virtual_screen_size))
        self.background = self.map_screen.copy()
        self.game_manager.all_cells.draw(self.background, self.background)
        self.game_manager.all_walls.draw(self.background, self.background)


    def handle_events(self, all_events: list[pg.event.Event]):
        for event in all_events:
            # Глобальные развилки
            if event.type == pg.QUIT:
                self.game.stop()

            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                from .main_menu_scene import MainMenuScene
                self.game.set_scene(MainMenuScene)

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
                if collidespritepoint(self.button_turn_switch, event.pos):
                    if not self.is_spawning_base:
                        self.change_turn()
                
                # Нажатия на клетки
                else:
                    cell_mouse_pos = get_cell_mouse_pos(self.cur_player, event.pos, len_cell)
                    self.cell_border.goto(cell_mouse_pos)
                    
                    self.cur_player.selected_tank = None
                    self.selected_cell = self.game_manager.tile_map[cell_mouse_pos[1], cell_mouse_pos[0]]

                    if self.selected_cell == data.maps.ID_TANK:
                        for tank in self.cur_player.tanks:
                            if tuple(tank.place) == cell_mouse_pos:
                                self.cur_player.selected_tank = tank
                                break

                    elif self.selected_cell == data.maps.ID_BASE:
                        if self.cur_player.base is not None:
                            if tuple(self.cur_player.base.place) == cell_mouse_pos:
                                self.market = ui.market.Market(self, self.cur_player)
                    
                    elif self.selected_cell == data.maps.ID_VOID:
                        # Спавн базы
                        if self.is_spawning_base:
                            base = self.game_manager.spawn_base(self.cell_border.place, self.cur_player)
                            self.all_world_sprites.add(base)

                            self.selected_cell = None
                            self.cell_border.visible = False

                            self.is_spawning_base = False
                        
                        # Спавн танка
                        elif self.is_spawning_tank:
                            tank = self.game_manager.spawn_tank(self.cell_border.place, self.cur_player)
                            if tank is not None:
                                self.all_world_sprites.add(tank)

                                self.cur_player.mist_matrix = utils.functions.mist_doting3000(self.cur_player.tanks, self.cur_player.base, self.map_objs_matrix, 
                                                                                            self.game_manager.all_tanks, self.game_manager.all_bases, self.cur_player.team)
                                
                                self.selected_cell = None
                                self.cell_border.visible = False

                                self.is_spawning_tank = False

            # Изменения выбранной клетки
            if self.selected_cell is not None:
                # Управление танком
                if self.selected_cell == data.maps.ID_TANK:
                    if self.cur_player.selected_tank is None:
                        pass
                    elif event.type == pg.KEYDOWN:
                        if event.key == pg.K_SPACE:
                            projectile = self.game_manager.spawn_projectile(self.cur_player, get_world_mouse_pos(self.cur_player, pg.mouse.get_pos()))
                            self.all_world_sprites.add(projectile)

                        elif event.key == pg.K_q:
                            self.tile_map[self.cur_player.selected_tank.place[1], self.cur_player.selected_tank.place[0]] = 0
                            self.cur_player.selected_tank.kill()
                            self.cur_player.selected_tank = None
                            self.cur_player.mist_matrix = utils.functions.mist_doting3000(self.cur_player.tanks,
                                                                                    self.cur_player.base, self.map_objs_matrix, self.game_manager.all_tanks,
                                                                                    self.game_manager.all_bases, self.cur_player.team)
                        else:
                            
                            self.cur_player.selected_tank.move(event.key) 
                            self.cell_border.goto(self.cur_player.selected_tank.place)
                        
                            self.cur_player.mist_matrix = utils.functions.mist_doting3000(
                                self.cur_player.tanks, self.cur_player.base, self.map_objs_matrix, self.game_manager.all_tanks, self.game_manager.all_bases, self.cur_player.team)

    def update(self):
        
        for tank in self.game_manager.all_tanks:
            tank.draw_stats(self.cur_player.team)
        for base in self.game_manager.all_bases:
            base.draw_stats()

        self.panel_cnt_turns.update(self.cur_player, self)
        self.panel_resources.update(self.cur_player)
        self.base_hp_bar.update(self.cur_player)
        
        if self.selected_cell in (None, data.maps.ID_VOID, data.maps.ID_WALL):
            self.cur_player.move(pg.key.get_pressed())
            
        for projectile in self.game_manager.all_projectiles:
            damage = projectile.update(self.game_manager.all_walls, self.game_manager.all_tanks, self.cur_player.tanks, self.game_manager.all_bases, self.map_objs_matrix)
            if damage != 0:
                damage_panel = ui.damage_panel.DamagePanel(projectile.x, projectile.y, SW/24,
                                            SH/32, (255, 255, 255), 1, (0,0,0), 4, DAMAGE_PANEL_TIMELIVE, damage, projectile.team)
                self.all_damage_panels.add(damage_panel)
                self.all_world_sprites.add(damage_panel)
        self.all_damage_panels.update()
        # self.all_world_sprites.update()
                
                
    def display(self, screen: pg.Surface):
        if self.curtain_is_raisen:
            screen.fill((66, 66, 66))
            return
        
        # Рисуется карта
        self.all_world_sprites.draw(self.map_screen, self.background)
        # self.all_damage_panels.draw(self.map_screen, self.background)

        dest = (-self.cur_player.cam_pos[0], -self.cur_player.cam_pos[1] )
        screen.fill((0,0,0))
        screen.blit(self.map_screen, dest)

        # UI
        self.all_UI.draw(screen)

        # text_turns = font48.render(f"Turn: {self.cnt_rounds//QNT_PLAYERS + 1}", True, team_to_color[self.cur_player.team])
        # text_resouces = font48.render(f"Resources : {self.cur_player.resources}", True, team_to_color[self.cur_player.team])
        # text_exp = font48.render(f"Сapture : {self.cur_player.exp}", True, team_to_color[self.cur_player.team])
        # screen.blit(text_turns, (SW*14/16 + SW*2/256, SH*14/16 - SW/32))
        # screen.blit(text_resouces, (SW/2-SW*7/64, 0))
        # screen.blit(text_exp, (SW/2-SW*7/64, SH*3/80))

        if self.market is not None:
            self.market.draw(screen)

    def close_market(self):
        self.market = None

    def change_turn(self):
        if self.cnt_rounds >= QNT_PLAYERS:
            self.cur_player.exp += utils.functions.cell_distribution(QNT_PLAYERS, self.cur_player.team, self.cur_player.tanks)
            self.cur_player.resources += utils.functions.resources_profit(len(self.cur_player.tanks.sprites()))
        self.cur_player.tanks.update()
        
        self.close_market()
        self.selected_cell = None
        self.cell_border.visible = False
        
        self.all_cell_borders.empty()
        self.all_world_sprites.remove(self.all_damage_panels)
        self.all_damage_panels.empty()

        self.curtain_is_raisen = True
        self.cnt_rounds += 1
    
        for tank in self.cur_player.tanks:
            tank.drowed_stats = False
        
        self.cur_player_id = (self.cur_player_id + 1) % QNT_PLAYERS
        self.cur_player = self.players[self.cur_player_id]
        self.cur_player.mist_matrix = utils.functions.mist_doting3000(self.cur_player.tanks, self.cur_player.base, self.map_objs_matrix, 
                                                                      self.game_manager.all_tanks, self.game_manager.all_bases, self.cur_player.team)
        

        if self.cur_player.base is None:
            self.is_spawning_base = True
