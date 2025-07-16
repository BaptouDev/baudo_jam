import pygame
from . import utils

class entity:
    def __init__(self,pos:utils.vector2,scale:float,name:str,is_visible = True):
        self.pos = pos
        self.scale=scale
        self.name = name
        self.is_visible=is_visible
    def update(self):
        pass
    def draw_display(self,screen):
        pass

class static_sprite_entity(entity):
    def __init__(self,pos:utils.vector2,scale:float,name:str,sprite_path:str,is_visible=True):
        super().__init__(pos, scale,name, is_visible)
        self.sprite_path = sprite_path
        self.sprite = pygame.transform.scale_by(pygame.image.load(self.sprite_path).convert_alpha(),self.scale)
    def update(self):
        super().update()
    def draw_display(self, screen:pygame.Surface, pos:tuple):
        screen.blit(self.sprite,pos)
    
