import pygame
from . import utils

class entity:
    def __init__(self,pos:utils.vector2,scale:float,name:str,is_visible = True,is_dead = False):
        self.pos = pos
        self.scale=scale
        self.name = name
        self.is_visible=is_visible
        self.is_dead = is_dead
    def update(self):
        pass
    def draw_display(self,screen):
        pass

class static_sprite_entity(entity):
    def __init__(self,pos:utils.vector2,scale:float,name:str,sprite_path:str,is_visible=True):
        #super().__init__(pos, scale,name, is_visible)
        self.pos = pos
        self.scale=scale
        self.name = name
        self.is_visible=is_visible
        self.sprite_path = sprite_path
        self.sprite = pygame.transform.scale_by(pygame.image.load(self.sprite_path).convert_alpha(),self.scale)
        self.is_dead = False
    def update(self):
        super().update()
    def draw(self,screen:pygame.Surface,camera_pos:utils.vector2):
        if not self.is_dead:
            screen.blit(self.sprite,(self.pos-camera_pos).to_tuple())
    def draw_display(self, screen:pygame.Surface, pos:tuple):
        screen.blit(self.sprite,pos)


def check_all_dead(entities:list):
    if len(entities) == 0:
        return True
    #for i in entities:
    #    if i.is_dead == False:
    #        return False
    return False
