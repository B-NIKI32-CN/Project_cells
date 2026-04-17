from scripts.player import Player
from scripts.functions import builder, spawn_obj
from scripts.cell import Cell
from scripts.wall import Wall
from scripts.tank import Tank
from scripts.base import Base
from scripts.button import Button
from scripts.selectedcell import Selectedcell
import pygame as pg
import maps.sandlot as sandlot
import maps.squares as squares
from settings import *
from ttx import *

pg.init()
pg.mixer.init()
# screen = pg.display.set_mode((SW, SH), pg.FULLSCREEN, vsync=1)
screen = pg.display.set_mode((SW, SH), vsync=1)
pg.display.set_caption("meme")
clock = pg.time.Clock()

all_walls = pg.sprite.Group()
all_cells = pg.sprite.Group()
all_selected = pg.sprite.Group()
all_tanks= pg.sprite.Group()
all_bases = pg.sprite.Group()
all_buttons_menu = pg.sprite.Group()
all_buttons_game = pg.sprite.Group()

vs = maplenincells * lencell
virtualscreen = pg.Surface((vs, vs))

select_cell = 0
players = []


running = True
scene = 'menu'

buildflagmap = True
buildflagmenu = True
buttons_flag_game = True
sel_tank = False
players_flag = True

keys = [0] * 100
turn = 0
n = 2
player = 0
all_keys = (pg.K_w, pg.K_a, pg.K_s, pg.K_d, pg.K_k, pg.K_l,
            pg.K_e, pg.K_r, pg.K_SPACE, pg.K_t, pg.K_b,
            pg.K_ESCAPE)


while running:
    r_m_pos = pg.mouse.get_pos()
    for event in pg.event.get():
        keys_clicked = [0] * 100
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            for i, k in enumerate(all_keys):
                if event.key == k:
                    keys[i] = 1
                    keys_clicked[i] = 1
        if event.type == pg.KEYUP:
            for i, k in enumerate(all_keys):
                if event.key == k:
                    keys[i] = 0
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                keys[32] = 1
                keys_clicked[32] = 1
            if event.button == 2:
                keys[35] = 1
                keys_clicked[35] = 1
            if event.button == 3:
                keys[37] = 1
                keys_clicked[37] = 1
        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                keys[32] = 0
            if event.button == 2:
                keys[35] = 0
            if event.button == 3:
                keys[37] = 0


        if scene == 'menu':
            if buildflagmenu:
                b_start = Button(SW/2, SH/2,200, 100, (0,255,255))
                all_buttons_menu.add(b_start)
                buildflagmenu = False
            screen.fill((255,255,255))
            all_buttons_menu.draw(screen)
            if keys_clicked[32] == 1 and b_start.rect.collidepoint(r_m_pos):
                scene = 'game'
                buildflagmenu = True
                all_buttons_menu.empty()
        if scene == 'game':

            map = squares.map
            if buildflagmap:

                builder(map, Cell, 0, all_cells)
                builder(map, Wall, 1, all_walls)
                buildflagmap = False

            if buttons_flag_game:
                b_turn = Button(SW*15/16, SH*15/16,SW*1/8, SH*1/8, (0,255,255))
                all_buttons_game.add(b_turn)
                buttons_flag_game = False

            if players_flag:
                for i in range(n):
                    players.append(Player(i, res0))
                player = players[turn]
                players_flag = False

            m_m_pos = (player.place[0] + r_m_pos[0], player.place[1] + r_m_pos[1])
            cell_m_pos = (m_m_pos[0] // lencell , m_m_pos[1] // lencell)

            if keys[32] == 1 and keys[9] == 1:
                spawn_obj(map, Tank, 2, all_tanks, cell_m_pos, player.n, 0, lt3a)
            if keys[32] == 1 and keys[10] == 1:
                spawn_obj(map, Base, 3, all_bases, cell_m_pos, player.n)
            if keys[32] == 1 and keys[5] == 1:
                spawn_obj(map, Wall, 1, all_walls, cell_m_pos)


            if keys[32] == 1:
                sel_tank = False
                all_selected.empty()
                select_cell = Selectedcell(lencell * cell_m_pos[0], lencell * cell_m_pos[1])
                all_selected.add(select_cell)
                if map[cell_m_pos[1], cell_m_pos[0]] == 2:
                    for tank in all_tanks:
                        if tank.place[0] == cell_m_pos[0] and tank.place[1] == cell_m_pos[1]:
                            sel_tank = tank
                            break


            if  sel_tank != False:
                sel_tank.move(keys_clicked[0], keys_clicked[1], keys_clicked[2], keys_clicked[3], map, select_cell)
            else:
                player.move(keys[0], keys[1], keys[2], keys[3])
                print(players[0].place)
                print(players[1].place)

            if keys_clicked[32] == 1 and b_turn.rect.collidepoint(r_m_pos):
                turn += 1
                if turn >= n:
                    turn = 0
                player = players[turn]
                print(turn)

            if keys_clicked[11] == 1:
                scene = 'menu'
                all_walls.empty()
                all_cells.empty()
                all_selected.empty()
                all_tanks.empty()
                all_bases.empty()
                all_buttons_menu.empty()
                buildflagmap = True
                players_flag = True
                buttons_flag_game = True

            virtualscreen.fill((255, 255, 255))
            screen.fill((255, 255, 255))

            all_cells.draw(virtualscreen)
            all_walls.draw(virtualscreen)
            all_tanks.draw(virtualscreen)
            all_bases.draw(virtualscreen)
            all_selected.draw(virtualscreen)
            dest = (-player.place[0], -player.place[1] )
            screen.blit(virtualscreen, dest)
            all_buttons_game.draw(screen)

    clock.tick(FPS)
    pg.display.flip()


pg.quit()