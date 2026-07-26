import json

# идея такова: когда клиент подключается он генерит себе случайный id отрицательный, потом сервак его меняет на нормальный
# вообще можешь делать как хочешь, можешь поменять то что я тут написал, главное каналы написаны - это низкий уровень, на тебе пока высокий - логика сервера и клиента.

# СЕТЬ
def show_id(id):
    data = {
        "global": "net", 
        "command": "show_id",
        "args": {
            "id": id
        }
    }
    return encode(data)

def change_id(old_id, new_id):
    data = {
        "global": "net", 
        "command": "change_id",
        "args": {
            "old": old_id,
            "new": new_id
        }
    }
    return encode(data)

def swap_id(pirst_id, second_id):
    data = {
        "global": "net", 
        "command": "swap_id",
        "args": {
            "ids": [pirst_id, second_id]
        }
    }
    return encode(data)


# ИГРА
def start_game(qnt_players: int, map_id: int):
    data = {
        "global": "game",
        "namespase": "main",
        "command": "start",
        "args": {
            "qnt_players": qnt_players,
            "map_id": map_id
        }
    }
    return encode(data)

# смена хода
def change_turn(new_player_id: int):
    data = {
        "global": "game", 
        "namespase": "turn", 
        "command": "change",
        "args": {
            "new_player_id": new_player_id
        }
    }
    return encode(data)

# спавн
def spawn_base(cell_pos: tuple[int, int]):
    data = {
        "global": "game", 
        "namespase": "spawn", 
        "command": "base",
        "args": {
            "pos": cell_pos
        }
    }
    return encode(data)

def spawn_tank(tank_type_id, cell_pos: tuple[int, int]):
    data = {
        "global": "game", 
        "namespase": "spawn", 
        "command": "tank",
        "args": {
            "tank_type_id": tank_type_id,
            "pos": cell_pos
        }
    }
    return encode(data)

def spawn_projectile(tank_id, direction: tuple[float, float]):
    data = {
        "global": "game", 
        "namespase": "spawn", 
        "command": "projectile",
        "args": {
            "tank_id": tank_id,
            "direction": direction
        }
    }
    return encode(data)

# мутации
def tank_move(tank_id, direction: str): # direction - ["forward", "backward", "left", "right"]
    if direction not in ["forward", "backward", "left", "right"]:
        return ""
    data = {
        "global": "game", 
        "namespase": "mutate", 
        "command": "move",
        "args": {
            "tank_id": tank_id,
            "direction": direction
        }
    }
    return encode(data)


# Утилиты
def encode(data: dict):
    return json.dumps(data, ensure_ascii=False, separators=(',', ':')) # separators=(',', ':')

def decode(json_string: str):
    return json.loads(json_string)

def decode_list(json_strings: list[str]):
    return [decode(json_string) for json_string in json_strings]
