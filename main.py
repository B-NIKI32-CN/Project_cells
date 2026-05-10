# хуй пися члеен
from urllib.parse import to_bytes

import pygame as pg
import scripts
import maps
from settings import *
from ttx import *

pg.init()
pg.mixer.init()

screen = pg.display.set_mode((SW, SH), vsync=1)

text_start = font48.render("Proceed", True, (0, 0, 0))

pg.display.set_caption("meme")
clock = pg.time.Clock()

all_walls = pg.sprite.Group()
all_cells = pg.sprite.Group()
all_selected_map = pg.sprite.Group()
all_selected_in_window = pg.sprite.Group() # некит переименуй
all_tanks = pg.sprite.Group()
all_bases = pg.sprite.Group()
all_buttons_menu = pg.sprite.Group()
all_buttons_game = pg.sprite.Group()
all_projectiles = pg.sprite.Group()
market_window = pg.sprite.Group() # некит переименуй #+ # некит я не понял че это напиши коммент
tanks_ing_for_window = pg.sprite.Group() # некит переименуй #+ # тут тоже но ещё я не понял че такое ing

virtual_screen_size = map_len_cells * len_cell # было vs (удали коммент если всё ок)
virtual_screen = pg.Surface((virtual_screen_size, virtual_screen_size)) # было virtualscreen (удали коммент если всё ок)

players = []

running = True
scene = "menu"

to_build_map = True
to_build_menu = True
to_build_game_buttons = True
selected_tank = None
players_registered = False
taken_tank = None
tank_ready_to_spawn = None # я сначала подумал что это булевая переменная,если есть идеи как переименовать то действуй (после прочтения удали коммент)

market_window_is_open = False # было open_win_market (коммент можно удалить)

keys = [0] * 100 # зачем тебе вручную делать список нажатых клавиш если есть pg.key.get_pressed()
keys_clicked = [0] * 100
active_player = 0
QNT_PLAYERS = 2
cnt_rounds = 0
damage_text_timelive = 0
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

    if scene == "menu":
        if to_build_menu:
            b_start = scripts.button.Button(SW/2, SH/2,200, 100, (0,255,255))
            b_start.edges((255,128,0), 5)
            all_buttons_menu.add(b_start)
            to_build_menu = False
        screen.fill((255,255,255))
        all_buttons_menu.draw(screen)
        screen.blit(text_start, (SW/2-75, SH/2-20))
        if keys_clicked[32] == 1 and b_start.rect.collidepoint(r_m_pos):
            keys_clicked[32] = 0
            scene = "game"
            to_build_menu = True
            all_buttons_menu.empty()

    elif scene == "game":
        if to_build_map:
            map = maps.squares.map.copy()
            scripts.functions.builder(map, scripts.cell.Cell, 0, all_cells)
            scripts.functions.builder(map, scripts.wall.Wall, 1, all_walls)
            to_build_map = False

        if to_build_game_buttons:
            b_turn = scripts.button.Button(SW*15/16, SH*15/16,SW*1/8, SH*1/8, (0,255,255))
            b_turn.edges((255,128,0), 5)
            canvas0 = scripts.surface.Surface(SW/2, SH*3/80, SW*15/64, SH*8/80, (128,128,128), 1, select_color,  int(SW*2/1280))
            canvas1 = scripts.surface.Surface(SW*15/16, SH*13.5/16, SW*1/8, SH*1/16, (128,128,128), 1, (255,128,0), int(SW*5/1280))
            canvas_for_hp = scripts.surface.Surface(SW/64, SH/2, SW/32, SH/2, (255,255,255), 1, (255,128,0), int(SW*5/1280))
            all_buttons_game.add(b_turn)
            to_build_game_buttons = False

        if not players_registered:   # регистрация игроков
            for i in range(QNT_PLAYERS):
                players.append(scripts.player.Player(i, res0))
            for cur_player in players:
                scripts.functions.mist_builder(np.zeros((map_len_cells, map_len_cells)), scripts.mist.Mist, cur_player.mists)
            cur_player = players[active_player]
            players_registered = True

        # координаты  мыщки сдвинутые на dest (смещение камеры игрока) снизу написал все
        dest_mouse_pos = (cur_player.place[0] + r_m_pos[0], cur_player.place[1] + r_m_pos[1])   # положение мыши на карте
        cell_mouse_pos = (int(dest_mouse_pos[0] // len_cell) , int(dest_mouse_pos[1] // len_cell)) # положение мыши на карте в количестве полных клеток

        if cur_player.base == 0 and not b_turn.rect.collidepoint(r_m_pos): # установка базы игрока
            if (keys_clicked[32] == 1 and 0<=cell_mouse_pos[0]<map_len_cells and 0<=cell_mouse_pos[1]<map_len_cells
                    and map[cell_mouse_pos[1], cell_mouse_pos[0]] == 0):
                keys_clicked[32] = 0
                cur_player.base = pg.sprite.Group()
                scripts.functions.spawn_team_obj(
                    map, scripts.base.Base, 3, all_bases, cur_player.base, cell_mouse_pos, cur_player.n, cur_player
                    )
                cur_player.mist_matrix[cur_player.base.sprites()[0].place[1], cur_player.base.sprites()[0].place[0]] = 1 # делаю видимым положение в которое только что поставил базу
                cur_player.hp = cur_player.base.sprites()[0].hp


        if keys_clicked[32] == 1 and cur_player.base != 0 and cur_player.base.sprites()[0].place[0] == cell_mouse_pos[0] and cur_player.base.sprites()[0].place[1] == cell_mouse_pos[1]: # меню выбора танков
            keys_clicked[32] = 0
            tank_menu =  scripts.button.Button(SW/2, SH/2, SW/2, SH/2, (66,66,66))
            tank_menu.edges((255,128,0), 10)
            market_window.add(tank_menu)
            for j, tank_for_menu in enumerate(alpha):
                x = j%3
                y = j//3
                tanks_ing_for_window.add(scripts.img_tank.ImgTank(SW / 2 - SW / 8 + x * SW / 8 - len_cell / 2,
                                                                  SH / 2 - SH / 8 + y * SH / 8 - len_cell / 2, cur_player.n, 0, tank_for_menu))
            market_window.add(tanks_ing_for_window)
            ext = scripts.button.Button(SW*3/4-SW/32, SH/4+SH/32, SW/16, SH/16, (200,0,0))
            ext.edges((0,255,255), 5)
            b_take = scripts.button.Button(SW*3/4-SW/32, SH*3/4+SH/32, SW/16, SH/16, (128,255,128))
            b_take.edges((0,128,0), 5)
            b_throw = scripts.button.Button(SW*3/4-SW/32-SW/16, SH*3/4+SH/32, SW/16, SH/16, (255,255,128))
            b_throw.edges((128,128,0), 5)
            market_window.add(ext, b_take, b_throw)
            market_window_is_open = True
        if market_window_is_open: # выбор танков в соответственном меню
            if keys_clicked[32] == 1:
                keys_clicked[32] = 0
                for tank in tanks_ing_for_window:
                    if tank.rect.collidepoint(r_m_pos):
                        market_window.remove(all_selected_in_window)
                        all_selected_in_window.empty()
                        taken_tank = tank
                        select_place = scripts.selectedcell.Selectedcell(tank.x, tank.y)
                        all_selected_in_window.add(select_place)
                        b_take.edges((0, 128, 0), 5)
                        b_throw.edges((128, 128, 0), 5)
                    market_window.add(all_selected_in_window)
                if b_take.rect.collidepoint(r_m_pos) and taken_tank is not None:
                    b_take.edges((0, 255, 255), 5)
                    b_throw.edges((128, 128, 0), 5)
                    tank_ready_to_spawn = taken_tank
                if b_throw.rect.collidepoint(r_m_pos) and tank_ready_to_spawn is not None:
                    b_throw.edges((0, 255, 255), 5)
                    b_take.edges((0, 128, 0), 5)
                    tank_ready_to_spawn = None
                if ext.rect.collidepoint(r_m_pos):
                    market_window.empty()
                    all_selected_in_window.empty()
                    taken_tank = None
                    market_window_is_open = False

        if keys_clicked[32] == 1 and not market_window_is_open and tank_ready_to_spawn is not None and cur_player.base != 0: # установка выбранного танка
            keys_clicked[32] = 0
            dist_spawn0 = ((int(cur_player.base.sprites()[0].x) / len_cell - cell_mouse_pos[0]) ** 2
                           + (int(cur_player.base.sprites()[0].y) / len_cell - cell_mouse_pos[1]) ** 2) ** 0.5
            if (dist_spawn0 <= dist_spawn and cur_player.res >= tank_ready_to_spawn.ttx[12]
                    and cur_player.exp >= tank_ready_to_spawn.ttx[13] and map[cell_mouse_pos[1], cell_mouse_pos[0]] == 0):
                scripts.functions.spawn_team_obj(
                    map, scripts.tank.Tank, 2, all_tanks, cur_player.tanks,
                    cell_mouse_pos, cur_player.n, 1, tank_ready_to_spawn.ttx,
                    cur_player, scripts.mist.Mist, map)
                cur_player.res -= tank_ready_to_spawn.ttx[-4]
                cur_player.mists.empty()
                cur_player.mist_matrix = scripts.functions.mist_doting3000(cur_player.tanks)
                scripts.functions.mist_builder(cur_player.mist_matrix, scripts.mist.Mist, cur_player.mists)
                cur_player.mist_matrix[cur_player.base.sprites()[0].place[1], cur_player.base.sprites()[0].place[0]] = 1
                tank_ready_to_spawn = None

        if keys_clicked[32] == 1 and b_turn.rect.collidepoint(r_m_pos) and cur_player.base != 0: # смена хода
            keys_clicked[32] = 0
            if cnt_rounds//QNT_PLAYERS != 0:
                cur_player.exp += scripts.functions.cell_distribution(QNT_PLAYERS, cur_player.n, all_tanks)
                cur_player.res += scripts.functions.get_res(len(cur_player.tanks.sprites()))
            cur_player.tanks.update()
            active_player += 1
            active_player %= QNT_PLAYERS
            cur_player = players[active_player]
            taken_tank = None
            tank_ready_to_spawn = None
            selected_tank = None
            market_window.empty()
            all_selected_map.empty()
            cnt_rounds += 1

        if keys_clicked[32] == 1 and 0<=cell_mouse_pos[0]<map_len_cells and 0<=cell_mouse_pos[1]<map_len_cells and not market_window_is_open: # выбор клетки
            keys_clicked[32] = 0
            selected_tank = None
            all_selected_map.empty()
            select_cell = scripts.selectedcell.Selectedcell(len_cell * cell_mouse_pos[0], len_cell * cell_mouse_pos[1])
            all_selected_map.add(select_cell)
            if map[cell_mouse_pos[1], cell_mouse_pos[0]] == 2:
                for tank in all_tanks:
                    if tank.place[0] == cell_mouse_pos[0] and tank.place[1] == cell_mouse_pos[1]: # выбор танка на клетке
                        if tank.team == cur_player.n:
                            selected_tank = tank
                        break

        if selected_tank is not None: # управление танком
            selected_tank.move(keys_clicked[0], keys_clicked[1], keys_clicked[2], keys_clicked[3], select_cell)
            if keys_clicked[0] or keys_clicked[1] or keys_clicked[2] or keys_clicked[3]:
                cur_player.mists.empty()
                cur_player.mist_matrix = scripts.functions.mist_doting3000(cur_player.tanks)
                scripts.functions.mist_builder(cur_player.mist_matrix, scripts.mist.Mist, cur_player.mists)
                cur_player.mist_matrix[cur_player.base.sprites()[0].place[1], cur_player.base.sprites()[0].place[0]] = 1
            keys_clicked[0] = 0
            keys_clicked[1] = 0
            keys_clicked[2] = 0
            keys_clicked[3] = 0
            if keys_clicked[8] == 1:
                keys_clicked[8] = 0
                selected_tank.shot(all_projectiles, dest_mouse_pos, scripts.projectile.Projectile)
            if keys[12] == 1:
                map[selected_tank.place[1], selected_tank.place[0]] = 0
                selected_tank.kill()
                selected_tank = None
                cur_player.mists.empty()
                cur_player.mist_matrix = scripts.functions.mist_doting3000(cur_player.tanks)
                scripts.functions.mist_builder(cur_player.mist_matrix, scripts.mist.Mist, cur_player.mists)
                cur_player.mist_matrix[cur_player.base.sprites()[0].place[1], cur_player.base.sprites()[0].place[0]] = 1
        else:  # управление камерой если не выбран танк
            cur_player.move(keys[0], keys[1], keys[2], keys[3])
            keys_clicked[0] = 0
            keys_clicked[1] = 0
            keys_clicked[2] = 0
            keys_clicked[3] = 0
            keys_clicked[8] = 0

        if keys_clicked[11] == 1:
            keys_clicked[11] = 0
            scene = "menu"
            all_walls.empty()
            all_cells.empty()
            all_selected_map.empty()
            all_tanks.empty()
            all_bases.empty()
            all_buttons_menu.empty()
            to_build_map = True
            players_registered = False
            to_build_game_buttons = True
            selected_tank = None
            taken_tank = None
            tank_ready_to_spawn = None
            players = []
            active_player = 0
            cnt_rounds = 0

        canvas_hp = scripts.surface.Surface(SW/64, (SH*(1/4+5/800)) + SH*(1/4-5/800)*(cur_player.hp/base_hp), SW/32 - SW*10/1280, (SH/2 - SW*10/1280)*(cur_player.hp/base_hp),
                                            (128+(team_to_color[cur_player.n][0]-128)*(cur_player.hp/base_hp),
                                             128+(team_to_color[cur_player.n][1]-128)*(cur_player.hp/base_hp),
                                             128+(team_to_color[cur_player.n][2]-128)*(cur_player.hp/base_hp)), 0, 0, 0)
        text_turns = font48.render(f"Turn: {cnt_rounds//QNT_PLAYERS + 1}", True, team_to_color[cur_player.n])
        text_res = font48.render(f"Resources : {cur_player.res}", True, team_to_color[cur_player.n])
        text_exp = font48.render(f"Сapture : {cur_player.exp}", True, team_to_color[cur_player.n])
        # all_projectiles.update(all_walls, all_tanks, player.tanks, all_bases)
        for projectile in all_projectiles:
            dam = projectile.update(all_walls, all_tanks, cur_player.tanks, all_bases)
            if dam != 0:
                dam_text = font32.render(f"{int(dam)}", True, team_to_color[projectile.team])
                dam_dest = projectile.x, projectile.y
                damage_text_timelive = FPS
        virtual_screen.fill((255, 255, 255))
        screen.fill((255, 255, 255))
        cur_player.mists.draw(virtual_screen)
        all_cells.draw(virtual_screen)
        for tank in all_tanks:
            if cur_player.mist_matrix[tank.place[1], tank.place[0]] > 0:
                tank.draw(virtual_screen, cur_player.n)
        for base in all_bases:
            if cur_player.mist_matrix[base.place[1], base.place[0]] > 0:
                base.draw(virtual_screen)
        all_projectiles.draw(virtual_screen)
        all_walls.draw(virtual_screen)
        all_selected_map.draw(virtual_screen)
        if damage_text_timelive > 0:
            virtual_screen.blit(dam_text, dam_dest)
            damage_text_timelive -= 1
        dest = (-cur_player.place[0], -cur_player.place[1] )
        screen.blit(virtual_screen, dest)
        all_buttons_game.draw(screen)
        market_window.draw(screen)
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