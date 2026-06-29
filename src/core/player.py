import pygame as pg
import numpy as np
from ..core.settings import *

class Player:
    select = 'player'
    speed = player_speed
    vs = map_len_cells * len_cell
    def __init__(self, n, res):
        self.place = [0,0]
        self.team = n
        self.res = res
        self.exp = 0
        self.base = None
        self.hp = 1
        self.tanks = pg.sprite.Group()
        # self.mists = pg.sprite.Group()
        self.mist_matrix = np.zeros((map_len_cells, map_len_cells))
    def move(self, w, a, s, d):
        if w == 1:
            self.place[1] -= self.speed
            if self.place[1] < -0*len_cell:
                self.place[1] = -0*len_cell
        if a == 1:
            self.place[0] -= self.speed
            if self.place[0] < -0*len_cell:
                self.place[0] = -0*len_cell
        if s == 1:
            self.place[1] += self.speed
            if self.place[1] > self.vs-SH+0*len_cell:
                self.place[1] = self.vs - SH + 0*len_cell
        if d == 1:
            self.place[0] += self.speed
            if self.place[0] > self.vs-SW+0*len_cell:
                self.place[0] = self.vs - SW + 0*len_cell