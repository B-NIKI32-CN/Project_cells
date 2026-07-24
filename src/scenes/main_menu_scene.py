from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..core.scene_manager import SceneManager


import pygame as pg
from random import randint

from ..core.settings import *
from ..core.scene import Scene
from ..ui.uipanel import UIPanel
from ..net import signals_collector
from ..net.our_net import SoftServer, SoftClient


class MainMenuScene(Scene):    

    text_on_button = font48.render("Proceed", True, (0, 0, 0))


    def __init__(self, scene_manager: SceneManager):
        super().__init__(scene_manager)

        if self.scene_manager.net_module is not None:
            if isinstance(self.scene_manager.net_module, SoftClient):
                self.scene_manager.local_player_id = randint(-32768, -1)
                self.is_registration_request_send = False
            else:
                self.scene_manager.local_player_id = 0

            self.player_ids = [self.scene_manager.local_player_id]


        self.background = pg.Surface((SW, SH))
        self.background.fill((255,255,255))
        self.button_start_game = UIPanel(SW/2 - SW/16, SH/2 - SH/16, SW/8, SH/8, (0,255,255), 1, (255,128,0), 5)
        self.button_start_game.image.blit(self.text_on_button, (self.button_start_game.size[0]/16, self.button_start_game.size[1]/3))
        self.all_buttons = pg.sprite.LayeredDirty()
        self.all_buttons.add(self.button_start_game)


    def handle_events(self, all_events: list[pg.event.Event]):
        for event in all_events:
            if event.type == pg.QUIT:
                self.scene_manager.stop()

            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.scene_manager.stop()

            elif event.type == pg.MOUSEBUTTONDOWN:
                if self.button_start_game.rect.collidepoint(event.pos):
                    
                    if self.scene_manager.net_module is not None:
                        if self.scene_manager.net_module.connections_cnt == 0:
                            print("[WARNING] Ещё не подключено!")
                            continue
                        elif min(self.player_ids) < 0:
                            print("[WARNING] Остались необработаные игроки!")
                            continue

                    from .game_scene import GameScene
                    self.scene_manager.set_scene(GameScene)
                    self.all_buttons.empty()


    def update(self):
        ### NET
        if self.scene_manager.net_module is not None:
            if self.scene_manager.net_module.connections_cnt == 0:
                self.is_connected = self.scene_manager.net_module.soft_conn()

            else:

                json_signals = self.scene_manager.net_module.soft_recv()
                signals = [signals_collector.decode(json_signal) for json_signal in json_signals]

                for signal in signals:
                    is_done = self.signal_processing(signal)
                    if not is_done:
                        print(f"[WARNING] сигнал поганый: {signal}")
                    elif isinstance(self.scene_manager.net_module, SoftServer):
                        self.scene_manager.net_module.add(signals_collector.encode(signal))

                if isinstance(self.scene_manager.net_module, SoftServer):

                    for player_id in self.player_ids:
                        if player_id < 0:
                            player_ind = self.player_ids.index(player_id)
                            new_id = max(self.player_ids) + 1
                            self.player_ids[player_ind] = new_id

                            signal = signals_collector.change_id(player_id, new_id)
                            self.scene_manager.net_module.add(signal)

                elif isinstance(self.scene_manager.net_module, SoftClient):

                    if not self.is_registration_request_send:
                        signal = signals_collector.show_id(self.scene_manager.local_player_id)
                        self.scene_manager.net_module.add(signal)
                        self.is_registration_request_send = True

                self.scene_manager.net_module.soft_send()


    def display(self, screen: pg.Surface):
        self.all_buttons.draw(screen, self.background)


    ### NET
    def signal_processing(self, signal: dict):

        if "global" not in signal: return False
        if "command" not in signal: return False
        if "args" not in signal: return False
                
        if signal["global"] == "net":

            if signal["command"] == "show_id":
            
                if "id" not in signal["args"]: return False
                if signal["args"]["id"] not in self.player_ids:
                    self.player_ids.append(signal["args"]["id"])
                # if signal["args"]["id"] == self.scene_manager.local_player_id:
                    # self.is_registred = True
                return True

            if signal["command"] == "change_id":

                if "old" not in signal["args"]: return False
                if "new" not in signal["args"]: return False
                if signal["args"]["old"] in self.player_ids:
                    old_id_ind = self.player_ids.index(signal["args"]["old"])
                    self.player_ids[old_id_ind] = signal["args"]["new"]
                    for id in range(0, signal["args"]["new"]):
                        if id not in self.player_ids: 
                            self.player_ids.append(id)
                if self.scene_manager.local_player_id == signal["args"]["old"]:
                    self.scene_manager.local_player_id = signal["args"]["new"]
                    
                if self.scene_manager.debug:
                    print("[log] player_ids:", self.player_ids)
                return True

            if signal["command"] == "swap_id":
            
                if "ids" not in signal["args"] or len(signal["args"]["ids"]) != 2: return False
                if self.scene_manager.local_player_id in signal["args"]["ids"]:
                    old_id_ind = signal["args"]["ids"].index(self.scene_manager.local_player_id)
                    new_id_ind = (old_id_ind + 1) % 2
                    new_id = signal["args"]["ids"][new_id_ind]
                    self.scene_manager.local_player_id = new_id
                return True

        return False
