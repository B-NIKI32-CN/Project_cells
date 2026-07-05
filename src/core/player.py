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
        self.res = res
        self.exp = 0
        self.base = None
        self.hp = 1
        self.spawn_tank_buff = None
        self.tanks = pg.sprite.Group()
        self.mist_matrix = np.zeros((map_len_cells, map_len_cells), np.int64)
        
    def move(self, w, a, s, d):
        if w == 1:
            self.cam_pos[1] -= self.speed
            if self.cam_pos[1] < -camera_luft*len_cell:
                self.cam_pos[1] = -camera_luft*len_cell
        if a == 1:
            self.cam_pos[0] -= self.speed
            if self.cam_pos[0] < -camera_luft*len_cell:
                self.cam_pos[0] = -camera_luft*len_cell
        if s == 1:
            self.cam_pos[1] += self.speed
            if self.cam_pos[1] > self.vs-SH+camera_luft*len_cell:
                self.cam_pos[1] = self.vs - SH + camera_luft*len_cell
        if d == 1:
            self.cam_pos[0] += self.speed
            if self.cam_pos[0] > self.vs-SW+camera_luft*len_cell:
                self.cam_pos[0] = self.vs - SW + camera_luft*len_cell
