from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..obj.base import Base
    from ..obj.tank import Tank
    from ..ui.img_tank import ImgTank


import pygame as pg
import numpy as np

from .settings import *


class Player:
    select = "player"
    speed = player_speed
    vs = map_len_cells * len_cell
    def __init__(self, n, res):
        self.cam_pos = [0,0]
        self.team = n
        self.resources = res
        self.exp = 0
        self.base: Base | None = None
        self.selected_tank: Tank | None = None
        self.hp = 1
        self.spawn_tank_buff: ImgTank | None = None
        self.tanks: pg.sprite.LayeredDirty[Tank] = pg.sprite.LayeredDirty()
        self.mist_matrix = np.zeros((map_len_cells, map_len_cells), np.int64)
        
    def move(self, keys):
        if keys[pg.K_w]:
            self.cam_pos[1] -= self.speed
            if self.cam_pos[1] < -camera_luft*len_cell:
                self.cam_pos[1] = -camera_luft*len_cell
        if keys[pg.K_a]:
            self.cam_pos[0] -= self.speed
            if self.cam_pos[0] < -camera_luft*len_cell:
                self.cam_pos[0] = -camera_luft*len_cell
        if keys[pg.K_s]:
            self.cam_pos[1] += self.speed
            if self.cam_pos[1] > self.vs-SH+camera_luft*len_cell:
                self.cam_pos[1] = self.vs - SH + camera_luft*len_cell
        if keys[pg.K_d]:
            self.cam_pos[0] += self.speed
            if self.cam_pos[0] > self.vs-SW+camera_luft*len_cell:
                self.cam_pos[0] = self.vs - SW + camera_luft*len_cell
