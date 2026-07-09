import pygame as pg
import numpy as np

from ..core.scene import Scene
from .. import core, data, obj, ui, utils
from ..core.settings import *
from ..core.game import Game
from ..utils.functions import collidespritepoint, get_cell_mouse_pos, get_world_mouse_pos

class GameScene(Scene):
    

    def __init__(self, game: Game):
        super().__init__(game)
        
        # Состояния
        self.curtain_is_raisen = False

        self.is_spawning_base = True
        self.is_spawning_tank = False

        # UI на карте
        # self.damage_panel = None
        self.cell_border = ui.cell_border.CellBorder(0,0)

        self.all_cell_borders = pg.sprite.LayeredDirty()
        

        # Группы
        self.all_world_sprites = pg.sprite.LayeredDirty(_time_threshold = float("inf"))
        self.all_walls = pg.sprite.LayeredDirty()
        self.all_cells = pg.sprite.LayeredDirty()
        self.all_bases = pg.sprite.LayeredDirty()
        self.all_tanks = pg.sprite.LayeredDirty()
        self.all_projectiles = pg.sprite.LayeredDirty()
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
        self.active_player = 0

        # UI экран
        self.button_turn_switch = ui.uipanel.UIPanel(SW*15/16 - SW/16, SH*15/16 - SH/16, SW*1/8, SH*1/8, (0,255,255), 1, (255,128,0), 5)
        # self.all_buttons.add(self.button_turn_switch)
        self.all_UI.add(self.button_turn_switch)

        self.panel_resources = ui.uipanel.UIPanel(SW/2, SH*3/80, SW*15/64, SH*8/80, (128,128,128), 1, select_color, int(SW*2/1280)) # select_color не объявлен
        self.panel_cnt_turns = ui.uipanel.UIPanel(SW*15/16, SH*13.5/16, SW*1/8, SH*1/16, (128,128,128), 1, (255,128,0), int(SW*5/1280))
        self.panel_under_hp = ui.uipanel.UIPanel(SW/64, SH/2, SW/32, SH/2, (255,255,255), 1, (255,128,0), int(SW*5/1280))
        self.all_UI.add(self.panel_resources, self.panel_cnt_turns, self.panel_under_hp)

        # Генерация карты
        self.tile_map = data.maps.squares.tile_map.copy() # тайловая карта - по сетке

        utils.functions.builder(self.tile_map, obj.cell.Cell, 0, self.all_cells, self.all_world_sprites, self.map_objs_matrix)
        utils.functions.builder(self.tile_map, obj.wall.Wall, 1, self.all_walls, self.all_world_sprites, self.map_objs_matrix)

        virtual_screen_size = map_len_cells * len_cell
        self.map_screen = pg.Surface((virtual_screen_size, virtual_screen_size))
        self.background = self.map_screen.copy()
        self.all_cells.draw(self.background, self.background)
        self.all_walls.draw(self.background, self.background)

        # Игроки
        self.players: list[core.player.Player] = []
        for i in range(QNT_PLAYERS):
            self.players.append(core.player.Player(i, INITIAL_RESOURCES))
        self.cur_player_id = 0
        self.cur_player = self.players[self.cur_player_id]

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
                
                # Клетки
                cell_mouse_pos = get_cell_mouse_pos(self.cur_player, event.pos, len_cell)
                
                self.cell_border.goto(cell_mouse_pos)
                self.cell_border.dirty = 1

                self.cur_player.selected_tank = None
                self.selected_cell = self.tile_map[cell_mouse_pos[1], cell_mouse_pos[0]]

                if self.selected_cell == data.maps.ID_TANK:
                    for tank in self.cur_player.tanks:
                        if tank.place == cell_mouse_pos:
                            self.cur_player.selected_tank = tank
                            break

                elif self.selected_cell == data.maps.ID_BASE:
                    self.market = ui.market.Market(self, self.cur_player)

            # Состояния
            elif self.selected_cell is not None:
                match self.selected_cell:
                    # Выбран танк
                    case data.maps.ID_TANK:
                        if self.cur_player.selected_tank is None:
                            print("бля пиздец и где танк")
                            exit()
                        if event.type == pg.KEYDOWN:
                            if event.key == pg.K_SPACE:
                                self.cur_player.selected_tank.shot(self.all_projectiles, self.all_world_sprites, 
                                                                   get_world_mouse_pos(self.cur_player, pg.mouse.get_pos()), 
                                                                   obj.projectile.Projectile)
                            elif event.key == pg.K_q:
                                self.tile_map[self.cur_player.selected_tank.place[1], self.cur_player.selected_tank.place[0]] = 0
                                self.cur_player.selected_tank.kill()
                                self.cur_player.selected_tank = None
                                self.cur_player.mist_matrix = utils.functions.mist_doting3000(self.cur_player.tanks,
                                                                                        self.cur_player.base, self.map_objs_matrix, self.all_tanks,
                                                                                        self.cur_player, self.cur_player.team)
                            else:
                                self.cur_player.selected_tank.move(event.key)
                                self.cell_border.goto(self.cur_player.selected_tank.place)
                                self.cell_border.dirty = 1
                               
                                self.cur_player.mist_matrix = utils.functions.mist_doting3000(
                                    self.cur_player.tanks, self.cur_player.base, self.map_objs_matrix, self.all_tanks, self.all_bases, self.cur_player.team)


    def update(self):
        for tank in self.all_tanks:
            tank.draw_stats(self.cur_player.team)
        if self.selected_cell in (None, data.maps.ID_CELL, data.maps.ID_WALL):
            self.cur_player.move(pg.key.get_pressed())
            
        for projectile in self.all_projectiles:
            damage = projectile.update(self.all_walls, self.all_tanks, self.cur_player.tanks, self.all_bases, self.map_objs_matrix)
            if damage != 0:
                damage_panel = ui.damage_panel.DamagePanel(projectile.x, projectile.y, SW/24,
                                            SH/32, (255, 255, 255), 1, (0,0,0), 4, DAMAGE_PANEL_TIMELIVE, damage, projectile.team)
                self.all_damage_panels.add(damage_panel)
                self.all_world_sprites.add(damage_panel)
        self.all_damage_panels.update()
                
                
    def display(self, screen: pg.Surface):
        if self.curtain_is_raisen:
            screen.fill((66, 66, 66))
            return
        
        # Рисуется карта
        self.all_world_sprites.draw(self.map_screen, self.background)
        # self.all_buttons.draw(screen, self.background)

        dest = (-self.cur_player.cam_pos[0], -self.cur_player.cam_pos[1] )
        screen.fill((0,0,0))
        screen.blit(self.map_screen, dest)

        # UI
        self.all_UI.draw(screen)

        panel_hp_bar = ui.uipanel.UIPanel(SW/64+1, (SH*(1/4+5/800)) + SH*(1/4-5/800)*(self.cur_player.hp/base_hp), SW/32 - SW*10/1280-1, (SH/2 - SW*10/1280)*(self.cur_player.hp/base_hp),
                                            (128+(team_to_color[self.cur_player.team][0]-128)*(self.cur_player.hp/base_hp),
                                             128+(team_to_color[self.cur_player.team][1]-128)*(self.cur_player.hp/base_hp),
                                             128+(team_to_color[self.cur_player.team][2]-128)*(self.cur_player.hp/base_hp)), 0, 0, 0)
        panel_hp_bar.draw(screen)

        text_turns = font48.render(f"Turn: {self.cnt_rounds//QNT_PLAYERS + 1}", True, team_to_color[self.cur_player.team])
        text_resouces = font48.render(f"Resources : {self.cur_player.resources}", True, team_to_color[self.cur_player.team])
        text_exp = font48.render(f"Сapture : {self.cur_player.exp}", True, team_to_color[self.cur_player.team])
        screen.blit(text_turns, (SW*14/16 + SW*2/256, SH*14/16 - SW/32))
        screen.blit(text_resouces, (SW/2-SW*7/64, 0))
        screen.blit(text_exp, (SW/2-SW*7/64, SH*3/80))

        if self.market is not None:
            self.market.draw(screen)

    def close_market(self):
        self.market = None

    def change_turn(self):
        if self.cnt_rounds >= QNT_PLAYERS:
            self.cur_player.exp += utils.functions.cell_distribution(QNT_PLAYERS, self.cur_player.team, self.cur_player.tanks)
            self.cur_player.resources += utils.functions.resources_profit(len(self.cur_player.tanks.sprites()))
        self.cur_player.tanks.update()
    
        for tank in self.cur_player.tanks:
            tank.drowed_stats = False
        
        self.active_player = (self.active_player + 1) % QNT_PLAYERS
        self.cur_player = self.players[self.active_player]
        self.cur_player.mist_matrix = utils.functions.mist_doting3000(self.cur_player.tanks, self.cur_player.base,
                                                                    self.map_objs_matrix, self.cur_player.tanks, self.all_bases, self.cur_player.team)
        
        self.close_market()
        self.curtain_is_raisen = True
        self.all_cell_borders.empty()
        self.all_damage_panels.empty()
        self.cnt_rounds += 1

        if self.cur_player.base is None:
            self.is_spawning_base = True
