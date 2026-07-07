import pygame as pg
import numpy as np

from ..core.scene import Scene
from .. import core, data, obj, ui, utils
from ..core.settings import *
from ..core.game import Game
from ..utils.functions import collidespritepoint, get_cell_mouse_pos

class GameScene(Scene):

    def __init__(self, game: Game):
        super().__init__(game)
        
        # Состояния
        self.curtain_is_raisen = False

        self.is_spawning_base = False
        self.is_spawning_tank = False

        # UI на карте
        self.damage_panel = None
        self.cell_border = ui.cell_border.CellBorder(0,0)

        self.all_cell_borders = pg.sprite.LayeredDirty()
        

        # Группы
        self.all_sprites = pg.sprite.LayeredDirty(_time_threshold = float("inf"))
        self.all_walls = pg.sprite.LayeredDirty()
        self.all_cells = pg.sprite.LayeredDirty()
        self.all_bases = pg.sprite.LayeredDirty()
        self.map_matrix = np.empty((map_len_cells, map_len_cells), dtype=object)
        self.all_buttons = pg.sprite.LayeredDirty()

        # Первичное заполнение групп
        self.all_cell_borders.add(self.cell_border)
        self.all_sprites.add(self.cell_border)
        
        # Данные
        self.market: ui.market.Market | None = None 
        self.selected_cell = None
        self.cnt_rounds = 0
        self.active_player = 0

        # UI экран
        self.button_turn_switch = ui.uipanel.UIPanel(SW*15/16 - SW/16, SH*15/16 - SH/16, SW*1/8, SH*1/8, (0,255,255), 1, (255,128,0), 5)
        self.button_turn_switch.dirty = 2
        self.all_buttons.add(self.button_turn_switch)

        self.panel_resources = ui.uipanel.UIPanel(SW/2, SH*3/80, SW*15/64, SH*8/80, (128,128,128), 1, select_color, int(SW*2/1280))
        self.panel_cnt_turns = ui.uipanel.UIPanel(SW*15/16, SH*13.5/16, SW*1/8, SH*1/16, (128,128,128), 1, (255,128,0), int(SW*5/1280))
        self.panel_hp = ui.uipanel.UIPanel(SW/64, SH/2, SW/32, SH/2, (255,255,255), 1, (255,128,0), int(SW*5/1280))
        
        # Генерация карты
        self.tile_map = data.maps.squares.tile_map.copy() # тайловая карта - по сетке

        utils.functions.builder(self.tile_map, obj.cell.Cell, 0, self.all_cells, self.all_sprites, self.map_matrix)
        utils.functions.builder(self.tile_map, obj.wall.Wall, 1, self.all_walls, self.all_sprites, self.map_matrix)

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
            # Глобальные
            if event.key == pg.K_ESCAPE and event.type == pg.KEYDOWN:
                from .main_menu_scene import MainMenuScene
                self.game.set_scene(MainMenuScene)

            if self.market is not None:
                self.market.handle_event(event)
            
            elif self.curtain_is_raisen:
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    self.curtain_is_raisen = False
            
            else:
                # Выбор
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
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

                    if self.selected_cell == 2:
                        for tank in self.cur_player.tanks:
                            if tank.place == cell_mouse_pos:
                                self.cur_player.selected_tank = tank
                                break

                    elif self.selected_cell == 3:
                        self.market = ui.market.Market(self, self.cur_player)


    def update(self):
        if self.selected_cell in (0, 1):
            self.cur_player.move(pg.key.get_pressed())

    def display(self, screen: pg.Surface):
        self.all_buttons.draw(screen, self.background)


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
                                                                    self.map_matrix, self.cur_player.tanks, self.all_bases, self.cur_player.team)
        if damage_text_timelive > 0:
            damage_text_timelive = 1
        if select_cell is not None:
            select_cell.kill()
            select_cell = None
        self.cur_player.tanks = None
        selected_tank = None
        self.curtain_is_raisen = True
        self.close_market()
        self.all_cell_borders.empty()
        self.cnt_rounds += 1
