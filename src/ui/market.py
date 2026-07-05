import pygame as pg

from .. import core, data, obj, ui, utils
from ..core.settings import *



class Market():
    market_sprites = pg.sprite.LayeredDirty()
    market_ui_tanks = pg.sprite.LayeredDirty()
    panel_menu = ui.uipanel.UIPanel(SW/4, SH/4, SW/2, SH/2, (66,66,66), 1, (255,128,0), 5)
    panel_menu.dirty = 2
    market_sprites.add(panel_menu)
    button_exit_market = ui.uipanel.UIPanel(SW*3/4-SW/16, SH/4, SW/16, SH/16, (200,0,0), 1, (0,255,255), 5)
    button_exit_market.dirty = 2
    button_confirm = ui.uipanel.UIPanel(SW*3/4-SW/16, SH*3/4, SW/16, SH/16, (128,255,128), 1, (0,128,0), 5)
    button_confirm.dirty = 2
    button_drop_confirm = ui.uipanel.UIPanel(SW*3/4-SW/8, SH*3/4, SW/16, SH/16, (255,255,128), 1, (128,128,0), 5)
    button_drop_confirm.dirty = 2
    panel_ttc = ui.uipanel.UIPanel(SW/32, SH/4, SW*7/32, SH/2, (255, 255, 255), 1,
                                    (255, 128, 0), int(SW * 5 / 1280))
    panel_ttc.dirty = 2
    def __init__(self, team):
        for j, tank_for_menu in enumerate(data.ttc.alpha):
                x = j%3
                y = j//3
                self.market_ui_tanks.add(ui.img_tank.ImgTank(SW / 2 - SW / 8 + x * SW / 8 - len_cell / 2,
                                                                  SH / 2 - SH / 8 + y * SH / 8 - len_cell / 2, team, 0, tank_for_menu))
        self.market_sprites.add(self.market_ui_tanks)
        self.market_sprites.add(self.button_exit_market, self.button_confirm, self.button_drop_confirm,
                                self.panel_menu, self.panel_ttc)
        



    def update: # выбор танков в соответственном меню
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

                    select_place = ui.selectedcell.Selectedcell(ui_tank.x, ui_tank.y)
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
