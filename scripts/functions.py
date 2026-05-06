import numpy as np
import pygame as pg
from settings import *
from math import sin, cos, pi, atan

def builder(map, obj, objind, objgroup):
    poses = np.where(map == objind)
    for pos in range(len(poses[0])):
        x = poses[1][pos] * obj.W
        y = poses[0][pos] * obj.H
        objgroup.add(obj(x, y))

def mist_builder(map, obj, objgroup):
    poses = np.where(map == 0)
    for pos in range(len(poses[0])):
        x = poses[1][pos] * obj.W
        y = poses[0][pos] * obj.H
        objgroup.add(obj(x, y))

def spawn_team_obj(map, obj, objind, objgroup, objgroup_player, sel_cell_pos, *info):
    if map[sel_cell_pos[1], sel_cell_pos[0]] == 0:
        odj = obj(sel_cell_pos[0] * len_cell, sel_cell_pos[1] * len_cell, *info)
        objgroup.add(odj)
        objgroup_player.add(odj)
        map[sel_cell_pos[1], sel_cell_pos[0]] = objind

def spawn_obj(map, obj, objind, objgroup, sel_cell_pos, *info):
    if map[sel_cell_pos[1], sel_cell_pos[0]] == 0:
        odj = obj(sel_cell_pos[0] * len_cell, sel_cell_pos[1] * len_cell, *info)
        objgroup.add(odj)
        map[sel_cell_pos[1], sel_cell_pos[0]] = objind

def angle_vector(x, y):
    if x == 0:
        if y>0:
            return pi/2
        else:
            return -pi/2
    else:
        angle = atan(y / x)
        if x < 0:
            angle = angle + pi
        if -pi <= angle <= pi:
            return angle
        elif angle < -pi:
            while angle < -pi:
                angle += 2*pi
        else:
            while angle > pi:
                angle -= 2*pi
        return angle

def mist_doting(A, group): # прибавляю к позициям матрицы A 1 которые видит танк (матрица A имеет размер карты)
    for tank in group:
        radius = tank.vis
        radius_in2 = radius**2
        center = tank.place
        limites = [[center[0]-radius,center[0]+radius], [center[1]-radius,center[1]+radius]] # просто для оптимизации и без того быстрого numpy (x, y)
        if limites[0][0] < 0:                                                                 # это просто ограничение области
            limites[0][0] = 0
        if limites[1][0] < 0:
            limites[1][0] = 0
        if limites[0][1] >= map_len_cells:
            limites[0][1] = map_len_cells-1
        if limites[1][1] >= map_len_cells:
            limites[1][1] = map_len_cells-1
        i, j = np.indices((limites[1][1]-limites[1][0]+1, limites[0][1]-limites[0][0]+1))
        i += limites[1][0]
        j += limites[0][0]
        dist_in2 = (center[1] - i)**2 + (center[0] - j)**2-1
        pos = np.where(dist_in2 <= radius_in2)
        dist_in2[:,:] = 0 # не хочу создавать новую матрицу, просто перезапишу отслужившую
        dist_in2[pos] = 1
        A[limites[1][0]:limites[1][1]+1, limites[0][0]:limites[0][1]+1] += dist_in2
    return A
    # подробно не описывал, все равно ты нумпай не будешь смотреть по-моему

def cell_distribution(n, team, group): # функция присвоения клетки команде, нужна для начисления exp в конце хода (равно количеству "захваченных клеток")
    matrixs = [0] * n
    dopusk = [1] * n
    bool_matrix = np.ones((map_len_cells, map_len_cells), dtype=bool)
    i, j = np.indices((map_len_cells, map_len_cells), np.float64)
    for tank in group:
        if dopusk[tank.team] == 1 and matrixs[tank.team] == 0:
            matrixs[tank.team] = np.zeros((map_len_cells, map_len_cells),np.float64)
            dopusk[tank.team] = 0
        pos = tank.place
        dist_in2 = (pos[1] - i)**2 + (pos[0] - j)**2
        dist_in2[pos[1], pos[0]] = 1e-6
        matrixs[tank.team] += 1/dist_in2
    for i in range(n):
        if i == team:
            continue
        delta_matrix = matrixs[team] - matrixs[i]
        if dopusk[team] == 0:
            bool_matrix[np.where(delta_matrix < 0)] = 0
        else:
            bool_matrix[:,:] = 0
    exp = len(np.where(bool_matrix == 1)[0])
    return exp

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

def get_res(n): # функция считающая сколько начислить ресурсов
    res = (1-n/12) * 40
    return int(res)

