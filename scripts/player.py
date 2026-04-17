import pygame as pg
from settings import *

class Player:
    select = 'player'
    speed = playerspeed
    vs = maplenincells * lencell
    def __init__(self, n, res):
        self.place = [0,0]
        self.n = n
        self.res = res
        self.base = 0
        self.tanks = pg.sprite.Group()
    def move(self, w, a, s, d):
        if w == 1:
            self.place[1] -= self.speed
            if self.place[1] < -5*lencell:
                self.place[1] = -5*lencell
        if a == 1:
            self.place[0] -= self.speed
            if self.place[0] < -5*lencell:
                self.place[0] = -5*lencell
        if s == 1:
            self.place[1] += self.speed
            if self.place[1] > self.vs-SH+5*lencell:
                self.place[1] = self.vs-SH+5*lencell
        if d == 1:
            self.place[0] += self.speed
            if self.place[0] > self.vs-SW+5*lencell:
                self.place[0] = self.vs-SW+5*lencell