# хуй пися члеен
import pygame as pg
import scripts
import maps
from settings import *
from ttc import *

pg.init()
pg.mixer.init()

# screen = pg.display.set_mode((SW, SH), pg.FULLSCREEN,  vsync=1)
screen = pg.display.set_mode((SW, SH), vsync=1)

text_start = font48.render("Proceed", True, (0, 0, 0))

pg.display.set_caption("meme")
clock = pg.time.Clock()

all_walls = pg.sprite.LayeredDirty()
map_matrix = np.empty((map_len_cells, map_len_cells), dtype=object)

all_cells = pg.sprite.LayeredDirty()
map_matrix = np.empty((map_len_cells, map_len_cells), dtype=object)

all_selected_cells = pg.sprite.LayeredDirty()
all_selected_in_window = pg.sprite.LayeredDirty()
all_selected_taken_in_window = pg.sprite.LayeredDirty()
all_tanks = pg.sprite.LayeredDirty()
all_bases = pg.sprite.LayeredDirty()
all_buttons_menu = pg.sprite.LayeredDirty()
all_buttons_game = pg.sprite.LayeredDirty()
all_projectiles = pg.sprite.LayeredDirty()
market_window = pg.sprite.LayeredDirty()
market_ui_tanks = pg.sprite.LayeredDirty()

all_sprites = pg.sprite.LayeredDirty(_time_threshold = 666)

virtual_screen_size = map_len_cells * len_cell

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
# selected_tank = False
to_regist_players = True # некит переименуй   #+
taken_tank = False # некит переименуй   #+
ready_to_spawn_tank = False
drop_the_curtain = False
select_cell = None
canvas_dam = None

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

old_fps_val = 0 # для вывода FPS


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
            b_start.image.blit(text_start, (b_start.size[0]/6, b_start.size[1]/3))
            all_buttons_menu.add(b_start)
            to_build_menu = False
            screen.fill((255, 255, 255))
            background = screen.copy()
        if keys_clicked[11] == 1:
            running = False

        all_buttons_menu.draw(screen, background)

        if keys_clicked[32] == 1 and b_start.rect.collidepoint(r_m_pos):
            keys_clicked[32] = 0
            scene = "game"
            to_build_menu = True
            all_buttons_menu.empty()

    elif scene == "game":
        if to_build_map:
            map = maps.squares.map.copy()
            scripts.functions.builder(map, scripts.cell.Cell, 0, all_cells, all_sprites, map_matrix)
            scripts.functions.builder(map, scripts.wall.Wall, 1, all_walls, all_sprites, map_matrix)
            map_screen = pg.Surface((virtual_screen_size, virtual_screen_size))
            background = map_screen.copy()
            all_cells.draw(background, background)
            all_walls.draw(background, background)

            to_build_map = False

        if drop_the_curtain == True and keys_clicked[32] == 1:
            keys_clicked[32] = 0
            drop_the_curtain = False

        if to_build_game_buttons:
            b_turn = scripts.button.Button(SW*15/16, SH*15/16,SW*1/8, SH*1/8, (0,255,255))
            b_turn.edges((255,128,0), 5)
            b_turn.dirty = 2
            canvas0 = scripts.surface.Surface(SW/2, SH*3/80, SW*15/64, SH*8/80, (128,128,128), 1, select_color,  int(SW*2/1280))
            canvas1 = scripts.surface.Surface(SW*15/16, SH*13.5/16, SW*1/8, SH*1/16, (128,128,128), 1, (255,128,0), int(SW*5/1280))
            canvas_for_hp = scripts.surface.Surface(SW/64, SH/2, SW/32, SH/2, (255,255,255), 1, (255,128,0), int(SW*5/1280))
            all_buttons_game.add(b_turn)
            to_build_game_buttons = False

        if not players_registered:   # регистрация игроков
            for i in range(QNT_PLAYERS):
                players.append(scripts.player.Player(i, res0))
            cur_player = players[active_player]
            players_registered = True

        # координаты  мыщки сдвинутые на dest (смещение камеры игрока) снизу написал все
        dest_mouse_pos = (cur_player.place[0] + r_m_pos[0], cur_player.place[1] + r_m_pos[1])   # положение мыши на карте
        cell_mouse_pos = (int(dest_mouse_pos[0] // len_cell) , int(dest_mouse_pos[1] // len_cell)) # положение мыши на карте в количестве полных клеток

        if cur_player.base == None and not b_turn.rect.collidepoint(r_m_pos): # установка базы игрока
            if (keys_clicked[32] == 1 and 0<=cell_mouse_pos[0]<map_len_cells and 0<=cell_mouse_pos[1]<map_len_cells
                    and map[cell_mouse_pos[1], cell_mouse_pos[0]] == 0):
                keys_clicked[32] = 0
                cur_player.base = pg.sprite.Group()
                scripts.functions.spawn_team_obj(
                    map, scripts.base.Base, 3, all_bases, cur_player.base, all_sprites, cell_mouse_pos, cur_player.team, cur_player
                    )
                cur_player.mist_matrix[cur_player.base.sprites()[0].place[1], cur_player.base.sprites()[0].place[0]] = 1 # делаю видимым положение в которое только что поставил базу
                cur_player.hp = cur_player.base.sprites()[0].hp
                mist_sprites = map_matrix[np.where(cur_player.mist_matrix == 1)]


        if (keys_clicked[32] == 1 and cur_player.base != None and cur_player.base.sprites()[0].place[0] == cell_mouse_pos[0]
                and cur_player.base.sprites()[0].place[1] == cell_mouse_pos[1]) and market_window_is_open == False: # меню выбора танков
            keys_clicked[32] = 0
            tank_menu =  scripts.button.Button(SW/2, SH/2, SW/2, SH/2, (66,66,66))
            tank_menu.dirty = 2
            tank_menu.edges((255,128,0), 5)
            market_window.add(tank_menu)
            for j, tank_for_menu in enumerate(alpha):
                x = j%3
                y = j//3
                market_ui_tanks.add(scripts.img_tank.ImgTank(SW / 2 - SW / 8 + x * SW / 8 - len_cell / 2,
                                                                  SH / 2 - SH / 8 + y * SH / 8 - len_cell / 2, cur_player.team, 0, tank_for_menu))
            market_window.add(market_ui_tanks)
            ext = scripts.button.Button(SW*3/4-SW/32, SH/4+SH/32, SW/16, SH/16, (200,0,0))
            ext.edges((0,255,255), 5)
            ext.dirty = 2
            b_take = scripts.button.Button(SW*3/4-SW/32, SH*3/4+SH/32, SW/16, SH/16, (128,255,128))
            b_take.edges((0,128,0), 5)
            b_take.dirty = 2
            b_throw = scripts.button.Button(SW*3/4-SW/32-SW/16, SH*3/4+SH/32, SW/16, SH/16, (255,255,128))
            b_throw.edges((128,128,0), 5)
            b_throw.dirty = 2
            canvas_ttc = scripts.surface.Surface(SW/32, SH/4, SW*7/32, SH/2, (255, 255, 255), 1,
                                                 (255, 128, 0), int(SW * 5 / 1280))
            canvas_ttc.dirty = 2
            market_window.add(ext, b_take, b_throw, canvas_ttc)

            market_window_is_open = True

        if market_window_is_open: # выбор танков в соответственном меню
            if keys_clicked[32] == 1:
                keys_clicked[32] = 0
                for tank in market_ui_tanks:
                    if tank.rect.collidepoint(r_m_pos):
                        market_window.remove(all_selected_in_window)
                        all_selected_in_window.empty()
                        taken_tank = tank
                        canvas_ttc.kill()

                        text_ttc = font48.render(f"TTC:", True, (0, 0, 0))
                        text_vis = font32.render(f"Distance of visible : {taken_tank.ttx[0]}", True, (0, 0, 0))
                        text_hp = font32.render(f"Healf points : {taken_tank.ttx[1]}", True, (0, 0, 0))
                        text_a = font32.render(f"Armor: {taken_tank.ttx[2]}, {taken_tank.ttx[3]}, {taken_tank.ttx[4]}", True, (0, 0, 0))
                        text_m = font32.render(f"Mobility: {taken_tank.ttx[5]}, {taken_tank.ttx[6]}, {taken_tank.ttx[7]}", True, (0, 0, 0))
                        text_dam = font32.render(f"Damage: {taken_tank.ttx[8]}", True, (0, 0, 0))
                        text_pen = font32.render(f"Penedration: {taken_tank.ttx[9]}", True, (0, 0, 0))
                        text_rel = font32.render(f"Reloading: {taken_tank.ttx[10]}", True, (0, 0, 0))
                        text_dist = font32.render(f"Fire distance: {taken_tank.ttx[11]}", True, (0, 0, 0))

                        canvas_ttc = scripts.surface.Surface(SW / 32, SH / 4, SW * 7 / 32, SH / 2, (255, 255, 255), 1,
                                                             (255, 128, 0), int(SW * 5 / 1280))
                        canvas_ttc.dirty = 2
                        canvas_ttc.image.blit(text_ttc, (10,10))
                        canvas_ttc.image.blit(text_vis, (10, 10+32))
                        canvas_ttc.image.blit(text_hp, (10, 10+32+32))
                        canvas_ttc.image.blit(text_a, (10, 10+32+32*2))
                        canvas_ttc.image.blit(text_m, (10, 10 + 32 + 32 * 3))
                        canvas_ttc.image.blit(text_dam, (10, 10 + 32 + 32 * 4))
                        canvas_ttc.image.blit(text_pen, (10, 10 + 32 + 32 * 5))
                        canvas_ttc.image.blit(text_rel, (10, 10 + 32 + 32 * 6))
                        canvas_ttc.image.blit(text_dist, (10, 10 + 32 + 32 * 7))

                        market_window.add(canvas_ttc)

                        select_place = scripts.selectedcell.Selectedcell(tank.x, tank.y)
                        select_place.dirty = 2
                        all_selected_in_window.add(select_place)
                        b_take.edges((0, 128, 0), 5)
                        b_throw.edges((128, 128, 0), 5)
                    market_window.add(all_selected_in_window)
                if b_take.rect.collidepoint(r_m_pos) and taken_tank is not None:
                    b_take.edges((0, 255, 255), 5)
                    b_throw.edges((128, 128, 0), 5)
                    tank_ready_to_spawn = taken_tank
                if b_throw.rect.collidepoint(r_m_pos) and tank_ready_to_spawn is not None:

                    all_selected_taken_in_window.empty()
                    select_place.change_color((255, 128, 0))
                    all_selected_taken_in_window.add(select_place)
                    market_window.remove(all_selected_in_window)
                    all_selected_in_window.empty()

                    tank_ready_to_spawn = taken_tank

                if b_throw.rect.collidepoint(r_m_pos) and tank_ready_to_spawn is not None:
                    b_throw.edges((0, 255, 255), 5)
                    b_take.edges((0, 128, 0), 5)
                    tank_ready_to_spawn = None

                    all_selected_taken_in_window.empty()

                if ext.rect.collidepoint(r_m_pos):
                    market_window.empty()
                    all_selected_in_window.empty()
                    all_selected_taken_in_window.empty()
                    taken_tank = None
                    market_window_is_open = False

        if keys_clicked[32] == 1 and not market_window_is_open and tank_ready_to_spawn is not None and cur_player.base != None: # установка выбранного танка
            keys_clicked[32] = 0
            dist_spawn0 = ((int(cur_player.base.sprites()[0].x) / len_cell - cell_mouse_pos[0]) ** 2
                           + (int(cur_player.base.sprites()[0].y) / len_cell - cell_mouse_pos[1]) ** 2) ** 0.5
            if (dist_spawn0 <= dist_spawn and cur_player.res >= tank_ready_to_spawn.ttx[12]
                    and cur_player.exp >= tank_ready_to_spawn.ttx[13] and map[cell_mouse_pos[1], cell_mouse_pos[0]] == 0):
                scripts.functions.spawn_team_obj(
                    map, scripts.tank.Tank, 2, all_tanks, cur_player.tanks, all_sprites,
                    cell_mouse_pos, cur_player.team, 1, tank_ready_to_spawn.ttx,
                    cur_player, scripts.mist.Mist, map)
                cur_player.res -= tank_ready_to_spawn.ttx[-4]

                cur_player.mist_matrix = scripts.functions.mist_doting3000(cur_player.tanks,
                                                                           cur_player.base, map_matrix, all_tanks, all_bases, cur_player.team)

                tank_ready_to_spawn = None

        if (keys_clicked[32] == 1 and b_turn.rect.collidepoint(r_m_pos) and cur_player.base != 0): # смена хода
            keys_clicked[32] = 0
            if cnt_rounds//QNT_PLAYERS != 0:
                cur_player.exp += scripts.functions.cell_distribution(QNT_PLAYERS, cur_player.team, all_tanks)
                cur_player.res += scripts.functions.get_res(len(cur_player.tanks.sprites()))
            cur_player.tanks.update()
            for tank in all_tanks:
                tank.drowed_stats = False
            active_player = (active_player + 1) % QNT_PLAYERS
            cur_player = players[active_player]
            cur_player.mist_matrix = scripts.functions.mist_doting3000(cur_player.tanks, cur_player.base,
                                                                       map_matrix, all_tanks, all_bases, cur_player.team)
            if damage_text_timelive > 0:
                damage_text_timelive = 1
            if select_cell != None:
                select_cell.kill()
                select_cell = None
            taken_tank = None
            tank_ready_to_spawn = None
            selected_tank = None
            drop_the_curtain = True
            market_window.empty()
            all_selected_cells.empty()
            cnt_rounds += 1

        if keys_clicked[32] == 1 and 0<=cell_mouse_pos[0]<map_len_cells and 0<=cell_mouse_pos[1]<map_len_cells and not market_window_is_open: # выбор клетки
            keys_clicked[32] = 0
            if select_cell == None:
                select_cell = scripts.selectedcell.Selectedcell(len_cell * cell_mouse_pos[0],
                                                            len_cell * cell_mouse_pos[1])
                all_selected_cells.add(select_cell)
                all_sprites.add(select_cell)
            else:
                select_cell.go_to(len_cell * cell_mouse_pos[0],
                                len_cell * cell_mouse_pos[1])
                select_cell.dirty = 1
            selected_tank = None

            if map[cell_mouse_pos[1], cell_mouse_pos[0]] == 2:
                for tank in all_tanks:
                    if tank.place[0] == cell_mouse_pos[0] and tank.place[1] == cell_mouse_pos[1]: # выбор танка на клетке
                        if tank.team == cur_player.team:
                            selected_tank = tank
                        break

        if selected_tank is not None: # управление танком
            if keys_clicked[0] or keys_clicked[1] or keys_clicked[2] or keys_clicked[3]:
                selected_tank.move(keys_clicked[0], keys_clicked[1], keys_clicked[2], keys_clicked[3], select_cell)

                cur_player.mist_matrix = scripts.functions.mist_doting3000(cur_player.tanks,
                                                                           cur_player.base, map_matrix, all_tanks, all_bases, cur_player.team)
                keys_clicked[0] = 0
                keys_clicked[1] = 0
                keys_clicked[2] = 0
                keys_clicked[3] = 0

            if keys_clicked[8] == 1:
                keys_clicked[8] = 0
                selected_tank.shot(all_projectiles, all_sprites, dest_mouse_pos, scripts.projectile.Projectile)
            if keys[12] == 1:
                map[selected_tank.place[1], selected_tank.place[0]] = 0
                selected_tank.kill()
                selected_tank = None
                cur_player.mist_matrix = scripts.functions.mist_doting3000(cur_player.tanks,
                                                                           cur_player.base, map_matrix, all_tanks,
                                                                           all_bases, cur_player.team)
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
            all_sprites.empty()
            all_selected_cells.empty()
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
            continue

        for tank in all_tanks:
            tank.draw_stats(cur_player.team)

        canvas_hp = scripts.surface.Surface(SW/64+1, (SH*(1/4+5/800)) + SH*(1/4-5/800)*(cur_player.hp/base_hp), SW/32 - SW*10/1280-1, (SH/2 - SW*10/1280)*(cur_player.hp/base_hp),
                                            (128+(team_to_color[cur_player.team][0]-128)*(cur_player.hp/base_hp),
                                             128+(team_to_color[cur_player.team][1]-128)*(cur_player.hp/base_hp),
                                             128+(team_to_color[cur_player.team][2]-128)*(cur_player.hp/base_hp)), 0, 0, 0)
        text_turns = font48.render(f"Turn: {cnt_rounds//QNT_PLAYERS + 1}", True, team_to_color[cur_player.team])
        text_res = font48.render(f"Resources : {cur_player.res}", True, team_to_color[cur_player.team])
        text_exp = font48.render(f"Сapture : {cur_player.exp}", True, team_to_color[cur_player.team])

        for projectile in all_projectiles:
            dam = projectile.update(all_walls, all_tanks, cur_player.tanks, all_bases, map_matrix)
            if dam != 0:
                dam_text = font32.render(f"{int(dam)}", True, team_to_color[projectile.team])
                dam_dest = projectile.x, projectile.y
                damage_text_timelive = FPS*3
                if canvas_dam != None:
                    canvas_dam.kill()
                canvas_dam = scripts.surface.Surface(projectile.x, projectile.y, SW/24,
                                            SH/32, (255, 255, 255), 1, (0,0,0), 2)
                canvas_dam.image.blit(dam_text, (SW/256,SH/256))
                all_sprites.add(canvas_dam)

        if damage_text_timelive > 0:
            damage_text_timelive -= 1
            if damage_text_timelive <= 0:
                canvas_dam.kill()

        all_sprites.draw(map_screen, background)

        dest = (-cur_player.place[0], -cur_player.place[1] )
        screen.blit(map_screen, dest)

        all_buttons_game.draw(screen)
        market_window.draw(screen)
        all_selected_taken_in_window.draw(screen)

        canvas0.draw(screen)
        canvas1.draw(screen)
        canvas_for_hp.draw(screen)

        canvas_hp.draw(screen)
        screen.blit(text_res, (SW/2-SW*7/64, 0))
        screen.blit(text_exp, (SW/2-SW*7/64, SH*3/80))
        screen.blit(text_turns, (SW*14/16 + SW*2/256, SH*14/16 - SW/32))
        if drop_the_curtain == True:
            screen.fill((66, 66, 66))
    

    if old_fps_val != clock.get_fps():
        print(clock.get_fps())
        old_fps_val = clock.get_fps()

    clock.tick(FPS)
    pg.display.flip()

pg.quit()
