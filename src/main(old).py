import pygame as pg
import numpy as np

from . import core, data, obj, ui, utils
from .core.settings import *

pg.init()
pg.mixer.init()

# screen = pg.display.set_mode((SW, SH), pg.FULLSCREEN, vsync=1)
screen = pg.display.set_mode((SW, SH), vsync=1)

text_start = font48.render("Proceed", True, (0, 0, 0))

pg.display.set_caption("meme")
clock = pg.time.Clock()

all_walls = pg.sprite.LayeredDirty()
all_cells = pg.sprite.LayeredDirty()
map_matrix = np.empty((map_len_cells, map_len_cells), dtype=object)

all_selected_cells = pg.sprite.LayeredDirty()
all_selected_in_market = pg.sprite.LayeredDirty()
all_taken_in_market = pg.sprite.LayeredDirty()
all_tanks = pg.sprite.LayeredDirty()
all_bases = pg.sprite.LayeredDirty()
all_buttons_menu = pg.sprite.LayeredDirty()
all_buttons_game = pg.sprite.LayeredDirty()
all_projectiles = pg.sprite.LayeredDirty()
market_window = pg.sprite.LayeredDirty()
market_ui_tanks = pg.sprite.LayeredDirty()

all_sprites = pg.sprite.LayeredDirty(_time_threshold = float("inf"))

virtual_screen_size = map_len_cells * len_cell

players: list[core.player.Player] = []

running = True
scene = "menu"

map_is_builded = False
menu_is_builded = False
game_buttons_is_builded = False
selected_tank = None
players_is_init = False
taken_tank_menu = None
tank_ready_to_spawn = None
curtain_is_raisen = False
select_cell = None
damage_window = None

market_is_open = False

USING_KEYS = (pg.K_w, pg.K_a, pg.K_s, pg.K_d, pg.K_k, pg.K_l,
            pg.K_e, pg.K_r, pg.K_SPACE, pg.K_t, pg.K_b,
            pg.K_ESCAPE, pg.K_q)
keys_click = {i: False for i in USING_KEYS}
MOUSE_LMB = 1
USING_MOUSE_BUTTONS = {MOUSE_LMB}
mouse_click = {i: False for i in USING_MOUSE_BUTTONS}

active_player = 0
QNT_PLAYERS = 2
cnt_rounds = 0
damage_text_timelive = 0

old_fps_val = 0 # для вывода FPS


while running:
    real_mouse_pos = pg.mouse.get_pos()
    for event in pg.event.get():
        match event.type:
            case pg.QUIT:
                running = False

            case pg.KEYDOWN:
                keys_click[event.key] = True

            case pg.MOUSEBUTTONDOWN:
                mouse_click[event.button] = True

    if scene == "menu":
        if not menu_is_builded:
            b_start = ui.uipanel.UIPanel(SW/2 - SW/16, SH/2 - SH/16, SW/8, SH/8, (0,255,255), 1, (255,128,0), 5)
            # b_start.edges((255,128,0), 5)
            b_start.image.blit(text_start, (b_start.size[0]/16, b_start.size[1]/3))
            all_buttons_menu.add(b_start)
            menu_is_builded = True
            screen.fill((255, 255, 255))
            background = screen.copy()
        if keys_click[pg.K_ESCAPE]:
            running = False

        all_buttons_menu.draw(screen, background)

        if mouse_click[MOUSE_LMB] and b_start.rect.collidepoint(real_mouse_pos):
            mouse_click[MOUSE_LMB] = False
            scene = "game"
            menu_is_builded = False
            all_buttons_menu.empty()

    elif scene == "game":
        if not map_is_builded:
            tile_map = data.maps.squares.tile_map.copy() # тайловая карта - по сетке
            utils.functions.builder(tile_map, obj.cell.Cell, 0, all_cells, all_sprites, map_matrix)
            utils.functions.builder(tile_map, obj.wall.Wall, 1, all_walls, all_sprites, map_matrix)
            map_screen = pg.Surface((virtual_screen_size, virtual_screen_size))
            background = map_screen.copy()
            all_cells.draw(background, background)
            all_walls.draw(background, background)

            map_is_builded = True

        if curtain_is_raisen and mouse_click[MOUSE_LMB]:
            mouse_click[MOUSE_LMB] = False
            curtain_is_raisen = False

        if not game_buttons_is_builded:
            button_turn_switch = ui.uipanel.UIPanel(SW*15/16 - SW/16, SH*15/16 - SH/16, SW*1/8, SH*1/8, (0,255,255), 1, (255,128,0), 5)
            # button_turn_switch.edges((255,128,0), 5)
            button_turn_switch.dirty = 2
            panel_resources = ui.uipanel.UIPanel(SW/2, SH*3/80, SW*15/64, SH*8/80, (128,128,128), 1, color_select, int(SW*2/1280))
            panel_cnt_turns = ui.uipanel.UIPanel(SW*15/16, SH*13.5/16, SW*1/8, SH*1/16, (128,128,128), 1, (255,128,0), int(SW*5/1280))
            panel_hp = ui.uipanel.UIPanel(SW/64, SH/2, SW/32, SH/2, (255,255,255), 1, (255,128,0), int(SW*5/1280))
            all_buttons_game.add(button_turn_switch)
            game_buttons_is_builded = True

        if not players_is_init: # регистрация игроков
            for i in range(QNT_PLAYERS):
                players.append(core.player.Player(i, INITIAL_RESOURCES))
            cur_player = players[active_player]
            players_is_init = True

        # координаты мыщки сдвинутые на dest (смещение камеры игрока) снизу написал все
        world_mouse_pos = utils.functions.get_world_mouse_pos(cur_player, real_mouse_pos) # положение мыши на карте
        cell_mouse_pos = utils.functions.get_cell_mouse_pos(world_mouse_pos, len_cell) # положение мыши на карте в количестве полных клеток

        if cur_player.base is None and not button_turn_switch.rect.collidepoint(real_mouse_pos): # установка базы игрока
            if (mouse_click[MOUSE_LMB] and 0<=cell_mouse_pos[0]<map_len_cells and 0<=cell_mouse_pos[1]<map_len_cells
                    and tile_map[cell_mouse_pos[1], cell_mouse_pos[0]] == 0):
                mouse_click[MOUSE_LMB] = False
                cur_player.base = pg.sprite.Group()
                utils.functions.spawn_team_obj(
                    tile_map, obj.base.Base, 3, all_bases, cur_player.base, all_sprites, cell_mouse_pos, cur_player.team, cur_player
                    )
                cur_player.mist_matrix[cur_player.base.sprites()[0].place[1], cur_player.base.sprites()[0].place[0]] = 1 # делаю видимым положение в которое только что поставил базу
                cur_player.hp = cur_player.base.sprites()[0].hp
                mist_sprites = map_matrix[np.where(cur_player.mist_matrix == 1)]


        if (mouse_click[MOUSE_LMB] and cur_player.base is not None and cur_player.base.sprites()[0].place[0] == cell_mouse_pos[0]
                and cur_player.base.sprites()[0].place[1] == cell_mouse_pos[1]) and market_is_open == False: # меню выбора танков
            mouse_click[MOUSE_LMB] = False
            tank_menu = ui.uipanel.UIPanel(SW/4, SH/4, SW/2, SH/2, (66,66,66), 1, (255,128,0), 5)
            tank_menu.dirty = 2
            # tank_menu.edges((255,128,0), 5)
            market_window.add(tank_menu)
            for j, tank_for_menu in enumerate(data.ttc.default_combination):
                x = j%3
                y = j//3
                market_ui_tanks.add(ui.img_tank.ImgTank(SW / 2 - SW / 8 + x * SW / 8 - len_cell / 2,
                                                                  SH / 2 - SH / 8 + y * SH / 8 - len_cell / 2, cur_player.team, 0, tank_for_menu))
            market_window.add(market_ui_tanks)
            button_exit_market = ui.uipanel.UIPanel(SW*3/4-SW/16, SH/4, SW/16, SH/16, (200,0,0), 1, (0,255,255), 5)
            # ext.edges((0,255,255), 5)
            button_exit_market.dirty = 2
            button_confirm = ui.uipanel.UIPanel(SW*3/4-SW/16, SH*3/4, SW/16, SH/16, (128,255,128), 1, (0,128,0), 5)
            # b_take.edges((0,128,0), 5)
            button_confirm.dirty = 2
            button_drop_confirm = ui.uipanel.UIPanel(SW*3/4-SW/8, SH*3/4, SW/16, SH/16, (255,255,128), 1, (128,128,0), 5)
            # b_throw.edges((128,128,0), 5)
            button_drop_confirm.dirty = 2
            panel_ttc = ui.uipanel.UIPanel(SW/32, SH/4, SW*7/32, SH/2, (255, 255, 255), 1,
                                            (255, 128, 0), int(SW * 5 / 1280))
            panel_ttc.dirty = 2
            market_window.add(button_exit_market, button_confirm, button_drop_confirm, panel_ttc)

            market_is_open = True

        if market_is_open: # выбор танков в соответственном меню
            if mouse_click[MOUSE_LMB]:
                mouse_click[MOUSE_LMB] = False
                for ui_tank in market_ui_tanks:
                    if ui_tank.rect.collidepoint(real_mouse_pos):
                        market_window.remove(all_selected_in_market)
                        all_selected_in_market.empty()
                        taken_tank_menu = ui_tank
                        panel_ttc.kill()

                        text_ttc = (
                            font48.render(f"TTC:", True, (0, 0, 0)),
                            font32.render(f"Distance of visible : {taken_tank_menu.ttx[0]}", True, (0, 0, 0)),
                            font32.render(f"Healf points : {taken_tank_menu.ttx[1]}", True, (0, 0, 0)),
                            font32.render(f"Armor: {taken_tank_menu.ttx[2]}, {taken_tank_menu.ttx[3]}, {taken_tank_menu.ttx[4]}", True, (0, 0, 0)),
                            font32.render(f"Mobility: {taken_tank_menu.ttx[5]}, {taken_tank_menu.ttx[6]}, {taken_tank_menu.ttx[7]}", True, (0, 0, 0)),
                            font32.render(f"Damage: {taken_tank_menu.ttx[8]}", True, (0, 0, 0)),
                            font32.render(f"Penedration: {taken_tank_menu.ttx[9]}", True, (0, 0, 0)),
                            font32.render(f"Reloading: {taken_tank_menu.ttx[10]}", True, (0, 0, 0)),
                            font32.render(f"Fire distance: {taken_tank_menu.ttx[11]}", True, (0, 0, 0)),
                        )

                        panel_ttc = ui.uipanel.UIPanel(SW / 32, SH / 4, SW * 7 / 32, SH / 2, (255, 255, 255), 1,
                                                             (255, 128, 0), int(SW * 5 / 1280))
                        panel_ttc.dirty = 2
                        text_indentation = 10
                        for characteristic_text in text_ttc:
                            panel_ttc.image.blit(characteristic_text, (10, text_indentation))
                            text_indentation += 32

                        # panel_ttc.image.blit(text_ttc, (10,10))
                        # panel_ttc.image.blit(text_vis, (10, 10+32))
                        # panel_ttc.image.blit(text_hp, (10, 10+32+32))
                        # panel_ttc.image.blit(text_a, (10, 10+32+32*2))
                        # panel_ttc.image.blit(text_m, (10, 10 + 32 + 32 * 3))
                        # panel_ttc.image.blit(text_dam, (10, 10 + 32 + 32 * 4))
                        # panel_ttc.image.blit(text_pen, (10, 10 + 32 + 32 * 5))
                        # panel_ttc.image.blit(text_rel, (10, 10 + 32 + 32 * 6))
                        # panel_ttc.image.blit(text_dist, (10, 10 + 32 + 32 * 7))

                        market_window.add(panel_ttc)

                        select_place = ui.cell_border.CellBorder(ui_tank.x, ui_tank.y)
                        select_place.dirty = 2
                        select_place.layer = LAYER_UI_SELECTION
                        all_selected_in_market.add(select_place)
                        button_confirm.edges((0, 128, 0), 5)
                        button_drop_confirm.edges((128, 128, 0), 5)
                    market_window.add(all_selected_in_market)
                if button_confirm.rect.collidepoint(real_mouse_pos) and taken_tank_menu is not None:
                    button_confirm.edges((0, 255, 255), 5)
                    button_drop_confirm.edges((128, 128, 0), 5)
                    tank_ready_to_spawn = taken_tank_menu
                    select_place.change_color((255, 128, 0))
                if button_drop_confirm.rect.collidepoint(real_mouse_pos) and tank_ready_to_spawn is not None:

                    all_taken_in_market.empty()
                    select_place.change_color((255, 128, 0))
                    all_taken_in_market.add(select_place)
                    market_window.remove(all_selected_in_market)
                    all_selected_in_market.empty()

                    tank_ready_to_spawn = taken_tank_menu

                if button_drop_confirm.rect.collidepoint(real_mouse_pos) and tank_ready_to_spawn is not None:
                    button_drop_confirm.edges((0, 255, 255), 5)
                    button_confirm.edges((0, 128, 0), 5)
                    tank_ready_to_spawn = None

                    all_taken_in_market.empty()

                if button_exit_market.rect.collidepoint(real_mouse_pos):
                    market_window.empty()
                    all_selected_in_market.empty()
                    all_taken_in_market.empty()
                    taken_tank_menu = None
                    market_is_open = False

        if mouse_click[MOUSE_LMB] and not market_is_open and tank_ready_to_spawn is not None and cur_player.base is not None: # установка выбранного танка
            mouse_click[MOUSE_LMB] = False
            dist_spawn0 = ((int(cur_player.base.sprites()[0].x) / len_cell - cell_mouse_pos[0]) ** 2
                           + (int(cur_player.base.sprites()[0].y) / len_cell - cell_mouse_pos[1]) ** 2) ** 0.5
            if (dist_spawn0 <= max_spawn_distance and cur_player.resources >= tank_ready_to_spawn.ttx[12]
                    and cur_player.exp >= tank_ready_to_spawn.ttx[13] and tile_map[cell_mouse_pos[1], cell_mouse_pos[0]] == 0):
                utils.functions.spawn_team_obj(
                    tile_map, obj.tank.Tank, 2, all_tanks, cur_player.tanks, all_sprites,
                    cell_mouse_pos, cur_player.team, 1, tank_ready_to_spawn.ttx,
                    cur_player, ui.mist.Mist, tile_map)
                cur_player.resources -= tank_ready_to_spawn.ttx[-4]

                cur_player.mist_matrix = utils.functions.mist_doting3000(cur_player.tanks, cur_player.base, 
                                                                        map_matrix, all_tanks, all_bases, cur_player.team)

                tank_ready_to_spawn = None

        if (mouse_click[MOUSE_LMB] and button_turn_switch.rect.collidepoint(real_mouse_pos) and cur_player.base != 0): # смена хода
            mouse_click[MOUSE_LMB] = False
            if cnt_rounds//QNT_PLAYERS != 0:
                cur_player.exp += utils.functions.cell_distribution(QNT_PLAYERS, cur_player.team, all_tanks)
                cur_player.resources += utils.functions.resources_profit(len(cur_player.tanks.sprites()))
            cur_player.tanks.update()
            for ui_tank in all_tanks:
                ui_tank.drowed_stats = False
            active_player = (active_player + 1) % QNT_PLAYERS
            cur_player = players[active_player]
            cur_player.mist_matrix = utils.functions.mist_doting3000(cur_player.tanks, cur_player.base,
                                                                       map_matrix, all_tanks, all_bases, cur_player.team)
            if damage_text_timelive > 0:
                damage_text_timelive = 1
            if select_cell is not None:
                select_cell.kill()
                select_cell = None
            taken_tank_menu = None
            tank_ready_to_spawn = None
            selected_tank = None
            curtain_is_raisen = True
            market_window.empty()
            all_selected_cells.empty()
            cnt_rounds += 1

        if mouse_click[MOUSE_LMB] and 0<=cell_mouse_pos[0]<map_len_cells and 0<=cell_mouse_pos[1]<map_len_cells and not market_is_open: # выбор клетки
            mouse_click[MOUSE_LMB] = False
            if select_cell is None:
                select_cell = ui.cell_border.CellBorder(len_cell * cell_mouse_pos[0],
                                                            len_cell * cell_mouse_pos[1])
                all_selected_cells.add(select_cell)
                all_sprites.add(select_cell)
            else:
                select_cell.goto(len_cell * cell_mouse_pos[0],
                                len_cell * cell_mouse_pos[1])
                select_cell.dirty = 1
            selected_tank = None

            if tile_map[cell_mouse_pos[1], cell_mouse_pos[0]] == 2:
                for ui_tank in all_tanks:
                    if ui_tank.place[0] == cell_mouse_pos[0] and ui_tank.place[1] == cell_mouse_pos[1]: # выбор танка на клетке
                        if ui_tank.team == cur_player.team:
                            selected_tank = ui_tank
                        break

        if selected_tank is not None: # управление танком pg.K_w, pg.K_a, pg.K_s, pg.K_d
            if keys_click[pg.K_w] or keys_click[pg.K_a] or \
               keys_click[pg.K_s] or keys_click[pg.K_d]:
                selected_tank.move(keys_click[pg.K_w], keys_click[pg.K_a], \
                                   keys_click[pg.K_s], keys_click[pg.K_d], select_cell)

                cur_player.mist_matrix = utils.functions.mist_doting3000(cur_player.tanks, 
                    cur_player.base, map_matrix, all_tanks, all_bases, cur_player.team)
                
                keys_click[pg.K_w] = False
                keys_click[pg.K_a] = False
                keys_click[pg.K_s] = False
                keys_click[pg.K_d] = False

            if keys_click[pg.K_SPACE]:
                keys_click[pg.K_SPACE] = False
                selected_tank.shot(all_projectiles, all_sprites, world_mouse_pos, obj.projectile.Projectile)
            if keys_click[pg.K_q]:
                keys_click[pg.K_q] = False
                tile_map[selected_tank.place[1], selected_tank.place[0]] = 0
                selected_tank.kill()
                selected_tank = None
                cur_player.mist_matrix = utils.functions.mist_doting3000(cur_player.tanks,
                                                                           cur_player.base, map_matrix, all_tanks,
                                                                           all_bases, cur_player.team)
        else:  # управление камерой если не выбран танк
            keys = pg.key.get_pressed()
            cur_player.move(keys[pg.K_w], keys[pg.K_a], keys[pg.K_s], keys[pg.K_d])
            keys_click[pg.K_w] = False
            keys_click[pg.K_a] = False
            keys_click[pg.K_s] = False
            keys_click[pg.K_d] = False
            keys_click[pg.K_SPACE] = False

        if keys_click[pg.K_ESCAPE]:
            keys_click[pg.K_ESCAPE] = False

            scene = "menu"

            all_walls.empty()
            all_cells.empty()
            all_sprites.empty()
            all_selected_cells.empty()
            all_tanks.empty()
            all_bases.empty()
            all_buttons_menu.empty()
            map_is_builded = False
            players_is_init = False
            game_buttons_is_builded = False
            selected_tank = None
            taken_tank_menu = None
            tank_ready_to_spawn = None
            players = []
            active_player = 0
            cnt_rounds = 0
            continue

        for ui_tank in all_tanks:
            ui_tank.draw_stats(cur_player.team)

        panel_hp = ui.uipanel.UIPanel(SW/64+1, (SH*(1/4+5/800)) + SH*(1/4-5/800)*(cur_player.hp/base_hp), SW/32 - SW*10/1280-1, (SH/2 - SW*10/1280)*(cur_player.hp/base_hp),
                                            (128+(team_to_color[cur_player.team][0]-128)*(cur_player.hp/base_hp),
                                             128+(team_to_color[cur_player.team][1]-128)*(cur_player.hp/base_hp),
                                             128+(team_to_color[cur_player.team][2]-128)*(cur_player.hp/base_hp)), 0, 0, 0)

        for projectile in all_projectiles:
            damage = projectile.update(all_walls, all_tanks, cur_player.tanks, all_bases, map_matrix)
            if damage != 0:
                dam_text = font32.render(f"{int(damage)}", True, team_to_color[projectile.team])
                dam_dest = projectile.x, projectile.y
                damage_text_timelive = FPS*3
                if damage_window is not None:
                    damage_window.kill()
                damage_window = ui.uipanel.UIPanel(projectile.x, projectile.y, SW/24,
                                            SH/32, (255, 255, 255), 1, (0,0,0), 2)
                damage_window.image.blit(dam_text, (SW/256,SH/256))
                all_sprites.add(damage_window)

        if damage_text_timelive > 0:
            damage_text_timelive -= 1
            if damage_text_timelive <= 0 and type(damage_window) is ui.uipanel.UIPanel:
                damage_window.kill()

        all_sprites.draw(map_screen, background)

        dest = (-cur_player.cam_pos[0], -cur_player.cam_pos[1] )
        screen.blit(map_screen, dest)

        all_buttons_game.draw(screen)
        market_window.draw(screen)
        all_taken_in_market.draw(screen)

        panel_resources.draw(screen)
        panel_cnt_turns.draw(screen)
        panel_hp.draw(screen)

        panel_hp.draw(screen)

        text_turns = font48.render(f"Turn: {cnt_rounds//QNT_PLAYERS + 1}", True, team_to_color[cur_player.team])
        text_resouces = font48.render(f"Resources : {cur_player.resources}", True, team_to_color[cur_player.team])
        text_exp = font48.render(f"Сapture : {cur_player.exp}", True, team_to_color[cur_player.team])
        screen.blit(text_resouces, (SW/2-SW*7/64, 0))
        screen.blit(text_exp, (SW/2-SW*7/64, SH*3/80))
        screen.blit(text_turns, (SW*14/16 + SW*2/256, SH*14/16 - SW/32))
        
        if curtain_is_raisen:
            screen.fill((66, 66, 66))
    

    if old_fps_val != clock.get_fps():
        print(clock.get_fps())
        old_fps_val = clock.get_fps()

    clock.tick(FPS)
    pg.display.flip()

pg.quit()
