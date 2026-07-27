import pygame as pg

from ..core.settings import *
from ..ui.uipanel import UIPanel

class ButtonServer(UIPanel):
    x = SW/2 - SW/16 - SW*1/8
    y = SH/2 - SH/16
    W = SW*1/8
    H = SH*1/8
    color = (0,255,255)
    color_edge = (255,128,0), 
    width = 5
    
    def __init__(self):
        super().__init__(self.x, self.y, self.W, self.H, self.color, 1, self.color_edge, self.width)
        text_on_button = font48.render("Server", True, (0, 0, 0))
        self.image.blit(text_on_button, (self.size[0]/16, self.size[1]/3))