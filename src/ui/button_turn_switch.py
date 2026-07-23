from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..scenes.game_scene import GameScene


from ..core.settings import *
from .uipanel import UIPanel


class ButtonTurnSwitch(UIPanel):

    x = SW*15/16 - SW/16
    y = SH*15/16 - SH/16
    W = SW*1/8
    H = SH*1/8
    color_on = (0,255,255)
    color_off = (0, 67, 67)
    color_edge = (255,128,0), 
    width = 5

    def __init__(self, game_scene: GameScene):
        super().__init__(self.x, self.y, self.W, self.H, self.color_on, 1, self.color_edge, self.width)
        self.game_scene = game_scene
        self.is_turned_on = True

    def update(self):
        if self.game_scene.is_active_player_turn != self.is_turned_on:
            self.is_turned_on = self.game_scene.is_active_player_turn
            if self.is_turned_on:
                color = self.color_on
            else:
                color = self.color_off
            super().__init__(self.x, self.y, self.W, self.H, color, 1, self.color_edge, self.width)
