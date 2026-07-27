from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..core.scene_manager import SceneManager


import pygame as pg
from random import randint


from ..core.settings import *
from ..core.scene import Scene
from ..ui.uipanel import UIPanel
from ..ui.button_manual import ButtonManual
from ..ui.button_start_game import ButtonStartGame
from ..ui.button_offline import ButtonOffline
from ..ui.button_online import ButtonOnline
from ..ui.button_server import ButtonServer
from ..ui.button_client import ButtonClient
from ..net import signals_collector
from ..net.our_net import SoftServer, SoftClient
from ..utils.functions import collidespritepoint

def ip_addr_format(ip_addr_str: str):
    try:
        split_str = ip_addr_str.strip().split(':')
        if len(split_str) != 2: return None

        ip_str_nums = [num for num in split_str[0].split('.')]
        if len(ip_str_nums) != 4: return None
        for num_str in ip_str_nums:
            if len(num_str) > 1 and num_str[0] == '0': return None
            if not (num_str.isdigit() and (0 <= int(num_str) <= 255)): return None

        port_str = split_str[1]
        if len(port_str) > 1 and port_str[0] == '0': return None
        if not port_str.isdigit(): return None
        port = int(split_str[1])
        if not (0 <= port <= 65535): return None

        return (split_str[0], port)
    
    except:
        return None

def input_server_addr():
    addr = None
    while addr is None:
        addr_str = input("Адресс сервера: ")
        addr = ip_addr_format(addr_str)
        if addr is None:
            print("Ошибка ввода! Пример адресса: 127.0.0.1:1234")
    return addr

class MainMenuScene(Scene):


    def __init__(self, scene_manager: SceneManager):
        super().__init__(scene_manager)

        if self.scene_manager.net_module is not None:
            if isinstance(self.scene_manager.net_module, SoftClient):
                self.scene_manager.local_player_id = randint(-32768, -1)
                self.is_registration_request_send = False
            else:
                self.scene_manager.local_player_id = 0

            self.player_ids = set([self.scene_manager.local_player_id])

            self.is_starting = False
            self.is_game_started = False
            

        self.background = pg.Surface((SW, SH))
        self.background.fill((255,255,255))

        # Кнопки
        self.button_start_game = ButtonStartGame()
        self.button_manual = ButtonManual()
        self.button_online = ButtonOnline()
        self.button_offline = ButtonOffline()
        self.button_server = ButtonServer()
        self.button_client = ButtonClient()

        
        self.all_buttons = pg.sprite.LayeredDirty()
        self.all_buttons.add(self.button_start_game, self.button_manual)

        self.where = "first_menu"


    def handle_events(self, all_events: list[pg.event.Event]):
        for event in all_events:
            if event.type == pg.QUIT:
                self.scene_manager.stop()
                
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                if self.where == "first_menu":
                    self.scene_manager.stop()
                elif self.where == "manual" or self.where == "select_type_game":
                    self.where = "first_menu"
                    self.all_buttons.empty()
                    self.all_buttons.add(self.button_start_game, self.button_manual)

                elif self.where == "select_online_role" or self.where == "offline":
                    self.where = "select_type_game"
                    self.all_buttons.empty()
                    self.all_buttons.add(self.button_online, self.button_offline)
                

            elif event.type == pg.MOUSEBUTTONDOWN:
                if self.where == "first_menu":
                    if collidespritepoint(self.button_manual, event.pos):
                        self.where = "manual"

                        self.all_buttons.empty()

                    if collidespritepoint(self.button_start_game, event.pos):
                        self.where = "select_type_game"

                        self.all_buttons.empty()
                        self.all_buttons.add(self.button_online, self.button_offline)
                        

                elif self.where == "select_type_game":
                    if collidespritepoint(self.button_online, event.pos):
                        self.where = "select_online_role"
                        self.all_buttons.empty()
                        self.all_buttons.add(self.button_server, self.button_client)

                    elif collidespritepoint(self.button_offline, event.pos):
                        self.where = "offline"
                        qnt_players = int(input("Количество игроков в игре: "))
                        self.scene_manager.net_module = None
                        self.scene_manager.max_qnt_players = qnt_players

                        from .game_scene import GameScene
                        self.scene_manager.set_scene(GameScene)
                        self.all_buttons.empty()
                        
                elif self.where == "select_online_role":

                    if collidespritepoint(self.button_server, event.pos):
                        if self.scene_manager.net_module is None:
                            server_addr = input_server_addr()
                            net_module = SoftServer(server_addr)
                            print(f"SERVER {server_addr}")
                            qnt_players = int(input("Количество игроков в игре: "))
                            self.scene_manager.net_module = net_module
                            self.scene_manager.max_qnt_players = qnt_players

                        if len(self.player_ids) < self.scene_manager.max_qnt_players or min(self.player_ids) < 0:
                            print(f"[WARNING] Остались необработаные игроки! (ids: {self.player_ids})")
                            continue

                        else:
                            self.is_game_started = True

                            signal = signals_collector.start_game(len(self.player_ids), self.scene_manager.cur_map_id)
                            self.scene_manager.net_module.add(signal)

                        from .game_scene import GameScene
                        self.scene_manager.set_scene(GameScene)
                        self.all_buttons.empty()


                        if collidespritepoint(self.button_client, event.pos):
                            if self.scene_manager.net_module is None:
                                server_addr = input_server_addr()
                                net_module = SoftClient(server_addr)
                                print(f"Client (server: {server_addr})")
                                self.scene_manager.net_module = net_module

                            if not self.is_game_started:
                                print("[WARNING] Хост ещё не начал игру!")
                                continue

                            from .game_scene import GameScene
                            self.scene_manager.set_scene(GameScene)
                            self.all_buttons.empty()
                    

                    



    def update(self):
        ### NET
        if self.scene_manager.net_module is not None:
                
            json_signals = self.scene_manager.net_module.soft_recv()
            signals = signals_collector.decode_list(json_signals)

            for signal in signals:
                is_done = self.signal_processing(signal)
                if not is_done:
                    print(f"[WARNING] сигнал поганый: {signal}")
                elif isinstance(self.scene_manager.net_module, SoftServer):
                    self.scene_manager.net_module.add(signals_collector.encode(signal))


            if isinstance(self.scene_manager.net_module, SoftServer):
                
                if (self.scene_manager.net_module.connections_cnt + 1) < self.scene_manager.max_qnt_players:
                    self.is_connected = self.scene_manager.net_module.soft_conn()

                for player_id in self.player_ids:
                    if player_id < 0:
                        self.player_ids.remove(player_id)
                        new_id = max(self.player_ids) + 1
                        self.player_ids.add(new_id)

                        signal = signals_collector.change_id(player_id, new_id)
                        self.scene_manager.net_module.add(signal)


            elif isinstance(self.scene_manager.net_module, SoftClient):

                if self.scene_manager.net_module.connections_cnt == 0:
                    self.is_connected = self.scene_manager.net_module.soft_conn()

                elif not self.is_registration_request_send:
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
                self.player_ids.add(signal["args"]["id"])
                # if signal["args"]["id"] == self.scene_manager.local_player_id:
                    # self.is_registred = True
                return True

            if signal["command"] == "change_id":

                if "old" not in signal["args"]: return False
                if "new" not in signal["args"]: return False
                self.player_ids.discard(signal["args"]["old"])
                self.player_ids.add(signal["args"]["new"])
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

        if signal["global"] == "game":

            if "namespase" not in signal: return False

            if signal["namespase"] == "main":

                if signal["command"] == "start":

                    if "qnt_players" not in signal["args"]: return False
                    if "map_id" not in signal["args"]: return False

                    for id in range(signal["args"]["qnt_players"]):
                        self.player_ids.add(id)
                    self.scene_manager.cur_map_id = signal["args"]["map_id"]

                    self.is_game_started = True
                    return True


        return False


