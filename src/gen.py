from . import utils
from . import player
import pygame
import numpy as np
import random

class room:
    def __init__(self,map_path:str,grass_path:str,sheet_path:str,tile_size,pos:utils.vector2,scale:float,grass_values:list,enemies:dict,objects:dict,w=18,h=10):
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
        self.enemies = enemies
        self.objects = objects
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

def dir(start_point,last_dir,chamber,fail=0):
    if fail >=4:
        return None
    r = random.randint(0,4)
    if r == 4 and last_dir !=None:
        init_dir = last_dir
    else:
        init_dir = min(3,r)
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
    size = len( chamber)
    if (0 <= return_point[0] < size) and (0 <= return_point[1] < size):
        if chamber[return_point[0]][return_point[1]] != 1:
            return dir(start_point,last_dir,chamber,fail+1)
    else:
        return dir(start_point,last_dir,chamber,fail+1)

    return return_point,init_dir

def random_walk(size,steps):
    chamber = np.ones((size,size)) 
    start_point = (random.randint(2,size-3),random.randint(2,size-3))
    chamber[start_point[0]][start_point[1]] = 2
    current_point,last_dir = dir(start_point,None,chamber)
    chamber[current_point[0]][current_point[1]] = 0
    fail = 0
    last_last_dir = 0
    for i in range (steps-2):
        last_last_dir = last_dir
        r = dir(current_point,last_dir,chamber)
        if r != None:
            current_point,last_dir = r
        else:
            return random_walk(size,steps)
        chamber[current_point[0]][current_point[1]] = 0
    return chamber
def generate_chamber(rooms:list,shop_rooms:list,size,steps):
    chamber = random_walk(size,steps)
    return chamber
