from . import utils
from . import player
import pygame
import numpy as np
import random

class room:
    def __init__(self,map_path:str,grass_path:str,sheet_path:str,tile_size,pos:utils.vector2,scale:float,grass_values:list,entities:dict,w=18,h=10):
        self.map_path = map_path
        self.grass_path = grass_path
        self.sheet_path = sheet_path
        self.grass_layer = utils.level("",grass_path,tile_size,scale,pos,False,False)
        self.main_layer = utils.level(map_path,sheet_path,tile_size,scale,pos,True,True)
        self.pos = pos
        self.scale = scale
        self.w=w
        self.h=h
        utils.rand_scatter_map(self.grass_layer,grass_values,"",h,w)
        self.entities = entities
    def change_tile_temp(self,pos:tuple,tile_index):
        utils.change_tile_temp(self.main_layer,pos,tile_index)
    def change_tile(self,pos:tuple,tile_index):
        utils.change_tile(self.main_layer,self.map_path,pos,tile_index)
    def clear_main_layer(self):
        utils.init_zero_map(self.main_layer,self.map_path,self.h,self.w)
    def check_collision_mouse(self,camera_pos:utils.vector2,edit_mode:bool):
        if edit_mode:
            mouse_pos = self.main_layer.gen_rects(camera_pos,edit_mode)
            return mouse_pos
        return None
    def check_player_collisions(self,player:player.player,camera_pos):
        return self.main_layer.check_player_collision(player.collision_box,camera_pos)
    def draw(self,screen:pygame.Surface,camera_pos:utils.vector2):
        self.grass_layer.draw(screen,camera_pos)
        self.main_layer.draw(screen,camera_pos)

def dir(start_point,last_dir,chamber,size,fail=0):
    if fail >=4:
        return None
    r = random.randint(1,8)
    if r == 1 and last_dir !=None:
        init_dir = last_dir
    else:
        init_dir = random.randint(0,3)
    #if last_dir != None:
    #    while init_dir %2 == last_dir % 2:
    #        init_dir = random.randint(0,3)
    #return_point = (0,0)
    if init_dir == 0:
        return_point = (start_point[0]+1,start_point[1])
    elif init_dir == 1:
        return_point = (start_point[0],start_point[1]+1)
    elif init_dir == 2:
        return_point = (start_point[0]-1,start_point[1])
    elif init_dir == 3:
        return_point = (start_point[0],start_point[1]-1)
    if return_point[0]<0 or return_point[0]>=len(chamber) or return_point[1]<0 or return_point[1]>=len(chamber):
        return dir(start_point,last_dir,chamber,fail+1)
    if chamber[return_point[0]][return_point[1]] != -1:
        return dir(start_point,last_dir,chamber,fail+1)
    return return_point,init_dir

def random_walk(size,steps):
    chamber = np.full((size,size),-1) 
    chamber = chamber.astype(int)
    start_point = (random.randint(2,size-3),random.randint(2,size-3))
    chamber[start_point[0]][start_point[1]] = 2
    current_point,last_dir = dir(start_point,None,chamber,size)
    chamber[current_point[0]][current_point[1]] = 0
    fail = 0
    last_last_dir = 0
    for i in range (steps-2):
        last_last_dir = last_dir
        r = dir(current_point,last_dir,chamber,size)
        if r != None:
            current_point,last_dir = r
        else:
            return random_walk(size,steps)
        chamber[current_point[0]][current_point[1]] = 0
    return chamber
def generate_chamber(rooms:list,size,steps,scale):
    chamber = random_walk(size,steps)
    pos_list = []
    #chamber = chamber.tolist()
    for i in range(size):
        for j in range(size):
            if chamber[i][j] !=-1 and chamber[i][j] != 2:
                pos_list.append((i,j))
    for i in pos_list:
        chamber[i[0]][i[1]] = random.randint(3,len(rooms)-1)
    r = random.randint(0,len(pos_list)-1)
    chamber[pos_list[r][0]][pos_list[r][1]] = 1
    return chamber

class door:
    def __init__(self,door_path:str,orientation:int,tile_size:int,scale:float,pos_in_layout:tuple,is_open=False):
        self.is_open=is_open
        self.orientation = orientation
        self.scale = scale
        self.tile_size = tile_size
        self.door_path = door_path
        self.door_sheet=pygame.image.load(self.door_path)
        self.images = utils.sheet_to_list(self.door_sheet,tile_size,scale)
        if self.orientation==0:
            self.door_sprite = pygame.Surface((tile_size*scale,tile_size*scale*2),pygame.SRCALPHA)
            self.door_sprite.blit(self.images[6],(0,0))
            self.door_sprite.blit(self.images[7],(0,tile_size*scale))
            self.pos = utils.vector2(0,0)
            self.pos.x = (pos_in_layout[1]*18+18)*tile_size*scale
            self.pos.y = (pos_in_layout[0]*10+5)*tile_size*scale
        elif self.orientation==1:
            self.door_sprite = pygame.Surface((tile_size*scale*2,tile_size*scale),pygame.SRCALPHA)
            self.door_sprite.blit(self.images[1],(0,0))
            self.door_sprite.blit(self.images[3],(tile_size*scale,0))
            self.pos = utils.vector2(0,0)
            self.pos.x = (pos_in_layout[1]*18+1+8)*tile_size*scale
            self.pos.y = (pos_in_layout[0]*10+1+9)*tile_size*scale
        elif self.orientation==2:
            self.door_sprite = pygame.Surface((tile_size*scale,tile_size*scale*2),pygame.SRCALPHA)
            self.door_sprite.blit(self.images[4],(0,0))
            self.door_sprite.blit(self.images[5],(0,tile_size*scale))
            self.pos = utils.vector2(0,0)
            self.pos.x = (pos_in_layout[1]*18+1)*tile_size*scale
            self.pos.y = (pos_in_layout[0]*10+5)*tile_size*scale
        elif self.orientation==3:
            self.door_sprite = pygame.Surface((tile_size*scale*2,tile_size*scale),pygame.SRCALPHA)
            self.door_sprite.blit(self.images[0],(0,0))
            self.door_sprite.blit(self.images[2],(tile_size*scale,0))
            self.pos = utils.vector2(0,0)
            self.pos.x = (pos_in_layout[1]*18+1+8)*tile_size*scale
            self.pos.y = (pos_in_layout[0]*10+1)*tile_size*scale
    def check_collision_player(self,player:pygame.Rect,camera_pos:utils.vector2):
        if not self.orientation%2==0:
            c_rect = pygame.Rect(self.pos.x-camera_pos.x,self.pos.y-camera_pos.y,self.tile_size*self.scale*2,self.tile_size*self.scale)
        else:
            c_rect = pygame.Rect(self.pos.x-camera_pos.x,self.pos.y-camera_pos.y,self.tile_size*self.scale,self.tile_size*self.scale*2)
        if c_rect.colliderect(player):
            return True
    def draw_rect(self,screen,camera_pos):
        if not self.orientation%2==0:
            c_rect = pygame.Rect(self.pos.x-camera_pos.x,self.pos.y-camera_pos.y,self.tile_size*self.scale*2,self.tile_size*self.scale)
        else:
            c_rect = pygame.Rect(self.pos.x-camera_pos.x,self.pos.y-camera_pos.y,self.tile_size*self.scale,self.tile_size*self.scale*2)
        pygame.draw.rect(screen,"green",c_rect)
    def draw(self,screen,camera_pos):
        screen.blit(self.door_sprite,(self.pos-camera_pos).to_tuple())
