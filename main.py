import pygame
import pygame.freetype
import numpy as np
import random
from src import utils
from src import gen
from src import player
#from src import enemy
from src import entity
import os
import sys

pygame.init()
screen = pygame.display.set_mode((1270,720))
clock = pygame.time.Clock() 
running = True
scale = 4
cam_speed = 200
hyper_cam_speed = 1000
font = pygame.freetype.Font("res/fonts/Jersey15-Regular.ttf",48)

values = [utils.weighted_value(0,1),
          utils.weighted_value(1,1),
          utils.weighted_value(2,1),
          utils.weighted_value(3,1),
          utils.weighted_value(4,1),
          utils.weighted_value(5,1),
          utils.weighted_value(6,1),
          utils.weighted_value(7,1),
          utils.weighted_value(8,1)]
room_names = ["test","shop","start","room1","room2","room3","room4","room5","room6","room7"]
rooms = []
entities = [entity.static_sprite_entity(utils.vector2(0,0),scale,"","res/img/little_guy.png"),
            entity.static_sprite_entity(utils.vector2(0,0),scale,"","res/img/little_rock.png")]
entity_maps=[]
for i in room_names:
    rooms.append(gen.room("res/rooms/"+i+".csv","res/img/sheet.png","res/img/collide_sheet.png",16,utils.vector2(64,64),4,values,{}))
    entity_maps.append(utils.entity_map("res/rooms/entity_maps/"+i+"_e.csv"))
    #rooms.append(utils.level("res/rooms/"+i+".csv","res/img/sheet.png",16,4,utils.vector2(64,64),False,True))

current_room_index = 0


ui_sprite = pygame.image.load("res/img/ui.png").convert_alpha()
ui_sprite = pygame.transform.scale_by(ui_sprite,scale)
little_rock_img = pygame.image.load("res/img/rock.png")
little_rock_img = pygame.transform.scale_by(little_rock_img,5)


#player_anims = {"idle": utils.animation([0,1],[.3,.3]),
#                "run": utils.animation([0,2],[.2,.2])}
#player = utils.animated_sprite(player_anims,"res/img/player.png",utils.vector2(128,128),scale,16,"idle")
player = player.player(utils.vector2(128,128),scale,"res/img/player.png",16,pygame.Rect(128,128,40,60),pygame.Rect(128,128,40,60))
kayou = utils.rotated_sprite("res/img/rock.png",player.pos,scale,45,0,64.0,16)

heart_images = utils.sheet_to_list(pygame.image.load("res/img/heart.png"),16,scale)
recharge_bar = pygame.transform.scale_by(pygame.image.load("res/img/recharge_bar.png").convert_alpha(),scale)

powerup_images = utils.sheet_to_list(pygame.image.load("res/img/powerup.png"),16,scale)

powerups = [utils.powerup_pickup("health","2 Coeurs en plus",powerup_images[0],scale),
            utils.powerup_pickup("double_dash","Un dash plus rapide",powerup_images[1],scale),
            utils.powerup_pickup("fast_rock","Kayou plus rapide",powerup_images[3],scale),
            utils.powerup_pickup("big_rock","Gros Kayou",powerup_images[4],scale),
            utils.powerup_pickup("exploding_rock","Kayou explosif",powerup_images[6],scale)]
current_pickups = []

previous_time = 0
current_time = 0

room_transition_time = .5
room_transition_timer = 50

re_enter_room_cooldown = 1.5
re_enter_room_timer = 0
camera_start_pos = utils.vector2(0,0)
player_start_pos = utils.vector2(0,0)
camera_goal_pos = utils.vector2(0,0)
player_goal_pos = utils.vector2(0,0)
trans = 0

camera_pos = utils.vector2(0,0)

#enemy = enemy.Enemy(utils.vector2(256,256), scale,"res/img/little_guy.png",16)

#Edit mode variable only for dev:
edit_mode = False
current_cam_speed = 0.0
cursor_pos = (0,0)
current_selected_tile_index = 0
current_selected_entity_index = 0
#for i in range(50):
#    layout = gen.generate_chamber(rooms,15,10,scale)

layout = gen.generate_chamber(rooms,20,10,scale)
rooms_in_layout = []
room_in_index = 0
x=0
current_room_pos = (0,0)
edit_mode_adding_entities = False #false is for tile placing, true is for entity placing
doors = []
been_explored_dict = {}

#entities_creation_lookup_table = 
for i in range(len(layout)):
    for j in range(len(layout[0])):
        if layout[i][j]!=-1:
            #rooms_in_layout.append(rooms[layout[i][j]].copy())
            rooms_in_layout.append(gen.room("res/rooms/"+room_names[layout[i][j]]+".csv","res/img/sheet.png","res/img/collide_sheet.png",16,utils.vector2(64,64) + utils.vector2(j*scale*16*18,i*scale*16*10),scale,values,{}))
            if (0<i):
                if layout[i-1][j] !=-1:
                    """rooms_in_layout[x].change_tile_temp((8,0),"-1")
                    rooms_in_layout[x].change_tile_temp((9,0),"-1")"""
                    if layout[i][j]==2:
                        doors.append(gen.door("res/img/door.png",3,16,scale,(i,j),x))
                    else:
                        doors.append(gen.door("res/img/door.png",3,16,scale,(i,j),x,False))
            if i<len(layout[0])-1:
                if layout[i+1][j] !=-1:
                    """"rooms_in_layout[x].change_tile_temp((8,9),"-1")
                    rooms_in_layout[x].change_tile_temp((9,9),"-1")"""
                    if layout[i][j] ==2:
                        doors.append(gen.door("res/img/door.png",1,16,scale,(i,j),x))
                    else:
                        doors.append(gen.door("res/img/door.png",1,16,scale,(i,j),x,False))
            if (0<j):
                if layout[i][j-1] !=-1:
                    """rooms_in_layout[x].change_tile_temp((0,4),"-1")
                    rooms_in_layout[x].change_tile_temp((0,5),"-1")"""
                    if layout[i][j]==2:
                        doors.append(gen.door("res/img/door.png",2,16,scale,(i,j),x))
                    else:
                        doors.append(gen.door("res/img/door.png",2,16,scale,(i,j),x,False))
                    
            if j<len(layout[1])-1:
                if layout[i][j+1] !=-1:
                    """rooms_in_layout[x].change_tile_temp((17,4),"-1")
                    rooms_in_layout[x].change_tile_temp((17,5),"-1")"""
                    if layout[i][j]==2:
                        doors.append(gen.door("res/img/door.png",0,16,scale,(i,j),x))
                    else:
                        doors.append(gen.door("res/img/door.png",0,16,scale,(i,j),x,False))
            been_explored_dict[(j,i)] = False
            #rooms_in_layout[x].pos = utils.vector2(64,64) + utils.vector2(j*scale*16*rooms_in_layout[x].h,i*scale*16*rooms_in_layout[x].w)
            if layout[i][j] ==2:
                camera_pos= rooms_in_layout[x].pos.copy()-utils.vector2(64,64)
                camera_goal_pos = rooms_in_layout[x].pos.copy()-utils.vector2(64,64)
                player.pos= rooms_in_layout[x].pos.copy()+utils.vector2(9*16*scale,5*16*scale)
                rooms_in_layout[x].been_explored = True
                rooms_in_index = x
                current_room_pos = (j,i)
                r = random.randint(0,len(powerups)-1)
                powerups[r].pos = utils.vector2(j*scale*16*18+16*scale*6,i*scale*16*10+16*5*scale)
                powerups[r].interact_rect.left = powerups[r].pos.x
                powerups[r].interact_rect.top = powerups[r].pos.y
                current_pickups.append(powerups[r])
                a = random.randint(0,len(powerups)-1)
                while a==r:
                    a = random.randint(0,len(powerups)-1)
                powerups[a].pos = utils.vector2(j*scale*16*18+16*scale*12,i*scale*16*10+16*5*scale)
                powerups[a].interact_rect.left = powerups[a].pos.x
                powerups[a].interact_rect.top = powerups[a].pos.y
                been_explored_dict[current_room_pos] = True
                current_pickups.append(powerups[a])
            if layout[i][j] ==1:
                rooms_in_layout[x].been_explored = True
                been_explored_dict[(j,i)] = True
            x+=1

collision_layers = []
for i in rooms_in_layout:
    collision_layers.append(i.main_layer)

kayou_cooldown = kayou.max_throw_time 
kayou_cooldown_max = kayou.max_throw_time

current_entities = []
projectiles = []
MENU = 0
GAME = 1
CREDIT = 2
PAUSE = 3
GAME_OVER = 4
state = MENU

button_w, button_h = 470, 100
button_play_rect = pygame.Rect((1280//2 - button_w//2, 300), (button_w, button_h))
button_credit_rect = pygame.Rect((1280//2 - button_w//2, 430), (button_w, button_h))
button_quit_rect = pygame.Rect((1280//2 - button_w//2, 560), (button_w, button_h))

bounce_rects = [pygame.Rect(0,0,16*18*scale,16*scale),pygame.Rect(0,9*16*scale,16*18*scale,16*scale),pygame.Rect(0,0,16*scale,10*16*scale),pygame.Rect(17*16*scale,0,16*scale,10*16*scale)]

show_fps = True
settings_menu = False
show_minimap = False

while running:
    current_time = pygame.time.get_ticks()
    delta_time = clock.tick() / 1000 
    previous_time = current_time
    room_transition_timer+= delta_time
    re_enter_room_timer-= delta_time
    if kayou.is_thrown:
        kayou_cooldown = kayou.max_throw_time - kayou.throw_timer
        if kayou_cooldown < 0:
            kayou_cooldown = 0
    else:
        kayou_cooldown = kayou_cooldown_max
        #if kayou_cooldown == 0:
        #    kayou_cooldown = kayou_cooldown_max
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if state == MENU:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if button_play_rect.collidepoint(mouse_pos):
                    state = GAME
                if button_quit_rect.collidepoint(mouse_pos):
                    running = False
                if button_credit_rect.collidepoint(mouse_pos):
                    state = CREDIT
        elif state == GAME:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = PAUSE
                if event.key == pygame.K_SPACE:
                    for i in current_pickups:
                        i.update(camera_pos)
                        if i.interact_rect.colliderect(player.collision_box):
                            player.pickup_powerup(i.name)
                            current_pickups.clear()
                            break
                if event.key == pygame.K_r and edit_mode:
                    if edit_mode_adding_entities == False:
                        rooms[current_room_index].clear_main_layer()
                    else:
                        entity_maps[current_room_index].init_zero_map(18,10)
                if event.key == pygame.K_e:
                    edit_mode = not edit_mode
                    if edit_mode:
                        camera_pos = utils.vector2(0,0)
                if event.key == pygame.K_g and edit_mode:
                    if current_room_index < len(rooms)-1:
                        current_room_index +=1
                    else:
                        current_room_index=0
                if event.key==pygame.K_k:
                    current_entities.clear()
                    #for i in range(len(current_entities)):
                    #    current_entities[i].is_dead = True
                if event.key == pygame.K_c and edit_mode:
                    edit_mode_adding_entities = not edit_mode_adding_entities
                if event.key == pygame.K_KP_PLUS:
                    if not edit_mode_adding_entities:
                        if current_selected_tile_index < len(rooms[current_room_index].main_layer.images)-1:
                            current_selected_tile_index+=1
                        else:
                            current_selected_tile_index = 0
                    else:
                        if current_selected_entity_index < len(entities)-1:
                            current_selected_entity_index+=1
                        else:
                            current_selected_entity_index = 0
                if event.key == pygame.K_KP_MINUS:
                    if not edit_mode_adding_entities:
                        if current_selected_tile_index > 0:
                            current_selected_tile_index-=1
                        else:
                            current_selected_tile_index = len(rooms[current_room_index].main_layer.images)-1
                    else:
                        if current_selected_entity_index > 0:
                            current_selected_entity_index-=1
                        else:
                            current_selected_entity_index = len(entities)-1
        
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not cursor_pos == None and edit_mode:
                if not edit_mode_adding_entities:
                    rooms[current_room_index].change_tile(cursor_pos,current_selected_tile_index)
                else:
                    entity_maps[current_room_index].change_tile(cursor_pos,current_selected_entity_index)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and not cursor_pos == None and edit_mode:
                if not edit_mode_adding_entities:
                    rooms[current_room_index].change_tile(cursor_pos,-1)
                else:
                    entity_maps[current_room_index].change_tile(cursor_pos,-1)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not edit_mode and not kayou.is_thrown:
                mouse_pos = utils.vector2(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]) + camera_pos
                direction = mouse_pos - kayou.pos
                if player.powerups_has["fast_rock"]:
                    kayou.throw(direction, 1600)
                else:
                    kayou.throw(direction, 800)
            if player.powerups_has["big_rock"]:
                kayou.hitbox.width = 16*scale
                kayou.hitbox.height = 16*scale
                kayou.sprite = pygame.transform.scale_by(pygame.image.load("res/img/big_rock.png").convert_alpha(),scale)

        elif state == CREDIT:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                retour_rect = pygame.Rect((1280//2 - button_w//2, 600), (button_w, button_h))
                if retour_rect.collidepoint(pygame.mouse.get_pos()):
                    state = MENU
    
        elif state == PAUSE:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = GAME

    if state == MENU:
        for y in range(720):
            color = (
                int(30 + (y/720)*60),
                int(30 + (y/720)*90),
                int(60 + (y/720)*120)
            )
            pygame.draw.line(screen, color, (0, y), (1280, y))
        
        mouse_pos = pygame.mouse.get_pos()
        big_font = pygame.freetype.Font("res/fonts/Jersey15-Regular.ttf", 96)
        title_rect = big_font.get_rect("Kayou")
        big_font.render_to(screen, (1280//2 - title_rect.width//2, 90), "Kayou", (255,255,255))
        
        def draw_button(rect, text, base_color, hover_color):
            is_hover = rect.collidepoint(mouse_pos)
            color = hover_color if is_hover else base_color
            shadow_rect = rect.copy()
            shadow_rect.x += 6
            shadow_rect.y += 6
            pygame.draw.rect(screen, (0,0,0,80), shadow_rect, border_radius=32)
            pygame.draw.rect(screen, color, rect, border_radius=32)
            text_rect = font.get_rect(text)
            text_x = rect.x + (rect.width - text_rect.width) // 2
            text_y = rect.y + (rect.height - text_rect.height) // 2
            font.render_to(screen, (text_x, text_y), text, (0,0,0))
        draw_button(button_play_rect, "JOUER", (80,180,255), (120,220,255))
        draw_button(button_credit_rect, "CRÉDIT", (120,120,120), (180,180,180))
        draw_button(button_quit_rect, "QUITTER", (200,60,60), (255,100,100))
        
        pygame.display.flip()
        continue
    elif state == GAME:
        if edit_mode:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LSHIFT]:
                current_cam_speed = hyper_cam_speed
            else:
                current_cam_speed = cam_speed
            if keys[pygame.K_z]:
                camera_pos.y -= current_cam_speed*delta_time
            if keys[pygame.K_s]:
                camera_pos.y += current_cam_speed*delta_time
            if keys[pygame.K_q]:
                camera_pos.x -= current_cam_speed*delta_time
            if keys[pygame.K_d]:
                camera_pos.x += current_cam_speed*delta_time
            cursor_pos = rooms[current_room_index].check_collision_mouse(camera_pos,edit_mode)
        else:
            player.update(delta_time,camera_pos,collision_layers)
            if player.is_dead:
                state = GAME_OVER
            kayou.update(player.pos,delta_time,collision_layers,camera_pos,player.powerups_has["explosive_rock"])
            for e in current_entities:
                e.update(camera_pos,player,delta_time,projectiles,collision_layers)
                if kayou.hitbox.colliderect(e.hitbox) and kayou.is_thrown:
                    if player.powerups_has["big_rock"]:
                        e.damage(2)
                    else:
                        e.damage(1)
                    kayou.throw_timer = 500
            for p in range(len(projectiles)):
                projectiles[p].update(camera_pos,delta_time)
                if projectiles[p].hitrect.colliderect(player.collision_box):
                    player.damage(projectiles[p].damage)
                    projectiles.pop(p)
                    break
            #kayou.face_mouse(camera_pos)
            #enemy.update(delta_time, rooms_in_layout[room_in_index].main_layer, player.pos)
            for i in range(len(current_entities)):
                #if current_entities[i]
                if current_entities[i].is_dead == True:
                    current_entities.pop(i)
                    break
            #all_dead = entity.check_all_dead(current_entities)
            for i in doors:
                
                #if i.is_open == False:
                if len(current_entities)!=0:
                    if i.orientation ==0:
                        rooms_in_layout[i.room_index].change_tile_temp((17,4),"34")
                        rooms_in_layout[i.room_index].change_tile_temp((17,5),"34")
                    elif i.orientation ==1:
                        rooms_in_layout[i.room_index].change_tile_temp((8,9),"32")
                        rooms_in_layout[i.room_index].change_tile_temp((9,9),"32")
                    elif i.orientation ==2:
                        rooms_in_layout[i.room_index].change_tile_temp((0,4),"28")
                        rooms_in_layout[i.room_index].change_tile_temp((0,5),"28")
                    elif i.orientation ==3:
                        rooms_in_layout[i.room_index].change_tile_temp((8,0),"30")
                        rooms_in_layout[i.room_index].change_tile_temp((9,0),"30")
                else:
                    if i.orientation ==0:
                        rooms_in_layout[i.room_index].change_tile_temp((17,4),"-1")
                        rooms_in_layout[i.room_index].change_tile_temp((17,5),"-1")
                    elif i.orientation ==1:
                        rooms_in_layout[i.room_index].change_tile_temp((8,9),"-1")
                        rooms_in_layout[i.room_index].change_tile_temp((9,9),"-1")
                    elif i.orientation ==2:
                        rooms_in_layout[i.room_index].change_tile_temp((0,4),"-1")
                        rooms_in_layout[i.room_index].change_tile_temp((0,5),"-1")
                    elif i.orientation ==3:
                        rooms_in_layout[i.room_index].change_tile_temp((8,0),"-1")
                        rooms_in_layout[i.room_index].change_tile_temp((9,0),"-1")
                
                if i.check_collision_player(player.collision_box,camera_pos) and room_transition_timer >=room_transition_time:
                    if i.orientation ==0:
                        camera_goal_pos = camera_pos + utils.vector2(18*scale*16,0)
                        player_goal_pos = player.pos + utils.vector2(scale*16*4,0)
                        current_room_pos = (current_room_pos[0]+1,current_room_pos[1])
                    elif i.orientation ==1:
                        camera_goal_pos = camera_pos + utils.vector2(0,10*scale*16)
                        player_goal_pos = player.pos + utils.vector2(0,scale*16*4)
                        current_room_pos = (current_room_pos[0],current_room_pos[1]+1)
                    elif i.orientation ==2:
                        camera_goal_pos = camera_pos - utils.vector2(18*scale*16,0)
                        player_goal_pos = player.pos - utils.vector2(scale*16*4,0)
                        current_room_pos = (current_room_pos[0]-1,current_room_pos[1])
                    elif i.orientation ==3:
                        camera_goal_pos = camera_pos - utils.vector2(0,10*scale*16)
                        player_goal_pos = player.pos - utils.vector2(0,scale*16*4)
                        current_room_pos = (current_room_pos[0],current_room_pos[1]-1)
                    re_enter_room_timer = re_enter_room_cooldown
                    room_transition_timer = 0
                    player_start_pos = player.pos.copy()
                    camera_start_pos = camera_pos.copy()
                    #c = entity_maps[layout[current_room_pos[0]][current_room_pos[1]]].map
                    c = entity_maps[layout[current_room_pos[1]][current_room_pos[0]]].map
                    #print(c)
                    #if rooms_in_layout[room_in_index].been_explored == False:
                    if been_explored_dict[current_room_pos]==False:
                        for j in range(len(c)):
                            for k in range(len(c[0])):
                                if c[j][k] =="0":
                                #current_entities.append(entity.static_sprite_entity(utils.vector2(current_room_pos[0]*16*scale*18+k*16*scale+16*scale,current_room_pos[1]*16*scale*10+j*16*scale+16*scale),scale,"","res/img/little_guy.png"))
                                    current_entities.append(entity.litte_guy(utils.vector2(current_room_pos[0]*16*scale*18+k*16*scale+16*scale,current_room_pos[1]*16*scale*10+j*16*scale+16*scale),
                                                                                      scale,
                                                                                      "",
                                                                                      {"idle": utils.animation([0,1],[.3,.3]),"run": utils.animation([2,3],[.2,.2])},
                                                                                      "res/img/basic_enemy.png",
                                                                                      "idle"))
                    been_explored_dict[current_room_pos]=True
                    
                if (i.pos_in_layout[1],i.pos_in_layout[0]) == current_room_pos and len(current_entities)!=0:
                    #rooms_in_layout[i.room_index].been_explored = True
                    room_in_index = i.room_index
                    rooms_in_layout[room_in_index].been_explored= True

                #if all_dead and (i.pos_in_layout[1],i.pos_in_layout[0]) == current_room_pos:
                #        i.is_open = True
            if room_transition_timer <=room_transition_time:
                t = min(room_transition_timer / room_transition_time, 1)
                camera_pos = utils.lerp(camera_start_pos,camera_goal_pos,t)
                player.pos = utils.lerp(player_start_pos,player_goal_pos,t)
            
            else:
                camera_pos = camera_goal_pos

            #if rooms[current_room_index].check_player_collisions(player,camera_pos):
            #    if player.vel.x != 0:
            #        player.pos.x = player.last_pos.x
            #    if player.vel.y != 0:
            #        player.pos.y = player.last_pos.y
            #    print("yeayah")
            #player.last_pos = player.pos

        #if rooms[current_room_index].check_player_collisions(player,camera_pos):
        #    if player.vel.x != 0:
        #        player.pos.x = player.last_pos.x
        #    if player.vel.y != 0:
        #        player.pos.y = player.last_pos.y
        #    print("yeayah")
        #player.last_pos = player.pos
        

        screen.fill("black")

        for i in rooms_in_layout:
                i.draw(screen,camera_pos)
        if edit_mode:
            rooms[current_room_index].draw(screen,camera_pos)
            if not cursor_pos == None:
                transparent_surface = pygame.Surface((1280, 720), pygame.SRCALPHA)
                pygame.draw.rect(transparent_surface,pygame.Color(255,255,255,50),pygame.Rect((utils.vector2(cursor_pos[0]*16*scale,cursor_pos[1]*16*scale)+rooms[current_room_index].pos - camera_pos).to_tuple(),
                                                                                (16*scale,16*scale)))
                screen.blit(transparent_surface,(0,0))
            #rooms[current_room_index].debug_draw_all_tiles(screen)
            font.render_to(screen,(10,10),room_names[current_room_index], "white")
            if edit_mode_adding_entities == False:
                font.render_to(screen,(138,10),"Tile Editing", "white")
                screen.blit(rooms[current_room_index].main_layer.images[current_selected_tile_index],(64*19,0))
            else:
                font.render_to(screen,(138,10),"Entity Editing", "white")
                entities[current_selected_entity_index].draw_display(screen,(64*19,0))
                for i in range(entity_maps[current_room_index].h):
                    for j in range(entity_maps[current_room_index].w):
                        if entity_maps[current_room_index].map[j][i]!="-1":
                            entities[int(entity_maps[current_room_index].map[j][i])].draw_display(screen,(64+i*16*scale,64+j*16*scale))
            for i in doors:
                i.draw(screen,camera_pos)
        else:

            for i in current_pickups:
                i.draw(screen,camera_pos)
            player.draw(screen,camera_pos,delta_time)
            kayou.draw(screen,camera_pos)
            for i in current_entities:
                i.draw(screen,camera_pos,delta_time)
            for i in projectiles:
                i.draw(screen,camera_pos)
            #.draw(screen,camera_pos)
            for i in doors:
                i.draw(screen,camera_pos)
                #i.draw_rect(screen,camera_pos)
            
            screen.blit(ui_sprite,(0,0))
            for i in range(player.max_health):
                if i<=player.current_health-1:
                    screen.blit(heart_images[0],(21*scale + 12*i*scale,0))
                else:
                    screen.blit(heart_images[2],(21*scale + 12*i*scale,0))

            # --- UI de recharge du kayou ---
            bar_x = 200*scale
            bar_y = 5*scale
            bar_w = recharge_bar.get_width()
            bar_h = recharge_bar.get_height()
            #pygame.draw.rect(screen, (60,60,60), (bar_x, bar_y, bar_w, bar_h), border_radius=8)
            fill_ratio = kayou_cooldown / kayou_cooldown_max
            pygame.draw.rect(screen, (80,180,255), (bar_x, bar_y, int((bar_w)*fill_ratio), bar_h), border_radius=0)
            screen.blit(recharge_bar,(bar_x,bar_y))
            #pygame.draw.rect(screen, (255,255,255), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=8)
            screen.blit(little_rock_img, (bar_x-scale*20, bar_y-scale*5))

            if show_minimap:
                # --- Mini-map ---
                minimap_w = 200
                minimap_h = 120
                minimap_x = 1270 - minimap_w - 20
                minimap_y = 720 - minimap_h - 20
                map_rows = len(layout)
                map_cols = len(layout[0])
                cell_w = minimap_w // map_cols
                cell_h = minimap_h // map_rows
                pygame.draw.rect(screen, (30,30,30), (minimap_x-4, minimap_y-4, minimap_w+8, minimap_h+8), border_radius=10)
                pygame.draw.rect(screen, (60,60,60), (minimap_x, minimap_y, minimap_w, minimap_h), border_radius=8)
                for i in range(map_rows):
                    for j in range(map_cols):
                        if layout[i][j] != -1:
                            color = (80,80,80)
                            for r in rooms_in_layout:
                                if hasattr(r, 'been_explored') and r.been_explored and r.pos == utils.vector2(64,64) + utils.vector2(j*scale*16*18,i*scale*16*10):
                                    color = (180,180,180)
                            if (j,i) == current_room_pos:
                                color = (80,180,255)
                            pygame.draw.rect(screen, color, (minimap_x + j*cell_w + 2, minimap_y + i*cell_h + 2, cell_w-4, cell_h-4), border_radius=3)

        if show_fps:
            font.render_to(screen, (10, 10), f"{1/delta_time:.1f}", (255,255,0))
        pygame.display.flip()

    elif state == CREDIT:
        for y in range(720):
            color = (
                int(30 + (y/720)*60),
                int(30 + (y/720)*90),
                int(60 + (y/720)*120)
            )
            pygame.draw.line(screen, color, (0, y), (1280, y))
        big_font = pygame.freetype.Font("res/fonts/Jersey15-Regular.ttf", 72)
        title_rect = big_font.get_rect("Crédits")
        big_font.render_to(screen, (1280//2 - title_rect.width//2, 90), "Crédits", (255,255,255))
        small_font = pygame.freetype.Font("res/fonts/Jersey15-Regular.ttf", 36)
        credit_lines = [
            "par liftyrskinnycat et F3kri",
            "Merci à tous les testeurs !",
        ]
        for i, line in enumerate(credit_lines):
            rect = small_font.get_rect(line)
            small_font.render_to(screen, (1280//2 - rect.width//2, 250 + i*60), line, (220,220,220))
        retour_rect = pygame.Rect((1280//2 - button_w//2, 600), (button_w, button_h))
        draw_button(retour_rect, "RETOUR", (80,180,255), (120,220,255))
        pygame.display.flip()
        continue
    elif state == PAUSE:
        for y in range(720):
            color = (
                int(30 + (y/720)*60),
                int(30 + (y/720)*90),
                int(60 + (y/720)*120)
            )
            pygame.draw.line(screen, color, (0, y), (1280, y))
        big_font = pygame.freetype.Font("res/fonts/Jersey15-Regular.ttf", 72)
        title_rect = big_font.get_rect("Pause")
        big_font.render_to(screen, (1280//2 - title_rect.width//2, 90), "Pause", (255,255,255))
        pause_resume_rect = pygame.Rect((1280//2 - button_w//2, 300), (button_w, button_h))
        pause_settings_rect = pygame.Rect((1280//2 - button_w//2, 430), (button_w, button_h))
        pause_menu_rect = pygame.Rect((1280//2 - button_w//2, 560), (button_w, button_h))
        def draw_button(rect, text, base_color, hover_color):
            mouse_pos = pygame.mouse.get_pos()
            is_hover = rect.collidepoint(mouse_pos)
            color = hover_color if is_hover else base_color
            shadow_rect = rect.copy()
            shadow_rect.x += 6
            shadow_rect.y += 6
            pygame.draw.rect(screen, (0,0,0,80), shadow_rect, border_radius=32)
            pygame.draw.rect(screen, color, rect, border_radius=32)
            text_rect = font.get_rect(text)
            text_x = rect.x + (rect.width - text_rect.width) // 2
            text_y = rect.y + (rect.height - text_rect.height) // 2
            font.render_to(screen, (text_x, text_y), text, (0,0,0))
        if not settings_menu:
            draw_button(pause_resume_rect, "REPRENDRE", (80,180,255), (120,220,255))
            draw_button(pause_settings_rect, "PARAMÈTRES", (120,120,120), (180,180,180))
            draw_button(pause_menu_rect, "MENU PRINCIPAL", (200,60,60), (255,100,100))
        else:
            settings_rect = pygame.Rect((1280//2 - button_w//2, 300), (button_w, button_h))
            draw_button(settings_rect, f"Afficher les FPS : {'OUI' if show_fps else 'NON'}", (80,180,255), (120,220,255))
            minimap_rect = pygame.Rect((1280//2 - button_w//2, 430), (button_w, button_h))
            draw_button(minimap_rect, f"Afficher la mini-map : {'OUI' if show_minimap else 'NON'}", (80,180,255), (120,220,255))
            retour_rect = pygame.Rect((1280//2 - button_w//2, 560), (button_w, button_h))
            draw_button(retour_rect, "RETOUR", (200,60,60), (255,100,100))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if not settings_menu:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if pause_resume_rect.collidepoint(mouse_pos):
                        state = GAME
                    if pause_menu_rect.collidepoint(mouse_pos):
                        state = MENU
                    if pause_settings_rect.collidepoint(mouse_pos):
                        settings_menu = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state = GAME
            else:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if settings_rect.collidepoint(mouse_pos):
                        show_fps = not show_fps
                    if minimap_rect.collidepoint(mouse_pos):
                        show_minimap = not show_minimap
                    if retour_rect.collidepoint(mouse_pos):
                        settings_menu = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        settings_menu = False
        pygame.display.flip()
        continue
    elif state == GAME_OVER:
        for y in range(720):
            color = (
                int(30 + (y/720)*60),
                int(30 + (y/720)*90),
                int(60 + (y/720)*120)
            )
            pygame.draw.line(screen, color, (0, y), (1280, y))
        big_font = pygame.freetype.Font("res/fonts/Jersey15-Regular.ttf", 96)
        title_rect = big_font.get_rect("GAME OVER")
        big_font.render_to(screen, (1280//2 - title_rect.width//2, 120), "GAME OVER", (255,60,60))
        retry_rect = pygame.Rect((1280//2 - button_w//2, 320), (button_w, button_h))
        quit_rect = pygame.Rect((1280//2 - button_w//2, 470), (button_w, button_h))
        def draw_button(rect, text, base_color, hover_color):
            mouse_pos = pygame.mouse.get_pos()
            is_hover = rect.collidepoint(mouse_pos)
            color = hover_color if is_hover else base_color
            shadow_rect = rect.copy()
            shadow_rect.x += 6
            shadow_rect.y += 6
            pygame.draw.rect(screen, (0,0,0,80), shadow_rect, border_radius=32)
            pygame.draw.rect(screen, color, rect, border_radius=32)
            text_rect = font.get_rect(text)
            text_x = rect.x + (rect.width - text_rect.width) // 2
            text_y = rect.y + (rect.height - text_rect.height) // 2
            font.render_to(screen, (text_x, text_y), text, (0,0,0))
        draw_button(retry_rect, "REVENIR AU MENU", (80,180,255), (120,220,255))
        draw_button(quit_rect, "QUITTER", (200,60,60), (255,100,100))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE:
                    import os
                    os.execl(sys.executable, sys.executable, *sys.argv)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if retry_rect.collidepoint(mouse_pos):
                    import os
                    os.execl(sys.executable, sys.executable, *sys.argv)
                if quit_rect.collidepoint(mouse_pos):
                    running = False
        continue
