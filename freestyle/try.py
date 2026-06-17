# from scripts.player import Player
# from scripts.functions import builder, spawn_obj, angle_vector
# from scripts.cell import Cell
# from scripts.wall import Wall
# from scripts.tank import Tank
# from scripts.base import Base
# from scripts.button import Button
# from scripts.selectedcell import Selectedcell
# import pygame as pg
# import maps.sandlot as sandlot
# import maps.squares as squares
# from settings import *
# from ttx import *
import numpy as np
from math import sin, cos, pi, radians

from settings import team_to_color

import pygame
import sys
k=0
import pygame
import random

pygame.init()
screen = pygame.display.set_mode((800, 600))
screen.fill((255,255,255))


# Обычный спрайт (перерисовка всего экрана)
class NormalBall(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, 780)
        self.rect.y = random.randint(0, 580)
        self.vel_x = random.randint(-3, 3)
        self.vel_y = random.randint(-3, 3)

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        # Ограничения границ...


# Dirty спрайт (перерисовка только измененных областей)
class DirtyBall(pygame.sprite.DirtySprite):
    def __init__(self, color=(0, 255, 0), visible = True):
        pygame.sprite.DirtySprite.__init__(self)
        self.image = pygame.Surface((20, 20))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, 780)
        self.rect.y = random.randint(0, 580)
        self.vel_x = random.randint(-3, 3)
        self.vel_y = random.randint(-3, 3)
        self.dirty = 1  # Начальное состояние - грязный
        self.visible = visible

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.dirty = 1  # Сообщаем, что спрайт изменился


# Обычная группа против LayeredDirty
normal_group = pygame.sprite.Group()
dirty_group = pygame.sprite.LayeredDirty()  # Специальная группа!
dirty_group_background = pygame.sprite.LayeredDirty()

# Создаем 500 обычных спрайтов
for _ in range(500):
    normal_group.add(NormalBall())

# Создаем 500 dirty спрайтов
for _ in range(2500):
    dirty_group.add(DirtyBall(visible = True))
    dirty_group_background.add(DirtyBall(color = (0,125,255)))


clock = pygame.time.Clock()
background = screen.copy()  # Снимок фона для dirty rects
dirty_group_background.draw(background)

running = True
use_dirty = True  # Переключайте для теста производительности

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                use_dirty = not use_dirty
                print(f"Режим: {'Dirty' if use_dirty else 'Normal'}")
            if event.key == pygame.K_l:
                k = 1
    if k==1:
        k=0
        for sprite in dirty_group:
            sprite.visible = False



    if use_dirty:
        # Обновление dirty спрайтов
        dirty_group.update()
        # Отрисовка только грязных областей!
        dirty_group.draw(screen, background)
    else:
        # Обычный подход: очистка всего экрана
        screen.fill((0, 0, 0))
        normal_group.update()
        normal_group.draw(screen)

    print(clock.get_fps())
    pygame.display.flip()
    clock.tick(60)


