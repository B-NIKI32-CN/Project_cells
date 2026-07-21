import json

# идея такова: когда клиент подключается он генерит себе случайный id отрицательный, потом сервак его меняет на нормальный
# вообще можешь делать как хочешь, можешь поменять то что я тут написал, главное каналы написаны - это низкий уровень, на тебе пока высокий - логика сервера и клиента.

def show_id(id):
    data = {
        "global": "net", 
        "command": "show_id",
        "args": {"id": id}
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

def start_game(map_id: int):
    data = {
        "global": "game", 
        "namespase": "main",
        "command": "start",
        "args": {
            "map_id": map_id
        }
    }
    return encode(data)

def end_turn():
    data = {
        "global": "game", 
        "namespase": "new_turn", 
        "command": "end_turn"
    }
    return encode(data)

def new_turn(id):
    data = {
        "global": "game", 
        "namespase": "new_turn", 
        "command": "end_turn"
    }
    return encode(data)


def encode(data: dict):
    return json.dumps(data, ensure_ascii=False, separators=(',', ':')) # separators=(',', ':')

def decode(json_string: str):
    data = json.loads(json_string)
    if isinstance(data, dict):
        return data
    return {}
