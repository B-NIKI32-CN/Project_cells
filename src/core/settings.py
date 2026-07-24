from pygame import init as pygame_init
from pygame.font import Font

a = 1
# SW = screen.get_width()
# SH = screen.get_height()

pygame_init()

font48 = Font(None, 48)
font32 = Font(None, 32)
font24 = Font(None, 24)
font16 = Font(None, 16)

SW = a*1280 # теперь изменяемая, поэтому нужно сделать маленькими буквами
SH = a*800 # теперь изменяемая, поэтому нужно сделать маленькими буквами
SC = [SW/2, SH/2] # теперь изменяемая, поэтому нужно сделать маленькими буквами
FPS = 120

len_cell = 50 # нужно разделять слова
cell_width = 5 # только нечетные очень желательно
# чем вообще отличаются len и widht? почему тогда нет height?(сellsize или cellside, хотя как хочешь, просто напиши комменты)
# почему cell в первой стоит в конце а в следующей в начале?
# почему это не в Cell ??

player_speed = len_cell
camera_luft = 4

map_len_cells = 64
# это так же в свои файлы лучше убрать

projectile_size = 4
projectile_speed = 2.5

color_select = (0,255,255) # не пон

team_to_color = {0:(0,0,255), 1:(0,255,0), 2:(255, 0, 0), 3:(255, 255, 0), 4:(255, 0, 255)}
team_to_anticolor = {0:(255, 165, 0), 1:(255,0,0), 2:(0, 255, 0), 3:(128, 0, 128), 4:(255, 0, 255)}

base_hp = 2000

QNT_PLAYERS = 2
INITIAL_RESOURCES = 1000
max_spawn_distance = 2

# слои
LAYER_GROUND = 1
LAYER_OBJECTS = 2
LAYER_SELECTION = 5
LAYER_PROJECTILES = 7
LAYER_UI = 10
LAYER_TANK_IMG = 11
LAYER_MARKET_BUTTONS = 11
LAYER_UI_SELECTION = 13

#время
DAMAGE_PANEL_TIMELIVE = 3
