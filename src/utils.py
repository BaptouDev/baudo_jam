from math import *
import numpy as np
import pygame
import csv
import random

class vector2:
    def __init__(self,x,y):
        self.x = x
        self.y = y
    def magnitude_sq(self):
        return self.x**2 + self.y**2
    def length(self):
        return sqrt(self.magnitude_sq())
    def normalize(self):
        l = self.length()
        if l ==0:
            return self
        else:
            return vector2(self.x/l,self.y/l)
    def to_tuple(self):
        return (self.x,self.y)
    def scale(self,scalar):
        return vector2(self.x*scalar,self.y*scalar)
    def __add__(self,o):
        return vector2(self.x+o.x,self.y+o.y)
    def __mul__(self,scalar:float):
        return vector2(self.x*scalar,self.y*scalar)
    def __sub__(self,o):
        return vector2(self.x-o.x,self.y-o.y)
    def copy(self):
        return vector2(self.x,self.y)
class weighted_value:
    def __init__(self,value,weight):
        self.value = value
        self.weight = weight

def get_image(width,height,i,j,sheet):
    rect = pygame.rect.Rect(i*width,j*height,width,height)
    image = pygame.Surface(rect.size,pygame.SRCALPHA).convert_alpha()
    image.blit(sheet,(0,0),rect)
    return image

def load_world(path):
    with open(path,"r",newline="") as file:
        reader = csv.reader(file)
        rows = list(reader)
def sheet_to_list(sheet,tile_size,scale):
    images = []
    width,height = sheet.size
    n_rows = int(width / tile_size)
    n_columns = int(height / tile_size)
    for i in range(n_rows):
        for j in range(n_columns):
            images.append(pygame.transform.scale(get_image(tile_size,tile_size,i,j,sheet),(tile_size*scale,tile_size*scale)))
    return images
class level:
    def __init__(self,map_path,sheet_path,tile_size,scale,pos:vector2,gen_collisions:bool,with_file:bool):
        self.sheet = pygame.image.load(sheet_path)
        if with_file:
            with open(map_path,"r",newline="") as file:
                reader = csv.reader(file)
                rows = list(reader)
                self.map = rows
        else:
            map = [[0]]
        #print(self.map)
        self.tile_size = tile_size
        self.scale = scale
        self.images = sheet_to_list(self.sheet,self.tile_size,self.scale)
        self.pos = pos
        #if gen_collisions:
        #    self.gen_rects()
    def change_pos(self,new_pos):
        self.pos = new_pos
    def reload_map(self,map_path):
        with open(map_path,"r",newline="") as file:
            reader = csv.reader(file)
            rows = list(reader)
            self.map = rows
    def load_map_from_list(self,list):
        self.map = list
    def draw(self,screen:pygame.Surface,camera_pos:vector2):
        for i in range(len(self.map)):
            for j in range(len(self.map[0])):    
                if not self.map[i][j] =="-1":
                    screen.blit(self.images[int(self.map[i][j])],(self.pos+vector2(j*self.tile_size*self.scale,i*self.tile_size*self.scale)-camera_pos).to_tuple())
    def debug_draw_all_tiles(self,screen):
        x=0
        for i in self.images:
            if x<=10:
                screen.blit(i,(1280-128,x*self.tile_size*self.scale))
            else:
                screen.blit(i,(1280-64,(x-11)*self.tile_size*self.scale))
            x+=1
    def check_player_collision(self,player_box:pygame.Rect,camera_pos:vector2):
        for i in range(len(self.map)):
            for j in range(len(self.map[0])):
                if not self.map[i][j] =="-1":
                    c_rect = pygame.Rect(self.pos.x + j*self.tile_size*self.scale-camera_pos.x,
                                            self.pos.y + i*self.tile_size*self.scale-camera_pos.y,
                                            self.tile_size*self.scale,
                                            self.tile_size*self.scale)
                    if player_box.colliderect(c_rect):
                        return True
        
        return False
    def debug_draw_collisions(self,screen,camera_pos:vector2):
        for i in range(len(self.map)):
            for j in range(len(self.map[0])):
                if not self.map[i][j] =="-1":
                    c_rect = pygame.Rect(self.pos.x + j*self.tile_size*self.scale-camera_pos.x,
                                            self.pos.y + i*self.tile_size*self.scale-camera_pos.y,
                                            self.tile_size*self.scale,
                                            self.tile_size*self.scale)
                    pygame.draw.rect(screen,"green",c_rect)
    def gen_rects(self,camera_pos:vector2,check_mouse_collision:bool):
        collide_rects = []
        for i in range(len(self.map)):
            for j in range(len(self.map[0])):
                
                c_rect = pygame.Rect(self.pos.x + j*self.tile_size*self.scale-camera_pos.x,
                                            self.pos.y + i*self.tile_size*self.scale-camera_pos.y,
                                            self.tile_size*self.scale,
                                            self.tile_size*self.scale)
                    #pygame.draw.rect(screen,"green",c_rect)
                collide_rects.append(c_rect)
                if c_rect.collidepoint(pygame.mouse.get_pos()) and check_mouse_collision:
                    return (j,i)
        self.collide_rects = collide_rects
                
        return None
def change_tile(l:level,map_path,pos:tuple,tile_index):
    l.map[pos[1]][pos[0]] = tile_index
    with open(map_path,"w",newline="") as file:
            file.truncate()
            writer = csv.writer(file)
            writer.writerows(l.map)
    l.reload_map(map_path)
def change_tile_temp(l:level,pos:tuple,tile_index):
    l.map[pos[1]][pos[0]] = tile_index
def init_zero_map(l:level,map_path,w,h):
    map = np.full((w,h),-1)
    map = map.astype(int)
    with open(map_path,"w",newline="") as file:
            file.truncate()
            writer = csv.writer(file)
            writer.writerows(map)
    l.reload_map(map_path)

#used for generating grass
def rand_scatter_map(l:level,weighted_values:list,map_path,w,h):
    map = np.zeros((w,h))
    map = map.astype(int)
    for i in range(w):
        for j in range(h):
            r = random.randint(0,len(weighted_values)-1)
            map[i][j] = weighted_values[r].value
    l.load_map_from_list(map.tolist())
    #with open(map_path,"w",newline="") as file:
    #        file.truncate()
    #        writer = csv.writer(file)
    #        writer.writerows(map)
    #l.reload_map(map_path)

def check_player_collision_list(player:pygame.rect,ls:list,camera_pos):
    for level in ls:
        if level.check_player_collision(player,camera_pos):
            return True
    return False

class animation:
    def __init__(self,frames:list,durations:list):
        self.frames = frames
        self.durations = durations

class animated_sprite:
    def __init__(self,anims:dict,sheet_path:str,pos:vector2,scale:float,tile_size,default_anim = None):
        self.pos = pos
        self.scale = scale
        self.tile_size = tile_size
        self.sheet = pygame.image.load(sheet_path).convert_alpha()
        self.images = sheet_to_list(self.sheet,self.tile_size,self.scale)
        self.anims = anims
        self.anims['null'] = animation([0],[0])
        if default_anim == None:
            self.current_anim = 'null'
        else:
            self.current_anim = default_anim
        self.current_frame = 0
        self.current_time = 0
        self.is_flipped = False
    def change_anim(self,new_anim:str):
        self.current_anim = new_anim
        self.current_frame = 0
        self.current_time = 0
    def update_pos(self,new_pos):
        self.pos = new_pos
    def draw(self,screen:pygame.Surface,delta_time:float,camera_pos:vector2):
        if len(self.anims[self.current_anim].frames) ==0:
            pass
        else:
            self.current_time+=delta_time
            if self.current_time <= self.anims[self.current_anim].durations[self.current_frame]:
                pass
            else:
                self.current_time = 0
                if self.current_frame < len(self.anims[self.current_anim].frames)-1:
                    self.current_frame+=1
                else:
                    self.current_frame = 0
        surf = pygame.Surface((self.tile_size*self.scale,self.tile_size*self.scale),pygame.SRCALPHA)
        surf.blit(self.images[self.anims[self.current_anim].frames[self.current_frame]],(0,0))
        surf = pygame.transform.flip(surf,self.is_flipped,False)
        screen.blit(surf,(self.pos-camera_pos).to_tuple())

class rotated_sprite:
    def __init__(self,img_path:str,pos:vector2,scale:float,rot:float,add_angle:float,dist:float,tile_size):
        self.pos = pos
        self.scale = scale
        self.rot = rot
        self.add_angle = 0
        self.dist = dist
        self.tile_size = tile_size
        self.sprite = pygame.image.load(img_path).convert_alpha()
        self.sprite = pygame.transform.scale_by(self.sprite,self.scale)
    def update(self,new_pos:vector2,dt:float):
        self.pos = new_pos
        #self.rot+=dt*50
    def face_mouse(self,camera_pos:vector2):
        mouse_pos = vector2(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1])+camera_pos
        self.rot = -atan2(mouse_pos.y-self.pos.y,mouse_pos.x-self.pos.x)*180/pi

    def draw(self,screen:pygame.Surface,camera_pos:vector2):
        r_x = cos(radians(-self.rot))
        r_y = sin(radians(-self.rot))
        real_pos = self.pos + vector2(r_x,r_y)*self.dist
        #render_sprite = pygame.transform.rotate(self.sprite,self.rot)
        screen.blit(self.sprite,(real_pos-camera_pos).to_tuple())
class fadeout_sprite:
    def __init__(self,pos:vector2,scale:float,fadeout_speed:float,base_alpha:float,fadeout_sprite:pygame.Surface):
        self.pos = pos
        self.scale=scale
        self.fadeout_speed=fadeout_speed
        self.base_alpha = base_alpha
        self.current_alpha = base_alpha
        self.fadeout_sprite=fadeout_sprite.copy()
    def update_pos(self,new_pos):
        self.pos = new_pos
    def draw(self,screen:pygame.Surface,camera_pos:vector2,dt):
        self.current_alpha -= dt*self.fadeout_speed
        self.current_alpha = int(self.current_alpha)
        self.fadeout_sprite.set_alpha(self.current_alpha)
        screen.blit(self.fadeout_sprite,(self.pos-camera_pos).to_tuple())