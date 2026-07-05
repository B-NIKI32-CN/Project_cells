import pygame as pg
import numpy as np

from ..core.scene import Scene
from .. import core, data, obj, ui, utils
from ..core.settings import *
from ..core.game import Game

class GameScene(Scene):

    def __init__(self, game: Game):
        super().__init__(game)
        
        # Состояния
        self.market_is_open = False
        self.spawning_tank = False
        self.curtain_is_raisen = False

        self.selected_cell = None

        # UI на карте
        self.damage_panel = None
        self.cell_border = None

        # Данные
        self.all_sprites = pg.sprite.LayeredDirty(_time_threshold = float("inf"))

        self.all_walls = pg.sprite.LayeredDirty()
        self.all_cells = pg.sprite.LayeredDirty()
        self.map_matrix = np.empty((map_len_cells, map_len_cells), dtype=object)
        
        self.all_buttons = pg.sprite.LayeredDirty()

        # Генерация карты
        self.tile_map = data.maps.squares.tile_map.copy() # тайловая карта - по сетке

        utils.functions.builder(self.tile_map, obj.cell.Cell, 0, self.all_cells, self.all_sprites, self.map_matrix)
        utils.functions.builder(self.tile_map, obj.wall.Wall, 1, self.all_walls, self.all_sprites, self.map_matrix)

        virtual_screen_size = map_len_cells * len_cell
        self.map_screen = pg.Surface((virtual_screen_size, virtual_screen_size))
        self.background = self.map_screen.copy()
        self.all_cells.draw(self.background, self.background)
        self.all_walls.draw(self.background, self.background)

        # UI экран
        self.button_turn_switch = ui.uipanel.UIPanel(SW*15/16 - SW/16, SH*15/16 - SH/16, SW*1/8, SH*1/8, (0,255,255), 1, (255,128,0), 5)
        self.button_turn_switch.dirty = 2
        self.all_buttons.add(self.button_turn_switch)

        self.panel_resources = ui.uipanel.UIPanel(SW/2, SH*3/80, SW*15/64, SH*8/80, (128,128,128), 1, select_color, int(SW*2/1280))
        self.panel_cnt_turns = ui.uipanel.UIPanel(SW*15/16, SH*13.5/16, SW*1/8, SH*1/16, (128,128,128), 1, (255,128,0), int(SW*5/1280))
        self.panel_hp = ui.uipanel.UIPanel(SW/64, SH/2, SW/32, SH/2, (255,255,255), 1, (255,128,0), int(SW*5/1280))

        # Игроки
        self.players: list[core.player.Player] = []
        for i in range(QNT_PLAYERS):
            players.append(core.player.Player(i, INITIAL_RESOURCES))
        self.cut_player_id = 0
        self.cur_player = players[active_player]
        players_is_init = True

    def handle_events(self, all_events: list[pg.event.Event]):
        for event in all_events:
            if event.type == pg.K_ESCAPE:
                from .main_menu_scene import MainMenuScene
                self.game.set_scene(MainMenuScene)

            elif event.type == pg.MOUSEBUTTONDOWN:
                if self.button_start_game.rect.collidepoint(event.pos):
                    
                    from .game_scene import GameScene
                    self.game.set_scene(GameScene)
                    self.all_buttons.empty()

    def update(self):
        pass

    def display(self, screen: pg.Surface):
        self.all_buttons.draw(screen, self.background)
