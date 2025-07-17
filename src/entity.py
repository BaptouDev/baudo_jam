import pygame
from . import utils

class entity:
    def __init__(self,pos:utils.vector2,scale:float,name:str,is_visible = True):
        self.pos = pos
        self.scale=scale
        self.name = name
        self.is_visible=is_visible
        self.is_dead = False
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

class animated_sprite_entity(entity):
    def __init__(self,pos:utils.vector2,scale:float,name:str,anims:dict,sprite_path:str,default_anim:str,is_visible=True):
        super().__init__(pos,scale,name,is_visible)
        self.sprite = utils.animated_sprite(anims,sprite_path,pos,scale,16,default_anim)
        self.hitbox = pygame.Rect(pos.x,pos.y,16*scale,16*scale)
    def update(self,camera_pos:utils.vector2):
        self.hitbox = pygame.Rect(self.pos.x-camera_pos.x,self.pos.y-camera_pos.y,16*self.scale,16*self.scale)
        self.sprite.update_pos(self.pos)
    def draw(self,screen,camera_pos,dt):
        self.sprite.draw(screen,dt,camera_pos)
    def draw_display(self, screen:pygame.Surface, pos:tuple):
        screen.blit(self.sprite.images[0],pos)
class basic_enemy(animated_sprite_entity):
    def __init__(self, pos, scale, name, anims, sprite_path, default_anim, is_visible=True):
        super().__init__(pos, scale, name, anims, sprite_path, default_anim, is_visible)
        self.damage = 1
        self.health = 5
    def damage(self,hurt):
        self.health -= hurt
    def update(self,camera_pos:utils.vector2,player_pos:utils.vector2):
        if self.health <= 0:
            self.is_dead = True
        super().update(camera_pos)
    def draw(self, screen, camera_pos, dt):
        super().draw(screen, camera_pos, dt)
    def draw_display(self, screen, pos):
        super().draw_display(screen, pos)

class litte_guy(basic_enemy):
    def __init__(self, pos, scale, name, anims, sprite_path, default_anim, is_visible=True):
        super().__init__(pos, scale, name, anims, sprite_path, default_anim, is_visible)
    def update(self, camera_pos,player_pos:utils.vector2):
        super().update(camera_pos)
    def draw(self, screen, camera_pos, dt):
        return super().draw(screen, camera_pos, dt)
    def draw_display(self, screen, pos):
        return super().draw_display(screen, pos)

def check_all_dead(entities:list):
    if len(entities) == 0:
        return True
    #for i in entities:
    #    if i.is_dead == False:
    #        return False
    return False
