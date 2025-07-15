from . import utils
import pygame
class player:
    def __init__(self,pos:utils.vector2,scale,sheet_path:str,tile_size:int,collision_box:pygame.Rect,hurtbox:pygame.Rect):
        player_anims = {"idle": utils.animation([0,1],[.3,.3]),
                "run": utils.animation([0,2],[.2,.2])}
        self.sprite = utils.animated_sprite(player_anims,sheet_path,pos,scale,tile_size,"idle")
        self.pos = pos
        self.collision_box = collision_box
        self.hurtbox = hurtbox
        self.vel = utils.vector2(0,0)
        self.speed = 500
        self.last_pos = self.pos
        self.offset = utils.vector2(12,4)
    def update(self,dt,camera_pos,collision_layer:utils.level):
        
        input_vect = utils.vector2(0,0)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_z]:
            input_vect.y -= 1
        if keys[pygame.K_s]:
            input_vect.y += 1
        if keys[pygame.K_q]:
            input_vect.x -= 1
            self.sprite.is_flipped = True
        if keys[pygame.K_d]:
            input_vect.x += 1
            self.sprite.is_flipped = False

        input_vect = input_vect.normalize()
        self.vel = input_vect * self.speed

        self.pos=self.pos + utils.vector2(self.vel.x,0) * dt
        self.collision_box.left = self.pos.x - camera_pos.x + self.offset.x
        if collision_layer.check_player_collision(self.collision_box,camera_pos):
            self.pos.x = self.last_pos.x

        self.pos=self.pos + utils.vector2(0,self.vel.y) * dt
        self.collision_box.top = self.pos.y - camera_pos.y + self.offset.y
        if collision_layer.check_player_collision(self.collision_box,camera_pos):
            self.pos.y = self.last_pos.y

        if self.sprite.current_anim == 'idle' and self.vel.magnitude_sq() >0:
            self.sprite.change_anim("run")
        if self.sprite.current_anim == "run" and self.vel.magnitude_sq() == 0:
            self.sprite.change_anim("idle")
        self.last_pos = self.pos
    def draw(self,screen,camera_pos,dt):
        self.sprite.update_pos(self.pos)
        self.sprite.draw(screen,dt,camera_pos)