import pygame
import math
import random
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
        self.max_health = 3
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
        self.wait_init_timer = .75
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
            projectiles.append(utils.projectile(350,self.pos,self.scale,1,utils.vector2(0,0),utils.vector2(16*self.scale,16*self.scale),launch_angle,"res/img/little_rock.png"))
        super().update(camera_pos,player,dt,projectiles)
    def draw(self, screen, camera_pos, dt):
        return super().draw(screen, camera_pos, dt)
    def draw_display(self, screen, pos):
        return super().draw_display(screen, pos)
    
class angry_guy(basic_enemy):
    def __init__(self, pos, scale, name, anims, sprite_path, default_anim, is_visible=True):
        super().__init__(pos, scale, name, anims, sprite_path, default_anim, is_visible)
        self.launch_projectile_time = 2
        self.launch_projectile_timer = 2
        self.wait_init_timer = .75
        self.speed = 150
        self.max_health = 6
        self.health = self.max_health
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
            projectiles.append(utils.projectile(350,self.pos,self.scale,1,utils.vector2(0,0),utils.vector2(16*self.scale,16*self.scale),launch_angle,"res/img/little_rock.png"))
            projectiles.append(utils.projectile(350,self.pos,self.scale,1,utils.vector2(0,0),utils.vector2(16*self.scale,16*self.scale),launch_angle+math.pi/12,"res/img/little_rock.png"))
            projectiles.append(utils.projectile(350,self.pos,self.scale,1,utils.vector2(0,0),utils.vector2(16*self.scale,16*self.scale),launch_angle-math.pi/12,"res/img/little_rock.png"))
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

class boss:
    def __init__(self, pos:utils.vector2, scale, anims, sprite_path):
        self.pos = pos 
        self.scale = scale
        self.sprite = utils.animated_sprite(anims,sprite_path,pos,scale,64,"idle")
        self.is_activated = False
        self.flipped = False
        self.is_dead = True
        self.max_health = 120
        self.current_health = self.max_health
        self.offset = utils.vector2(0,0)
        self.hurtbox = pygame.Rect(self.pos.x +self.offset.x,self.pos.y+self.offset.y,64*scale,64*scale)
        self.pos_in_layout = (0,0)
        
        self.first_attack_time = 1
        self.first_attack_timer = 1
        self.state = 0 #0 is base idle state, 1 is for the projectile attack, 2 is for teleportation, 3 is for the meteors, 4 is for the dash
        self.previous_state = 0
        self.wait_time_between_states = .5
        self.state_timer = .5
        #projectile variables
        self.first_projectile_attack_time = 1
        self.projectile_attack_wave_interval = .5
        self.projectile_attack_time = .5
        self.projectile_attack_nb = 6
        self.projectile_attack_count = 6
        #teleport variables
        self.summon_portal_wait_time = 1
        self.summon_portal_wait_timer = 1
        self.teleport_interval = .5
        self.teleport_timer = .5
        self.portals_nb = 3
        self.teleport_count = 3
        self.has_first_attacked = False
        self.teleport_pos = []
        self.portals = []
        self.has_summoned_portals =  True
        self.portal_projectile_nb = 6
    def update(self, camera_pos,player:player.player,dt:float,projectiles:list,collide_list):
        if self.is_activated:
            self.first_attack_timer-=dt
            self.hurtbox.left = self.pos.x + self.offset.x - camera_pos.x
            self.hurtbox.top = self.pos.y + self.offset.y - camera_pos.y
            if self.state ==0:
                self.state_timer -= dt
                if self.pos.x - player.pos.x <0:
                    self.flipped = False
                else:
                    self.flipped = True
                if self.first_attack_timer <=0 and not self.has_first_attacked:
                    self.state = 1
                    self.previous_state = 0
                    self.sprite.change_anim("cast_projectiles")
                    self.has_first_attacked =  True
                    self.projectile_attack_time = self.first_projectile_attack_time
                    self.projectile_attack_count = self.projectile_attack_nb
                if self.first_attack_timer<=0 and self.state_timer<=0 and self.has_first_attacked and self.state==0:
                    """self.state = random.randint(1,4)
                    while self.state == self.previous_state:
                        self.state = random.randint(1,4)"""
                    self.state = 2
                    if self.state == 1:
                        self.sprite.change_anim("cast_projectiles")
                        self.projectile_attack_time = self.first_projectile_attack_time
                        self.projectile_attack_count = self.projectile_attack_nb
                    elif self.state==2:
                        self.sprite.change_anim("cast_meteorite")
                        self.teleport_count = self.portals_nb
                        self.summon_portal_wait_timer = self.summon_portal_wait_time
                        self.teleport_pos.clear()
                        self.has_summoned_portals = False

            elif self.state == 1:
                self.projectile_attack_time -= dt
                if self.projectile_attack_count >0:
                    if self.projectile_attack_time <=0:
                        self.projectile_attack_count -=1
                        self.projectile_attack_time = self.projectile_attack_wave_interval
                        if not self.flipped:
                            projectiles.append(utils.projectile(350,self.pos + utils.vector2(50*self.scale,32*self.scale),self.scale,1,utils.vector2(2*self.scale,2*self.scale),utils.vector2(14*self.scale,14*self.scale),0,"res/img/powerball.png"))
                            projectiles.append(utils.projectile(350,self.pos + utils.vector2(50*self.scale,32*self.scale),self.scale,1,utils.vector2(2*self.scale,2*self.scale),utils.vector2(14*self.scale,14*self.scale),math.pi/8,"res/img/powerball.png"))
                            projectiles.append(utils.projectile(350,self.pos + utils.vector2(50*self.scale,32*self.scale),self.scale,1,utils.vector2(2*self.scale,2*self.scale),utils.vector2(14*self.scale,14*self.scale),-math.pi/8,"res/img/powerball.png"))
                            projectiles.append(utils.projectile(350,self.pos + utils.vector2(50*self.scale,32*self.scale),self.scale,1,utils.vector2(2*self.scale,2*self.scale),utils.vector2(14*self.scale,14*self.scale),math.pi/4,"res/img/powerball.png"))
                            projectiles.append(utils.projectile(350,self.pos + utils.vector2(50*self.scale,32*self.scale),self.scale,1,utils.vector2(2*self.scale,2*self.scale),utils.vector2(14*self.scale,14*self.scale),-math.pi/4,"res/img/powerball.png"))
                        else:
                            projectiles.append(utils.projectile(350,self.pos + utils.vector2(-10*self.scale,32*self.scale),self.scale,1,utils.vector2(2*self.scale,2*self.scale),utils.vector2(14*self.scale,14*self.scale),math.pi,"res/img/powerball.png"))
                            projectiles.append(utils.projectile(350,self.pos + utils.vector2(-10*self.scale,32*self.scale),self.scale,1,utils.vector2(2*self.scale,2*self.scale),utils.vector2(14*self.scale,14*self.scale),math.pi*9/8,"res/img/powerball.png"))
                            projectiles.append(utils.projectile(350,self.pos + utils.vector2(-10*self.scale,32*self.scale),self.scale,1,utils.vector2(2*self.scale,2*self.scale),utils.vector2(14*self.scale,14*self.scale),math.pi*7/8,"res/img/powerball.png"))
                            projectiles.append(utils.projectile(350,self.pos + utils.vector2(-10*self.scale,32*self.scale),self.scale,1,utils.vector2(2*self.scale,2*self.scale),utils.vector2(14*self.scale,14*self.scale),math.pi*5/4,"res/img/powerball.png"))
                            projectiles.append(utils.projectile(350,self.pos + utils.vector2(-10*self.scale,32*self.scale),self.scale,1,utils.vector2(2*self.scale,2*self.scale),utils.vector2(14*self.scale,14*self.scale),math.pi*3/4,"res/img/powerball.png"))
                else:
                    self.state =0   
                    self.previous_state = 1
                    self.state_timer = self.wait_time_between_states
            elif self.state == 2:
                self.summon_portal_wait_time-=dt
                if self.summon_portal_wait_time<=0 and not self.has_summoned_portals:
                    for i in range(self.portals_nb):
                        self.teleport_pos.append(utils.vector2(self.pos_in_layout[0]*16*self.scale*18 + random.randint(2,16)*self.scale*16,self.pos_in_layout[1]*16*self.scale*10 + random.randint(2,8)*self.scale*16))
                    for i in self.teleport_pos:
                        self.portals.append((pygame.transform.scale_by(pygame.image.load("res/img/portal.png").convert_alpha(),self.scale),i))
                    self.has_summoned_portals = True
                if self.has_summoned_portals and self.teleport_count >0:
                    self.teleport_timer-=dt
                    if self.teleport_timer <=0:
                        self.pos = self.teleport_pos[self.teleport_count-1] - utils.vector2(32,32)*self.scale
                        utils.summon_projectile_circle(350,self.pos + utils.vector2(-10*self.scale,32*self.scale),self.scale,1,utils.vector2(2*self.scale,2*self.scale),utils.vector2(14*self.scale,14*self.scale),self.portal_projectile_nb,"res/img/powerball.png",projectiles)
                        self.teleport_count-=1
                        self.teleport_timer = self.teleport_interval
                        self.portals.pop(self.teleport_count-1)
                if self.teleport_count ==0:
                    self.state =0   
                    self.previous_state = 2
                    self.state_timer = self.wait_time_between_states
            elif self.state == 3:
                pass
            elif self.state == 4:
                pass
            self.sprite.is_flipped = self.flipped
            
            self.sprite.update_pos(self.pos)
    def damage(self,hurt_amount):
        self.current_health-= hurt_amount
    def draw(self,screen:pygame.Surface,dt:float,camera_pos:utils.vector2):
        if self.is_activated:
            self.sprite.draw(screen,dt,camera_pos)
            for i in self.portals:
                screen.blit(i[0],(i[1]-camera_pos).to_tuple())
