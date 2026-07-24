import pygame as pg

from .core.settings import *
from .core.scene_manager import SceneManager
from .scenes.main_menu_scene import MainMenuScene
from .net.our_net import SoftServer, SoftClient


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


# ("127.0.0.1", 1234) ("10.26.229.242", 1234) ("10.26.229.165", 1234)
# server_addr = ("10.26.229.242", 1234)

k = input("(S)erver/(C)lient:")
if k in ['s','S','ы','Ы']:
    server_addr = input_server_addr()
    net_module = SoftServer(server_addr)
    print(f"SERVER {server_addr}")
elif k in ['c','C','с','С']:
    server_addr = input_server_addr()
    net_module = SoftClient(server_addr)
    print(f"Client (server: {server_addr})")
else:
    net_module = None


display_name = "tank game: "
if isinstance(net_module, SoftServer):
    display_name += "SERVER"
elif isinstance(net_module, SoftClient):
    display_name += "Client"
else:
    display_name += "offline"


pg.init()

screen = pg.display.set_mode((SW, SH), vsync=1) # pg.display.set_mode((SW, SH), pg.FULLSCREEN, vsync=1)
pg.display.set_caption(display_name)

clock = pg.time.Clock()

scene_manager = SceneManager(screen, MainMenuScene, net_module, debug=False)

while scene_manager.is_running():
    scene_manager.iteration()

    clock.tick(FPS)
    pg.display.flip()

pg.quit()
