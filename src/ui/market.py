import pygame as pg

from ..core.settings import *
from ..utils.functions import collidespritepoint
from ..data import ttc
from ..ui import cell_border, img_tank, uipanel



class Market():
    panel_menu = uipanel.UIPanel(SW/4, SH/4, SW/2, SH/2, (66,66,66), 1, (255,128,0), 5)
    button_exit_market = uipanel.UIPanel(SW*3/4-SW/16, SH/4, SW/16, SH/16, (200,0,0), 1, (0,255,255), 5)
    # button_confirm = uipanel.UIPanel(SW*3/4-SW/16, SH*3/4, SW/16, SH/16, (128,255,128), 1, (0,128,0), 5)
    button_drop_confirm = uipanel.UIPanel(SW*3/4-SW/8 + SW/16, SH*3/4 - SH/16, SW/16, SH/16, (255,255,128), 1, (128,128,0), 5)

    button_exit_market.layer = LAYER_MARKET_BUTTONS
    # button_confirm.layer = LAYER_MARKET_BUTTONS
    button_drop_confirm.layer = LAYER_MARKET_BUTTONS
    
    def __init__(self, scene, player):
        self.panel_ttc = uipanel.UIPanel(SW/32, SH/4, SW*7/32, SH/2, (255, 255, 255), 1,
                                    (255, 128, 0), int(SW * 5 / 1280))
        self.taken_tank_menu = None
        self.tank_ready_to_spawn = None
        self.market_sprites = pg.sprite.LayeredDirty() # была market_window
        self.market_ui_tanks = pg.sprite.LayeredDirty()
        self.all_border_in_market = pg.sprite.LayeredDirty() # было all_selected_in_window

        for j, tank_for_menu in enumerate(ttc.default_combination):
                x = j%3
                y = j//3
                tank_img = img_tank.ImgTank(SW / 2 - SW / 8 + x * SW / 8 - len_cell / 2,
                                                                  SH / 2 - SH / 8 + y * SH / 8 - len_cell / 2, player.team, 0, tank_for_menu)
                tank_img.layer = LAYER_TANK_IMG
                self.market_ui_tanks.add(tank_img)

        self.market_sprites.add(self.market_ui_tanks)
        self.market_sprites.add(self.market_ui_tanks, self.button_exit_market,
                                self.button_drop_confirm, self.panel_menu, self.panel_ttc) #, self.button_confirm
        self.player = player
        self.scene = scene
        
    def handle_event(self, event): # выбор танков в соответственном меню
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            real_mouse_pos = event.pos
            # перебор танков
            for ui_tank in self.market_ui_tanks:
                # поиск возможно нажатого танка
                if ui_tank.rect.collidepoint(real_mouse_pos):
                    self.market_sprites.remove(self.all_border_in_market)
                    self.all_border_in_market.empty()
                    self.taken_tank_menu = ui_tank
                    if self.tank_ready_to_spawn == self.taken_tank_menu:
                        self.drop()
                        return

                    self.panel_ttc.kill()

                    text_ttc = (
                        font48.render(f"TTC:", True, (0, 0, 0)),
                        font32.render(f"Distance of visible : {self.taken_tank_menu.ttx[0]}", True, (0, 0, 0)),
                        font32.render(f"Healf points : {self.taken_tank_menu.ttx[1]}", True, (0, 0, 0)),
                        font32.render(f"Armor: {self.taken_tank_menu.ttx[2]}, {self.taken_tank_menu.ttx[3]}, {self.taken_tank_menu.ttx[4]}", True, (0, 0, 0)),
                        font32.render(f"Mobility: {self.taken_tank_menu.ttx[5]}, {self.taken_tank_menu.ttx[6]}, {self.taken_tank_menu.ttx[7]}", True, (0, 0, 0)),
                        font32.render(f"Damage: {self.taken_tank_menu.ttx[8]}", True, (0, 0, 0)),
                        font32.render(f"Penedration: {self.taken_tank_menu.ttx[9]}", True, (0, 0, 0)),
                        font32.render(f"Reloading: {self.taken_tank_menu.ttx[10]}", True, (0, 0, 0)),
                        font32.render(f"Fire distance: {self.taken_tank_menu.ttx[11]}", True, (0, 0, 0)),
                    )

                    self.panel_ttc = uipanel.UIPanel(SW / 32, SH / 4, SW * 7 / 32, SH / 2, (255, 255, 255), 1,
                                                            (255, 128, 0), int(SW * 5 / 1280))
                    text_indentation = 10
                    for characteristic_text in text_ttc:
                        self.panel_ttc.image.blit(characteristic_text, (10, text_indentation))
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

                    self.market_sprites.add(self.panel_ttc)

                    self.border = cell_border.CellBorder(ui_tank.x, ui_tank.y)
                    self.border.dirty = 2
                    self.border.layer = LAYER_UI_SELECTION
                    self.all_border_in_market.add(self.border)   #self.button_confirm.edges((0, 128, 0), 5)
                    self.button_drop_confirm.edges((128, 128, 0), 5)
                    self.market_sprites.add(self.all_border_in_market)
                    
                    self.button_drop_confirm.edges((128, 128, 0), 5)
                    self.tank_ready_to_spawn = self.taken_tank_menu

                    return
                
            # if collidespritepoint(self.button_confirm, event.pos) and self.taken_tank_menu is not None:
            #     self.button_confirm.edges((0, 255, 255), 5)
            #     self.button_drop_confirm.edges((128, 128, 0), 5)
            #     self.border.change_color((255, 128, 0))

            #     self.tank_ready_to_spawn = self.taken_tank_menu

            #     return
                
            if collidespritepoint(self.button_drop_confirm, event.pos) and self.tank_ready_to_spawn is not None:
                # self.button_confirm.edges((0, 128, 0), 5)
                # self.border.change_color((255, 128, 0))

                self.drop()

                return

            if collidespritepoint(self.button_exit_market, event.pos):
                self.close()
                return
            for canvas in [self.panel_ttc, self.panel_menu]:
                if collidespritepoint(canvas, event.pos):
                    return
            self.close()
                
    def draw(self, screen):
        self.market_sprites.draw(screen)
        self.all_border_in_market.draw(screen)

    def close(self):
        self.player.spawn_tank_buff = self.tank_ready_to_spawn
        if self.tank_ready_to_spawn is not None:
            self.scene.is_spawning_tank = True
        else:
            self.scene.is_spawning_tank = False
        self.scene.panel_for_spawn_tank.draw_tank(self.tank_ready_to_spawn)
        self.scene.close_market()
        
    
    def drop(self):
        self.button_drop_confirm.edges((0, 255, 255), 5)
        self.market_sprites.remove(self.all_border_in_market)
        self.all_border_in_market.empty()
        self.panel_ttc = uipanel.UIPanel(SW / 32, SH / 4, SW * 7 / 32, SH / 2, (255, 255, 255), 1,
                                            (255, 128, 0), int(SW * 5 / 1280))
        self.market_sprites.add(self.panel_ttc)
        self.taken_tank_menu = None
        self.tank_ready_to_spawn = None

