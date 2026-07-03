import pygame as pg
import numpy as np

from ..core.scene import Scene
from .. import ui
from ..core.settings import *
from ..core.game import Game

class GameScene(Scene):

    def __init__(self, game: Game):
        super().__init__(game)
        self.all_walls = pg.sprite.LayeredDirty()
        self.all_cells = pg.sprite.LayeredDirty()
        self.map_matrix = np.empty((map_len_cells, map_len_cells), dtype=object)

        self.all_selected_cells = pg.sprite.LayeredDirty()
        self.all_selected_in_window = pg.sprite.LayeredDirty()
        self.all_selected_taken_in_window = pg.sprite.LayeredDirty()
        self.all_tanks = pg.sprite.LayeredDirty()
        self.all_bases = pg.sprite.LayeredDirty()
        self.all_buttons = pg.sprite.LayeredDirty()
        self.all_projectiles = pg.sprite.LayeredDirty()
        self.market_window = pg.sprite.LayeredDirty()
        self.market_ui_tanks = pg.sprite.LayeredDirty()

        self.all_sprites = pg.sprite.LayeredDirty(_time_threshold = 666)

        self.virtual_screen_size = map_len_cells * len_cell

        self.players = []

        self.to_build_map = True
        self.to_build_menu = True
        self.to_build_game_buttons = True
        self.selected_tank = None
        self.players_registered = False
        self.taken_tank = None
        self.tank_ready_to_spawn = None
        # self.selected_tank = False
        self.to_regist_players = True
        self.taken_tank = False
        self.ready_to_spawn_tank = False
        self.drop_the_curtain = False
        self.select_cell = None
        self.canvas_dam = None

        self.market_window_is_open = False

        self.active_player = 0
        self.QNT_PLAYERS = 2
        self.cnt_rounds = 0
        self.damage_text_timelive = 0

        self.old_fps_val = 0


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
