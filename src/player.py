from . import utils
import pygame
import random
import math

class GrassParticle(utils.fadeout_sprite):
    def __init__(self, pos, scale, fadeout_speed, base_alpha, surf):
        super().__init__(pos, scale, fadeout_speed, base_alpha, surf)
        angle = random.uniform(0, 2*3.14159)
        speed = random.uniform(40, 80)
        self.vel = utils.vector2(math.cos(angle), math.sin(angle)) * speed
    def update(self, dt):
        self.pos = self.pos + self.vel * dt
        self.vel = self.vel * 0.85
        self.current_alpha -= dt*self.fadeout_speed
        self.current_alpha = int(self.current_alpha)

class player:
    def __init__(self,pos:utils.vector2,scale,sheet_path:str,tile_size:int,collision_box:pygame.Rect,hurtbox:pygame.Rect):
        player_anims = {"idle": utils.animation([0,1],[.3,.3]),
                "run": utils.animation([2,3],[.2,.2])}
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
        self.dash_duration = .12
        self.dashing_timer = 0
        self.dash_cooldown = .6
        self.dash_time = 0
        self.fadeout_sprites = []
        self.nb_fadeout_sprites = 5
        self.sprite_creation_timer = 0
        self.created_sprite_countdown = self.nb_fadeout_sprites
        self.created_sprite_offset = 0#.01
        #self.temp_fadeout_sprite = utils.fadeout_sprite(self.pos,scale,20,255,self.sprite.images[0])
        self.grass_particles = []
        self.grass_particle_timer = 0
        self.grass_particle_image = pygame.image.load('res/img/grass.png').convert_alpha()
        self.grass_particle_image = pygame.transform.scale(self.grass_particle_image, (int(8*self.scale), int(8*self.scale)))
        self.max_health = 6
        self.current_health = 6
        self.powerups_has = {"health":False,"double_dash":False,"fast_rock":False,"big_rock":False}
        self.invis_time = 1.5
        self.invis_timer = 0
        self.is_dashing = False
        self.is_dead = False
    def update(self,dt,camera_pos,collision_layers:list):
        self.dash_time -= dt
        self.dashing_timer-=dt
        self.sprite_creation_timer -= dt
        self.invis_timer-=dt
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
            self.fadeout_sprites.append(utils.fadeout_sprite(self.pos,self.scale,250,200,self.sprite.images[0]))
            self.created_sprite_countdown-=1
            self.sprite_creation_timer = self.dash_duration/self.nb_fadeout_sprites+self.created_sprite_offset
        if self.dashing_timer >=0:
            self.is_dashing = True
            self.vel = self.vel.normalize() * self.dash_speed
            if self.sprite_creation_timer <=0 and self.created_sprite_countdown >=0:
                self.created_sprite_countdown -= 1
                self.fadeout_sprites.append(utils.fadeout_sprite(self.pos,self.scale,150,200,self.sprite.images[0]))
                self.sprite_creation_timer = self.dash_duration/self.nb_fadeout_sprites+self.created_sprite_offset
        else:
            self.is_dashing = False

        # --- Particules d'herbe ---
        if self.vel.magnitude_sq() > 0:
            self.grass_particle_timer -= dt
            if self.grass_particle_timer <= 0:
                for _ in range(1):
                    p = GrassParticle(self.pos.copy() + utils.vector2(self.scale*8, self.scale*16), self.scale, 200, 200, self.grass_particle_image)
                    self.grass_particles.append(p)
                self.grass_particle_timer = 0.04
        # Update grass particles
        for p in self.grass_particles:
            p.update(dt)
        self.grass_particles = [p for p in self.grass_particles if p.current_alpha > 0]

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
        if self.invis_timer >= 0:
            self.sprite.is_blinking = True
        else:
            self.sprite.is_blinking = False
        #self.temp_fadeout_sprite.update_pos(self.pos + utils.vector2(64,64))
        self.last_pos = self.pos
    def pickup_powerup(self,powerup_name:str):
        self.powerups_has[powerup_name] = True
        if powerup_name == "health":
            self.max_health += 2
            self.current_health += 2
        if powerup_name == "double_dash":
            self.nb_fadeout_sprites = 8
            self.dash_speed = 2000
            self.dash_duration = .2
    def damage(self,damage):
        if self.invis_timer <0 and self.is_dashing == False:
            self.current_health-=damage
            if self.current_health<0:
                self.current_health=0
            if self.current_health==0:
                self.is_dead = True
            self.invis_timer = self.invis_time
    def is_alive(self):
        return not self.is_dead
    def draw(self,screen,camera_pos,dt):
        self.sprite.update_pos(self.pos)
        for i in self.fadeout_sprites:
            i.draw(screen,camera_pos,dt)
        #self.temp_fadeout_sprite.draw(screen,camera_pos,dt)
        self.sprite.draw(screen,dt,camera_pos)
        # Draw grass particles
        for p in self.grass_particles:
            p.draw(screen, camera_pos, dt)
