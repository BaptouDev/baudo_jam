import pygame
import pygame.freetype
from src import utils
from src import gen
from src import player
from src import enemy
from src import entity

pygame.init()
screen = pygame.display.set_mode((1280,720))
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
room_names = ["test","shop","start","room1","room2"]
rooms = []
entities = [entity.static_sprite_entity(utils.vector2(0,0),scale,"","res/img/little_guy.png"),
            entity.static_sprite_entity(utils.vector2(0,0),scale,"","res/img/little_rock.png")]
entity_maps=[]
for i in room_names:
    rooms.append(gen.room("res/rooms/"+i+".csv","res/img/sheet.png","res/img/collide_sheet.png",16,utils.vector2(64,64),4,values,{}))
    entity_maps.append(utils.entity_map("res/rooms/entity_maps/"+i+"_e.csv"))
    #rooms.append(utils.level("res/rooms/"+i+".csv","res/img/sheet.png",16,4,utils.vector2(64,64),False,True))

current_room_index = 0


ui_sprite = pygame.image.load("res/img/ui.png")
ui_sprite = pygame.transform.scale_by(ui_sprite,scale)
little_rock_img = pygame.image.load("res/img/little_rock.png")
little_rock_img = pygame.transform.scale_by(little_rock_img,5)

#player_anims = {"idle": utils.animation([0,1],[.3,.3]),
#                "run": utils.animation([0,2],[.2,.2])}
#player = utils.animated_sprite(player_anims,"res/img/player.png",utils.vector2(128,128),scale,16,"idle")
player = player.player(utils.vector2(128,128),scale,"res/img/player.png",16,pygame.Rect(128,128,40,60),pygame.Rect(128,128,40,60))
kayou = utils.rotated_sprite("res/img/rock.png",player.pos,scale,45,0,64.0,16)

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

enemy = enemy.Enemy(utils.vector2(256,256), scale,"res/img/little_guy.png",16)

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
            #rooms_in_layout[x].pos = utils.vector2(64,64) + utils.vector2(j*scale*16*rooms_in_layout[x].h,i*scale*16*rooms_in_layout[x].w)
            if layout[i][j] ==2:
                camera_pos= rooms_in_layout[x].pos.copy()-utils.vector2(64,64)
                camera_goal_pos = rooms_in_layout[x].pos.copy()-utils.vector2(64,64)
                player.pos= rooms_in_layout[x].pos.copy()+utils.vector2(9*16*scale,5*16*scale)
                rooms_in_layout[x].been_explored = True
                rooms_in_index = x
                current_room_pos = (j,i)
            if layout[i][j] ==1:
                rooms_in_layout[x].been_explored = True
            x+=1

collision_layers = []
for i in rooms_in_layout:
    collision_layers.append(i.main_layer)

kayou_cooldown = kayou.max_throw_time 
kayou_cooldown_max = kayou.max_throw_time

current_entities = []
MENU = 0
GAME = 1
CREDIT = 2
state = MENU

button_w, button_h = 400, 100
button_play_rect = pygame.Rect((1280//2 - button_w//2, 300), (button_w, button_h))
button_credit_rect = pygame.Rect((1280//2 - button_w//2, 430), (button_w, button_h))
button_quit_rect = pygame.Rect((1280//2 - button_w//2, 560), (button_w, button_h))

while running:
    current_time = pygame.time.get_ticks()
    delta_time = (current_time-previous_time)/1000
    previous_time = current_time
    room_transition_timer+= delta_time
    re_enter_room_timer-= delta_time
    if kayou.is_thrown:
        kayou_cooldown = kayou.max_throw_time - kayou.throw_timer
        if kayou_cooldown < 0:
            kayou_cooldown = 0
    else:
        if kayou_cooldown == 0:
            kayou_cooldown = kayou_cooldown_max
    
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
                kayou.throw(direction, 800)
        elif state == CREDIT:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                retour_rect = pygame.Rect((1280//2 - button_w//2, 600), (button_w, button_h))
                if retour_rect.collidepoint(pygame.mouse.get_pos()):
                    state = MENU

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
            font.render_to(screen, (rect.x+rect.width//2-70, rect.y+rect.height//2-24), text, (0,0,0))
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
            kayou.update(player.pos,delta_time,collision_layers,camera_pos)
            #kayou.face_mouse(camera_pos)
            enemy.update(delta_time, rooms_in_layout[room_in_index].main_layer, player.pos)
            for i in range(len(current_entities)):
                #if current_entities[i]
                if current_entities[i].is_dead == True:
                    current_entities.pop(i)
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
                    #if rooms_in_layout[i.room_index].been_explored == False:
                    for j in range(len(c)):
                        for k in range(len(c[0])):
                            if c[j][k] =="0":
                                current_entities.append(entity.static_sprite_entity(utils.vector2(current_room_pos[0]*16*scale*18+k*16*scale+16*scale,current_room_pos[1]*16*scale*10+j*16*scale+16*scale),scale,"","res/img/little_guy.png"))
                    
                if (i.pos_in_layout[1],i.pos_in_layout[0]) == current_room_pos:
                    print("yeah")
                    rooms_in_layout[i.room_index].been_explored = True

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
            
            player.draw(screen,camera_pos,delta_time)
            kayou.draw(screen,camera_pos)
            for i in current_entities:
                i.draw(screen,camera_pos)
            enemy.draw(screen,camera_pos)
            for i in doors:
                i.draw(screen,camera_pos)
                #i.draw_rect(screen,camera_pos)
            screen.blit(ui_sprite,(0,0))
            # --- UI de recharge du kayou ---
            bar_x = 250
            bar_y = 25
            bar_w = 120
            bar_h = 24
            pygame.draw.rect(screen, (60,60,60), (bar_x, bar_y, bar_w, bar_h), border_radius=8)
            fill_ratio = kayou_cooldown / kayou_cooldown_max
            pygame.draw.rect(screen, (80,180,255), (bar_x+2, bar_y+2, int((bar_w-4)*fill_ratio), bar_h-4), border_radius=6)
            pygame.draw.rect(screen, (255,255,255), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=8)
            screen.blit(little_rock_img, (bar_x+110, bar_y-34))
            
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

