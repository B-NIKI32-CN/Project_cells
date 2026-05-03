import pygame as pg
from settings import *
import numpy as np

class Player:
    select = 'player'
    speed = player_speed
    vs = map_len_cells * len_cell
    def __init__(self, n, res):
        self.place = [0,0]
        self.n = n
        self.res = res
        self.base = 0
        self.tanks = pg.sprite.Group()
        self.mists = pg.sprite.Group()
    def move(self, w, a, s, d):
        if w == 1:
            self.place[1] -= self.speed
            if self.place[1] < -5*len_cell:
                self.place[1] = -5 * len_cell
        if a == 1:
            self.place[0] -= self.speed
            if self.place[0] < -5*len_cell:
                self.place[0] = -5 * len_cell
        if s == 1:
            self.place[1] += self.speed
            if self.place[1] > self.vs-SH+5*len_cell:
                self.place[1] = self.vs - SH + 5 * len_cell
        if d == 1:
            self.place[0] += self.speed
            if self.place[0] > self.vs-SW+5*len_cell:
                self.place[0] = self.vs - SW + 5 * len_cell