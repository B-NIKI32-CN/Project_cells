import pygame as pg
import scripts
import maps
from settings import *
from ttx import *

pg.init()
pg.mixer.init()

screen = pg.display.set_mode((SW, SH), pg.FULLSCREEN, vsync=1)
SW = screen.get_width()
SH = screen.get_height()

pg.display.set_caption("meme")
clock = pg.time.Clock()

all_walls = pg.sprite.Group()
all_cells = pg.sprite.Group()
all_selected_map = pg.sprite.Group()
all_selected_win = pg.sprite.Group()
all_tanks= pg.sprite.Group()
all_bases = pg.sprite.Group()
all_buttons_menu = pg.sprite.Group()
all_buttons_game = pg.sprite.Group()
all_projectiles = pg.sprite.Group()
tanks_win = pg.sprite.Group()
tanks_for_win = pg.sprite.Group()

vs = maplenincells * lencell
virtualscreen = pg.Surface((vs, vs))

select_cell = 0
players = []

running = True
scene = 'menu'

map_not_builded = True
menu_not_builded = True
buttons_flag_game = True
sel_tank = False
players_flag = True # понормальнее надо назвать
tank_take = False
ready_to_spawn_tank = False

win1 = 0 # не понятно что это значит

keys = [0] * 100 # зачем тебе вручную делать список нажатых клавиш если есть pg.key.get_pressed()
keys_clicked = [0] * 100
turn = 0
n = 2
player = 0
all_keys = (pg.K_w, pg.K_a, pg.K_s, pg.K_d, pg.K_k, pg.K_l,
            pg.K_e, pg.K_r, pg.K_SPACE, pg.K_t, pg.K_b,
            pg.K_ESCAPE, pg.K_q)

while running:
    # mouse_pos = pg.mouse.get_pos()
    r_m_pos = pg.mouse.get_pos()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        keys_clicked = [0] * 100    
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
            if menu_not_builded:
                b_start = scripts.button.Button(SW/2, SH/2,200, 100, (0,255,255))
                all_buttons_menu.add(b_start)
                menu_not_builded = False
            screen.fill((255,255,255))
            all_buttons_menu.draw(screen)
            if keys_clicked[32] == 1 and b_start.rect.collidepoint(r_m_pos):
                scene = 'game'
                menu_not_builded = True
                all_buttons_menu.empty()

        elif scene == 'game':
            if map_not_builded:
                map = maps.squares.map.copy()
                scripts.functions.builder(map, scripts.cell.Cell, 0, all_cells)
                scripts.functions.builder(map, scripts.wall.Wall, 1, all_walls)
                map_not_builded = False

            if buttons_flag_game:
                b_turn = scripts.button.Button(SW*15/16, SH*15/16,SW*1/8, SH*1/8, (0,255,255))
                b_tanks_menu = scripts.button.Button(SW/2, SH*15/16,SW*1/8, SH*1/8, (150,0,255))
                all_buttons_game.add(b_turn)
                all_buttons_game.add(b_tanks_menu)
                buttons_flag_game = False

            if players_flag:
                for i in range(n):
                    players.append(scripts.player.Player(i, res0))
                player = players[turn]
                players_flag = False

            # это что вообще блин
            m_m_pos = (player.place[0] + r_m_pos[0], player.place[1] + r_m_pos[1])
            cell_m_pos = (int(m_m_pos[0] // lencell) , int(m_m_pos[1] // lencell))

            if player.base == 0:
                if keys_clicked[32] == 1:
                    player.base = pg.sprite.Group()
                    scripts.functions.spawn_team_obj(
                        map, scripts.base.Base, 3, all_bases, player.base, cell_m_pos, player.n
                        )

            if keys_clicked[32] == 1 and b_tanks_menu.rect.collidepoint(r_m_pos):
                tank_menu =  scripts.button.Button(SW/2, SH/2, SW/2, SH/2, (166,166,166))
                tanks_win.add(tank_menu)
                for j, tank_for_menu in enumerate(alpha):
                    x = j%3
                    y = j//3
                    tanks_for_win.add(scripts.img_tank.ImgTank(SW/2 - SW/8 + x*SW/8 - lencell/2,
                                              SH/2 - SH/8 + y*SH/8 - lencell/2, player.n, 0, tank_for_menu))
                tanks_win.add(tanks_for_win)
                ext = scripts.button.Button(SW*3/4-SW/32, SH/4+SH/32, SW/16, SH/16, (200,0,0))
                b_take = scripts.button.Button(SW*3/4-SW/32, SH*3/4+SH/32, SW/16, SH/16, (0,200,0))
                b_throw = scripts.button.Button(SW*3/4-SW/32-SW/16, SH*3/4+SH/32, SW/16, SH/16, (200,200,0))
                tanks_win.add(ext, b_take, b_throw)
                win1 = 1
            if win1 == 1:
                if keys_clicked[32] == 1:
                    for tank in tanks_for_win:
                        if tank.rect.collidepoint(r_m_pos):
                            tanks_win.remove(all_selected_win)
                            all_selected_win.empty()
                            tank_take = tank
                            select_place = scripts.selectedcell.Selectedcell(tank.x, tank.y)
                            all_selected_win.add(select_place)
                        tanks_win.add(all_selected_win)
                    if b_take.rect.collidepoint(r_m_pos) and tank_take != False:
                        ready_to_spawn_tank = tank_take
                    if b_throw.rect.collidepoint(r_m_pos) and ready_to_spawn_tank != False:
                        ready_to_spawn_tank = False
                    if ext.rect.collidepoint(r_m_pos):
                        tanks_win.empty()
                        all_selected_win.empty()
                        tank_take = False
                        win1 = 0

            if keys_clicked[32] == 1 and win1 == 0 and ready_to_spawn_tank != False:
                dist_spawn0 = ((int(player.base.sprites()[0].x)/lencell-cell_m_pos[0])**2
                               + (int(player.base.sprites()[0].y)/lencell-cell_m_pos[1])**2)**0.5
                if dist_spawn0 <= dist_spawn:
                    if player.res >= ready_to_spawn_tank.ttx[-3]:
                        scripts.functions.spawn_team_obj(
                            map, scripts.tank.Tank, 2, all_tanks, player.tanks, 
                            cell_m_pos, player.n, 0, ready_to_spawn_tank.ttx
                            )
                        player.res -= ready_to_spawn_tank.ttx[-3]
                    ready_to_spawn_tank = False

            if keys_clicked[32] == 1:
                sel_tank = False
                all_selected_map.empty()
                select_cell = scripts.selectedcell.Selectedcell(lencell * cell_m_pos[0], lencell * cell_m_pos[1])
                all_selected_map.add(select_cell)
                if map[cell_m_pos[1], cell_m_pos[0]] == 2:
                    for tank in all_tanks:
                        if tank.place[0] == cell_m_pos[0] and tank.place[1] == cell_m_pos[1]:
                            sel_tank = tank
                            break

            if  sel_tank != False:
                sel_tank.move(keys_clicked[0], keys_clicked[1], keys_clicked[2], keys_clicked[3], map, select_cell)
                if keys_clicked[8] == 1:
                    sel_tank.shot(all_projectiles, m_m_pos, scripts.projectile.Projectile)
                if keys[12] == 1:
                    map[sel_tank.place[1], sel_tank.place[0]] = 0
                    sel_tank.kill()
                    sel_tank = False
            else:
                player.move(keys[0], keys[1], keys[2], keys[3])

            if keys_clicked[32] == 1 and b_turn.rect.collidepoint(r_m_pos):
                turn += 1
                if turn >= n:
                    turn = 0
                player = players[turn]
                tank_take = False
                ready_to_spawn_tank = False
                tanks_win.empty()

            # if keys_clicked[32] == 1:

            if keys_clicked[11] == 1:
                scene = 'menu'
                all_walls.empty()
                all_cells.empty()
                all_selected_map.empty()
                all_tanks.empty()
                all_bases.empty()
                all_buttons_menu.empty()
                map_not_builded = True
                players_flag = True
                buttons_flag_game = True
                sel_tank = False
                tank_take = False
                ready_to_spawn_tank = False
                players = []

            all_projectiles.update()
            virtualscreen.fill((255, 255, 255))
            screen.fill((255, 255, 255))

            all_cells.draw(virtualscreen)
            all_walls.draw(virtualscreen)
            all_tanks.draw(virtualscreen)
            all_bases.draw(virtualscreen)
            all_selected_map.draw(virtualscreen)
            all_projectiles.draw(virtualscreen)
            dest = (-player.place[0], -player.place[1] )
            screen.blit(virtualscreen, dest)
            all_buttons_game.draw(screen)
            tanks_win.draw(screen)

    clock.tick(FPS)
    pg.display.flip()

pg.quit()