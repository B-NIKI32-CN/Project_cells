import pygame as pg

from ..core.scene import Scene
from .. import ui
from ..core.settings import *
from ..core.game import Game

class GameScene(Scene):



    def __init__(self, game: Game):
        super().__init__()
        self.game = game