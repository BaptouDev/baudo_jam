import pygame
import math
from . import utils
from . import player

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
        self.damage_value = 1
        self.max_health = 2
        self.health = self.max_health
    def damage(self, hurt):
        self.health -= hurt
        if self.health < 0:
            self.health = 0
    def update(self, camera_pos:utils.vector2, player:player.player,dt:float,projectiles:list):
        if self.health <= 0:
            self.is_dead = True
        super().update(camera_pos)
    def draw(self, screen, camera_pos, dt):
        super().draw(screen, camera_pos, dt)
        if not self.is_dead:
            bar_width = 24 * self.scale
            bar_height = 2 * self.scale
            x = self.pos.x - camera_pos.x + 8 * self.scale - bar_width // 2
            y = self.pos.y - camera_pos.y - 10 * self.scale
            ratio = self.health / self.max_health
            pygame.draw.rect(screen, (60, 0, 0), (x, y, bar_width, bar_height))
            pygame.draw.rect(screen, (255, 0, 0), (x, y, bar_width * ratio, bar_height))
    def draw_display(self, screen, pos):
        super().draw_display(screen, pos)

class litte_guy(basic_enemy):
    def __init__(self, pos, scale, name, anims, sprite_path, default_anim, is_visible=True):
        super().__init__(pos, scale, name, anims, sprite_path, default_anim, is_visible)
        self.launch_projectile_time = 3
        self.launch_projectile_timer = 3
        self.wait_init_timer = 1
        self.speed = 100
    def update(self, camera_pos,player:player.player,dt:float,projectiles:list,collide_list):
        self.launch_projectile_timer-=dt
        self.wait_init_timer-=dt
        if self.wait_init_timer <=0:
            target_pos = player.pos - self.pos
            self.pos+= target_pos.normalize()*self.speed*dt
        if self.launch_projectile_timer <=0:
            self.launch_projectile_timer = self.launch_projectile_time
            target_pos = player.pos - self.pos + utils.vector2(8,8)*self.scale
            launch_angle = math.atan2(target_pos.y,target_pos.x)#*180/math.pi
            projectiles.append(utils.projectile(300,self.pos,self.scale,1,utils.vector2(0,0),utils.vector2(16*self.scale,16*self.scale),launch_angle,"res/img/little_rock.png"))
        super().update(camera_pos,player,dt,projectiles)
    def draw(self, screen, camera_pos, dt):
        return super().draw(screen, camera_pos, dt)
    def draw_display(self, screen, pos):
        return super().draw_display(screen, pos)

class rocket_enemy(basic_enemy):
    def __init__(self, pos, scale, name, anims, sprite_path, default_anim, is_visible=True):
        super().__init__(pos, scale, name, anims, sprite_path, default_anim, is_visible)
        self.wait_init_timer = 1
        self.wait_between_rocket = 1
        self.wait_between_rocket_timer = 2
        self.launch_time = 2
        self.launch_timer = 5
        self.speed = 100
        self.angle = 0
    
    def draw(self, screen, camera_pos, dt,player:player.player,projectiles:list,collide_list):
        self.wait_init_timer-=dt
        self.wait_between_rocket_timer-=dt
        self.launch_timer -=dt
        if self.wait_between_rocket_timer<=0 and self.launch_timer>=0:
            target_pos = player.pos - self.pos + utils.vector2(8,8)*self.scale
            launch_angle = math.atan2(target_pos.y,target_pos.x)
            
        self.vel = utils.vector2(math.cos(self.launch_angle),math.sin(self.launch_angle))*self.speed
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
