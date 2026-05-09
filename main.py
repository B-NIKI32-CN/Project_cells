# хуй пися члеен
import pygame as pg
import scripts
import maps
from settings import *
from ttx import *

pg.init()
pg.mixer.init()

screen = pg.display.set_mode((SW, SH), vsync=1)
# SW = screen.get_width()
# SH = screen.get_height()

text_start = font48.render("Proceed", True, (0, 0, 0))

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

vs = map_len_cells * len_cell
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

open_win_market = 0 # не понятно что это значит

keys = [0] * 100 # зачем тебе вручную делать список нажатых клавиш если есть pg.key.get_pressed()
keys_clicked = [0] * 100
turn = 0
n = 2
len_game_count = 0
player = 0
dam_text_timelive = 0
all_keys = (pg.K_w, pg.K_a, pg.K_s, pg.K_d, pg.K_k, pg.K_l,
            pg.K_e, pg.K_r, pg.K_SPACE, pg.K_t, pg.K_b,
            pg.K_ESCAPE, pg.K_q)

while running:
    r_m_pos = pg.mouse.get_pos()
    for event in pg.event.get():
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
        if menu_not_builded:
            b_start = scripts.button.Button(SW/2, SH/2,200, 100, (0,255,255))
            b_start.edges((255,128,0), 5)
            all_buttons_menu.add(b_start)
            menu_not_builded = False
        screen.fill((255,255,255))
        all_buttons_menu.draw(screen)
        screen.blit(text_start, (SW/2-75, SH/2-20))
        if keys_clicked[32] == 1 and b_start.rect.collidepoint(r_m_pos):
            keys_clicked[32] = 0
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
            b_turn.edges((255,128,0), 5)
            canvas0 = scripts.surface.Surface(SW/2, SH*3/80, SW*15/64, SH*8/80, (128,128,128), 1, select_color,  int(SW*2/1280))
            canvas1 = scripts.surface.Surface(SW*15/16, SH*13.5/16, SW*1/8, SH*1/16, (128,128,128), 1, (255,128,0), int(SW*5/1280))
            canvas_for_hp = scripts.surface.Surface(SW/64, SH/2, SW/32, SH/2, (255,255,255), 1, (255,128,0), int(SW*5/1280))
            all_buttons_game.add(b_turn)
            buttons_flag_game = False

        if players_flag:   # регистрация игроков
            for i in range(n):
                players.append(scripts.player.Player(i, res0))
            for player in players:
                scripts.functions.mist_builder(np.zeros((map_len_cells, map_len_cells)), scripts.mist.Mist, player.mists)
            player = players[turn]
            players_flag = False

        # координаты  мыщки сдвинутые на dest (смещение камеры игрока) снизу написал все
        dest_mouse_pos = (player.place[0] + r_m_pos[0], player.place[1] + r_m_pos[1])   # положение мыши на карте
        cell_mouse_pos = (int(dest_mouse_pos[0] // len_cell) , int(dest_mouse_pos[1] // len_cell)) # положение мыши на карте в количестве полных клеток

        if player.base == 0: # установка базы игрока
            if (keys_clicked[32] == 1 and 0<=cell_mouse_pos[0]<map_len_cells and 0<=cell_mouse_pos[1]<map_len_cells
                    and map[cell_mouse_pos[1], cell_mouse_pos[0]] == 0):
                keys_clicked[32] = 0
                player.base = pg.sprite.Group()
                scripts.functions.spawn_team_obj(
                    map, scripts.base.Base, 3, all_bases, player.base, cell_mouse_pos, player.n, player
                    )
                player.mist_matrix[player.base.sprites()[0].place[1], player.base.sprites()[0].place[0]] = 1 # делаю видимым положение в которое только что поставил базу
                player.hp = player.base.sprites()[0].hp


        if keys_clicked[32] == 1 and player.base != 0 and player.base.sprites()[0].place[0] == cell_mouse_pos[0] and player.base.sprites()[0].place[1] == cell_mouse_pos[1]: # меню выбора танков
            keys_clicked[32] = 0
            tank_menu =  scripts.button.Button(SW/2, SH/2, SW/2, SH/2, (66,66,66))
            tank_menu.edges((255,128,0), 10)
            tanks_win.add(tank_menu)
            for j, tank_for_menu in enumerate(alpha):
                x = j%3
                y = j//3
                tanks_for_win.add(scripts.img_tank.ImgTank(SW / 2 - SW / 8 + x * SW / 8 - len_cell / 2,
                                                           SH / 2 - SH / 8 + y * SH / 8 - len_cell / 2, player.n, 0, tank_for_menu))
            tanks_win.add(tanks_for_win)
            ext = scripts.button.Button(SW*3/4-SW/32, SH/4+SH/32, SW/16, SH/16, (200,0,0))
            ext.edges((0,255,255), 5)
            b_take = scripts.button.Button(SW*3/4-SW/32, SH*3/4+SH/32, SW/16, SH/16, (128,255,128))
            b_take.edges((0,128,0), 5)
            b_throw = scripts.button.Button(SW*3/4-SW/32-SW/16, SH*3/4+SH/32, SW/16, SH/16, (255,255,128))
            b_throw.edges((128,128,0), 5)
            tanks_win.add(ext, b_take, b_throw)
            open_win_market = 1
        if open_win_market == 1: # выбор танков в соответственном меню
            if keys_clicked[32] == 1:
                keys_clicked[32] = 0
                for tank in tanks_for_win:
                    if tank.rect.collidepoint(r_m_pos):
                        tanks_win.remove(all_selected_win)
                        all_selected_win.empty()
                        tank_take = tank
                        select_place = scripts.selectedcell.Selectedcell(tank.x, tank.y)
                        all_selected_win.add(select_place)
                        b_take.edges((0, 128, 0), 5)
                        b_throw.edges((128, 128, 0), 5)
                    tanks_win.add(all_selected_win)
                if b_take.rect.collidepoint(r_m_pos) and tank_take != False:
                    b_take.edges((0, 255, 255), 5)
                    ready_to_spawn_tank = tank_take
                if b_throw.rect.collidepoint(r_m_pos) and ready_to_spawn_tank != False:
                    b_throw.edges((0, 255, 255), 5)
                    b_take.edges((0, 128, 0), 5)
                    ready_to_spawn_tank = False
                if ext.rect.collidepoint(r_m_pos):
                    tanks_win.empty()
                    all_selected_win.empty()
                    tank_take = False
                    open_win_market = 0

        if keys_clicked[32] == 1 and open_win_market == 0 and ready_to_spawn_tank != False and player.base != 0: # установка выбранного танка
            keys_clicked[32] = 0
            dist_spawn0 = ((int(player.base.sprites()[0].x) / len_cell - cell_mouse_pos[0]) ** 2
                           + (int(player.base.sprites()[0].y) / len_cell - cell_mouse_pos[1]) ** 2) ** 0.5
            if (dist_spawn0 <= dist_spawn and player.res >= ready_to_spawn_tank.ttx[12]
                    and player.exp >= ready_to_spawn_tank.ttx[13] and map[cell_mouse_pos[1], cell_mouse_pos[0]] == 0):
                scripts.functions.spawn_team_obj(
                    map, scripts.tank.Tank, 2, all_tanks, player.tanks,
                    cell_mouse_pos, player.n, 1, ready_to_spawn_tank.ttx,
                    player, scripts.mist.Mist, map)
                player.res -= ready_to_spawn_tank.ttx[-4]
                player.mists.empty()
                player.mist_matrix = scripts.functions.mist_doting3000(player.tanks)
                scripts.functions.mist_builder(player.mist_matrix, scripts.mist.Mist, player.mists)
                player.mist_matrix[player.base.sprites()[0].place[1], player.base.sprites()[0].place[0]] = 1
                ready_to_spawn_tank = False

        if keys_clicked[32] == 1 and b_turn.rect.collidepoint(r_m_pos): # смена хода
            keys_clicked[32] = 0
            if len_game_count//n != 0:
                player.exp += scripts.functions.cell_distribution(n, player.n, all_tanks)
                player.res += scripts.functions.get_res(len(player.tanks.sprites()))
            player.tanks.update()
            turn += 1
            if turn >= n:
                turn = 0
            player = players[turn]
            tank_take = False
            ready_to_spawn_tank = False
            sel_tank = False
            tanks_win.empty()
            all_selected_map.empty()
            len_game_count += 1

        if keys_clicked[32] == 1 and 0<=cell_mouse_pos[0]<map_len_cells and 0<=cell_mouse_pos[1]<map_len_cells and open_win_market == 0: # выбор клетки
            keys_clicked[32] = 0
            sel_tank = False
            all_selected_map.empty()
            select_cell = scripts.selectedcell.Selectedcell(len_cell * cell_mouse_pos[0], len_cell * cell_mouse_pos[1])
            all_selected_map.add(select_cell)
            if map[cell_mouse_pos[1], cell_mouse_pos[0]] == 2:
                for tank in all_tanks:
                    if tank.place[0] == cell_mouse_pos[0] and tank.place[1] == cell_mouse_pos[1]: # выбор танка на клетке
                        if tank.team == player.n:
                            sel_tank = tank
                        break

        if  sel_tank != False: # управление танком # ваня можешь переписать != False
            sel_tank.move(keys_clicked[0], keys_clicked[1], keys_clicked[2], keys_clicked[3], select_cell)
            if keys_clicked[0] or keys_clicked[1] or keys_clicked[2] or keys_clicked[3]:
                player.mists.empty()
                player.mist_matrix = scripts.functions.mist_doting3000(player.tanks)
                scripts.functions.mist_builder(player.mist_matrix, scripts.mist.Mist, player.mists)
                player.mist_matrix[player.base.sprites()[0].place[1], player.base.sprites()[0].place[0]] = 1
            keys_clicked[0] = 0
            keys_clicked[1] = 0
            keys_clicked[2] = 0
            keys_clicked[3] = 0
            if keys_clicked[8] == 1:
                keys_clicked[8] = 0
                sel_tank.shot(all_projectiles, dest_mouse_pos, scripts.projectile.Projectile)
            if keys[12] == 1:
                map[sel_tank.place[1], sel_tank.place[0]] = 0
                sel_tank.kill()
                sel_tank = False
                player.mists.empty()
                player.mist_matrix = scripts.functions.mist_doting3000(player.tanks)
                scripts.functions.mist_builder(player.mist_matrix, scripts.mist.Mist, player.mists)
                player.mist_matrix[player.base.sprites()[0].place[1], player.base.sprites()[0].place[0]] = 1
        else:  # управление камерой если не выбран танк
            player.move(keys[0], keys[1], keys[2], keys[3])
            keys_clicked[0] = 0
            keys_clicked[1] = 0
            keys_clicked[2] = 0
            keys_clicked[3] = 0
            keys_clicked[8] = 0

        if keys_clicked[11] == 1:
            keys_clicked[11] = 0
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
            turn = 0
            len_game_count = 0

        canvas_hp = scripts.surface.Surface(SW/64, (SH*(1/4+5/800)) + SH*(1/4-5/800)*(player.hp/base_hp), SW/32 - SW*10/1280, (SH/2 - SW*10/1280)*(player.hp/base_hp),
                                            (128+(team_to_color[player.n][0]-128)*(player.hp/base_hp),
                                             128+(team_to_color[player.n][1]-128)*(player.hp/base_hp),
                                             128+(team_to_color[player.n][2]-128)*(player.hp/base_hp)), 0, 0, 0)
        text_turns = font48.render(f'Turn: {len_game_count//n + 1}', True, team_to_color[player.n])
        text_res = font48.render(f"Resources : {player.res}", True, team_to_color[player.n])
        text_exp = font48.render(f"Сapture : {player.exp}", True, team_to_color[player.n])
        # all_projectiles.update(all_walls, all_tanks, player.tanks, all_bases)
        for projectile in all_projectiles:
            dam = projectile.update(all_walls, all_tanks, player.tanks, all_bases)
            if dam != 0:
                dam_text = font32.render(f'{int(dam)}', True, team_to_color[projectile.team])
                dam_dest = projectile.x, projectile.y
                dam_text_timelive = FPS
        virtualscreen.fill((255, 255, 255))
        screen.fill((255, 255, 255))
        player.mists.draw(virtualscreen)
        all_cells.draw(virtualscreen)
        for tank in all_tanks:
            if player.mist_matrix[tank.place[1], tank.place[0]] > 0:
                tank.draw(virtualscreen, player.n)
        for base in all_bases:
            if player.mist_matrix[base.place[1], base.place[0]] > 0:
                base.draw(virtualscreen)
        all_projectiles.draw(virtualscreen)
        all_walls.draw(virtualscreen)
        all_selected_map.draw(virtualscreen)
        if dam_text_timelive > 0:
            virtualscreen.blit(dam_text, dam_dest)
            dam_text_timelive -= 1
        dest = (-player.place[0], -player.place[1] )
        screen.blit(virtualscreen, dest)
        all_buttons_game.draw(screen)
        tanks_win.draw(screen)
        canvas0.draw(screen)
        canvas1.draw(screen)
        canvas_for_hp.draw(screen)
        canvas_hp.draw(screen)
        screen.blit(text_res, (SW/2-SW*7/64, 0))
        screen.blit(text_exp, (SW/2-SW*7/64, SH*3/80))
        screen.blit(text_turns, (SW*14/16 + SW*2/256, SH*14/16 - SW/32))

    clock.tick(FPS)
    pg.display.flip()

pg.quit()