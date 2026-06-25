import numpy as np
import pygame as pg
from settings import *
from math import sin, cos, pi, atan, log
import matplotlib.pyplot as plt
# import scipy.interpolate as interp

def builder(map, obj, obj_ind, obj_group, all_sprites, obj_group_matrix):
    poses = np.where(map == obj_ind)
    k = 0
    for pos in range(len(poses[0])):
        x = poses[1][pos] * obj.W
        y = poses[0][pos] * obj.H
        sprite = obj(x, y)
        obj_group.add(sprite)
        all_sprites.add(sprite)
        obj_group_matrix[poses[0][pos], poses[1][pos]] = sprite


def mist_builder(map, obj, objgroup):
    poses = np.where(map == 0)
    for pos in range(len(poses[0])):
        x = poses[1][pos] * obj.W
        y = poses[0][pos] * obj.H
        objgroup.add(obj(x, y))

def spawn_team_obj(map, obj, objind, objgroup, objgroup_player, all_sprites, sel_cell_pos, *info):
    if map[sel_cell_pos[1], sel_cell_pos[0]] == 0:
        obj_cur = obj(sel_cell_pos[0] * len_cell, sel_cell_pos[1] * len_cell, *info)
        objgroup.add(obj_cur)
        objgroup_player.add(obj_cur)
        all_sprites.add(obj_cur)
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
def mist_doting3000(tank_group, base, map_matrix, all_tanks, all_bases, team): # прибавляю к позициям матрицы A 1 которые видит танк (матрица A имеет размер карты)
    A = np.zeros((map_len_cells, map_len_cells), np.int64)
    for tank in tank_group:
        radius = tank.vis
        radius_in2 = radius**2
        center = tank.place
        start_x = 0
        start_y = 0
        end_x = 2*radius + 1
        end_y = 2*radius + 1
        limites = [[center[0]-radius,center[0]+radius], [center[1]-radius,center[1]+radius]] # просто для оптимизации и без того быстрого numpy (x, y)
        if limites[0][0] < 0:                                                                 # это просто ограничение области
            limites[0][0] = 0
            start_x = radius - center[0]
        if limites[1][0] < 0:
            limites[1][0] = 0
            start_y = radius - center[1]
        if limites[0][1] >= map_len_cells:
            limites[0][1] = map_len_cells-1
            end_x = map_len_cells - 1 - center[0] - radius
        if limites[1][1] >= map_len_cells:
            limites[1][1] = map_len_cells-1
            end_y = map_len_cells - 1 - center[1] - radius
        A[limites[1][0]:limites[1][1]+1, limites[0][0]:limites[0][1]+1] += tank.mist_matrix[start_y:end_y,start_x:end_x]
    if base != None:
        A[base.sprites()[0].place[1], base.sprites()[0].place[0]] = 1
    mist_sprites = map_matrix[np.where(A == 1)]
    for sprite in mist_sprites:
        sprite.change_misty(0)
    mist_sprites = map_matrix[np.where(A == 0)]
    for sprite in mist_sprites:
        sprite.change_misty(1)
    for tank in all_tanks:
        tank.change_misty(map_matrix[tank.place[1], tank.place[0]].misty)
    for base in all_bases:
        base.change_misty(map_matrix[base.place[1], base.place[0]].misty)
    return A

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

# def f1(x):
#     return sin(pi*(x-0.5))/2 + 0.5
# def f2(x):
#     return (x-1)**2 + 1
# def f3(x):
#     return x - 0.25
# def f_full(x):
#     if x <= 1:
#         k = f1(x)
#     elif x <= 1.5:
#         k = f2(x)
#     else:
#         k = f3(x)
#     return k

def f1(x):
    return x**2
def f2(x):
    return log(x)/2 +1
def f_full(x):
    if x <= 1:
        k = f1(x)
    else:
        k = f2(x)
    return k

def damage(a, p, d0):
    x = p/a
    k = f_full(x)
    d = k * d0
    return d

def get_res(n): # функция считающая сколько начислить ресурсов
    res = (1-n/12) * 40
    return int(res)

def calclin(pount1, pount2):
    x1 = pount1[0]
    y1 = pount1[1]
    x2 = pount2[0]
    y2 = pount2[1]
    if x1*(y1+y2) != y1*(x1+x2): # условия не прохождения прямой через 0,0 ведь тогда потом матрице пизда
        if x1 == x2:
            solve = np.array([1, 0])
            equals = x1
        elif y1 == y2:
            solve = np.array([0, 1])
            equals = y1
        else:
            A = np.array([[x1, y1], [x2, y2]])
            solve = np.linalg.solve(A, np.ones(2)) # a, b
            equals = 1 # число после равно
    else:
        solve = np.array([y2-y1, x1-x2])
        equals = 0

    return solve, equals  # возвращает a и b уравнения прямой вида x*a + y*b = с, и c (equals)

def dist_linpoint(point, solve, equals):
    dist = abs(point[0]*solve[0] + point[1]*solve[1] - equals) / (solve[0]**2 + solve[1]**2)**0.5
    return dist

# plt.figure(figsize=[10,6], dpi=100, facecolor='m')
# x_plot = np.linspace(0, 4, 500)
# y_plot = []
# for i in range(len(x_plot)):
#     y_plot.append(damage(1, x_plot[i], 1))
# plt.plot(x_plot, y_plot)
#
#
#
# plt.grid(True)
#
# plt.show()