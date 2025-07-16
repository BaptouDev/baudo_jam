from . import utils
import pygame
class player:
    def __init__(self,pos:utils.vector2,scale,sheet_path:str,tile_size:int,collision_box:pygame.Rect,hurtbox:pygame.Rect):
        player_anims = {"idle": utils.animation([0,1],[.3,.3]),
                "run": utils.animation([0,2],[.2,.2])}
        self.sprite = utils.animated_sprite(player_anims,sheet_path,pos,scale,tile_size,"idle")
        self.pos = pos
        self.scale = scale
        self.collision_box = collision_box
        self.hurtbox = hurtbox
        self.vel = utils.vector2(0,0)
        self.speed = 500
        self.last_pos = self.pos
        self.offset = utils.vector2(12,4)
        self.dash_speed = 1500
        self.dash_duration = .10
        self.dashing_timer = 0
        self.dash_cooldown = 1.5
        self.dash_time = 0
        self.fadeout_sprites = []
        self.nb_fadeout_sprites = 5
        self.sprite_creation_timer = 0
        self.created_sprite_countdown = self.nb_fadeout_sprites
        self.created_sprite_offset = 0#.01
        #self.temp_fadeout_sprite = utils.fadeout_sprite(self.pos,scale,20,255,self.sprite.images[0])
    def update(self,dt,camera_pos,collision_layers:list):
        self.dash_time -= dt
        self.dashing_timer-=dt
        self.sprite_creation_timer -= dt
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
        if keys[pygame.K_LSHIFT] and self.dash_time <=0 and input_vect.magnitude_sq() !=0:
            self.created_sprite_countdown = self.nb_fadeout_sprites
            self.dash_time = self.dash_cooldown
            self.dashing_timer = self.dash_duration
            self.fadeout_sprites.append(utils.fadeout_sprite(self.pos,self.scale,150,200,self.sprite.images[0]))
            self.created_sprite_countdown-=1
            self.sprite_creation_timer = self.dash_duration/self.nb_fadeout_sprites+self.created_sprite_offset
        if self.dashing_timer >=0:
            self.vel = self.vel.normalize() * self.dash_speed
            if self.sprite_creation_timer <=0 and self.created_sprite_countdown >=0:
                print("yeah")
                self.created_sprite_countdown -= 1
                self.fadeout_sprites.append(utils.fadeout_sprite(self.pos,self.scale,150,200,self.sprite.images[0]))
                self.sprite_creation_timer = self.dash_duration/self.nb_fadeout_sprites+self.created_sprite_offset

        self.pos = self.pos + utils.vector2(self.vel.x, 0) * dt
        self.collision_box.left = self.pos.x + self.offset.x-camera_pos.x
        self.collision_box.top = self.pos.y + self.offset.y-camera_pos.y
        if utils.check_player_collision_list(self.collision_box,collision_layers,camera_pos):
            self.pos.x = self.last_pos.x
            self.collision_box.left = self.pos.x + self.offset.x-camera_pos.x

        self.pos = self.pos + utils.vector2(0, self.vel.y) * dt
        self.collision_box.left = self.pos.x + self.offset.x-camera_pos.x
        self.collision_box.top = self.pos.y + self.offset.y-camera_pos.y
        if utils.check_player_collision_list(self.collision_box,collision_layers,camera_pos):
            self.pos.y = self.last_pos.y
            self.collision_box.top = self.pos.y + self.offset.y-camera_pos.y

        if self.sprite.current_anim == 'idle' and self.vel.magnitude_sq() >0:
            self.sprite.change_anim("run")
        if self.sprite.current_anim == "run" and self.vel.magnitude_sq() == 0:
            self.sprite.change_anim("idle")
        #self.temp_fadeout_sprite.update_pos(self.pos + utils.vector2(64,64))
        self.last_pos = self.pos
    def draw(self,screen,camera_pos,dt):
        self.sprite.update_pos(self.pos)
        for i in self.fadeout_sprites:
            i.draw(screen,camera_pos,dt)
        #self.temp_fadeout_sprite.draw(screen,camera_pos,dt)
        self.sprite.draw(screen,dt,camera_pos)
