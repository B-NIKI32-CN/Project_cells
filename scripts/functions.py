import numpy as np
import pygame as pg
from settings import *
from math import sin, cos, pi

def builder(map, obj, objind, objgroup):
    poses = np.where(map == objind)
    for pos in range(len(poses[0])):
        x = poses[1][pos] * obj.W
        y = poses[0][pos] * obj.H
        objgroup.add(obj(x, y))

def spawn_team_obj(map, obj, objind, objgroup, objgroup_player, sel_cell_pos, *info):
    if map[sel_cell_pos[1], sel_cell_pos[0]] == 0:
        odj = obj(sel_cell_pos[0] * lencell, sel_cell_pos[1] * lencell, *info)
        objgroup.add(odj)
        objgroup_player.add(odj)
        map[sel_cell_pos[1], sel_cell_pos[0]] = objind
def spawn_obj(map, obj, objind, objgroup, sel_cell_pos, *info):
    if map[sel_cell_pos[1], sel_cell_pos[0]] == 0:
        odj = obj(sel_cell_pos[0] * lencell, sel_cell_pos[1] * lencell, *info)
        objgroup.add(odj)
        map[sel_cell_pos[1], sel_cell_pos[0]] = objind

def f1(x):
    return sin(pi*(x-0.5))/2 + 0.5
def f2(x):
    return (x-1)**2 + 1
def f3(x):
    return x - 0.25
def damage(a, p, d0):
    x = p/a
    if x <= 1:
        k = f1(x)
    elif x <= 1.5:
        k = f2(x)
    else:
        k = f3(x)
    d = k * d0
    return d

