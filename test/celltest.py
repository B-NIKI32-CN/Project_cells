from scripts.functions import builder
from scripts.cell import Cell
from scripts.wall import Wall
import pygame as pg
import maps.sandlot as sandlot
import maps.squares as squares


SW = 1000
SH = 800
SC = SW/2, SH/2

FPS = 120

pg.init()
pg.mixer.init()
screen = pg.display.set_mode((SW, SH))
pg.display.set_caption("meme")
clock = pg.time.Clock()

all_walls = pg.sprite.Group()
all_cells = pg.sprite.Group()

running = True
scene = 'game'

buildflag = True

keys = [0] * 100

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_w:
                keys[0] = 1
            if event.key == pg.K_a:
                keys[1] = 1
            if event.key == pg.K_s:
                keys[2] = 1
            if event.key == pg.K_d:
                keys[3] = 1
            if event.key == pg.K_k:
                keys[4] = 1
            if event.key == pg.K_l:
                keys[5] = 1
            if event.key == pg.K_e:
                keys[6] = 1
            if event.key == pg.K_r:
                keys[7] = 1
            if event.key == pg.K_SPACE:
                keys[8] = 1
        if event.type == pg.KEYUP:
            if event.key == pg.K_w:
                keys[0] = 0
            if event.key == pg.K_a:
                keys[1] = 0
            if event.key == pg.K_s:
                keys[2] = 0
            if event.key == pg.K_d:
                keys[3] = 0
            if event.key == pg.K_k:
                keys[4] = 0
            if event.key == pg.K_l:
                keys[5] = 0
            if event.key == pg.K_e:
                keys[6] = 0
            if event.key == pg.K_r:
                keys[7] = 0
            if event.key == pg.K_SPACE:
                keys[8] = 0
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                keys[32] = 1
            if event.button == 2:
                keys[35] = 1
            if event.button == 3:
                keys[37] = 1
        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                keys[32] = 0
            if event.button == 2:
                keys[35] = 0
            if event.button == 3:
                keys[37] = 0




        if scene == 'menu':
            pass
        if scene == 'game':
            if buildflag:

                cell1 = Cell(100,100)
                all_walls.add(cell1)
                buildflag = False
            screen.fill((255, 255, 255))
            all_cells.draw(screen)
            all_walls.draw(screen)







    clock.tick(FPS)
    pg.display.flip()


pg.quit()