import pygame
from src import utils
from src import gen
from src import player
from src import enemy

pygame.init()
screen = pygame.display.set_mode((1280,720))
running = True
scale = 4
cam_speed = 200
hyper_cam_speed = 1000

#terrain_sheet = pygame.image.load("res/img/terrain.png")
#level = utils.level("res/rooms/test.csv","res/img/sheet.png",16,4)
values = [utils.weighted_value(0,1),
          utils.weighted_value(1,1),
          utils.weighted_value(2,1),
          utils.weighted_value(3,1),
          utils.weighted_value(4,1),
          utils.weighted_value(5,1),
          utils.weighted_value(6,1),
          utils.weighted_value(7,1),
          utils.weighted_value(8,1)]
room_names = ["test","room1","room2"]
rooms = []
for i in room_names:
    rooms.append(gen.room("res/rooms/"+i+".csv","res/img/sheet.png","res/img/collide_sheet.png",16,utils.vector2(64,64),4,values,{},{}))
    #rooms.append(utils.level("res/rooms/"+i+".csv","res/img/sheet.png",16,4,utils.vector2(64,64),False,True))

current_room_index = 0


ui_sprite = pygame.image.load("res/img/ui.png")
ui_sprite = pygame.transform.scale_by(ui_sprite,scale)

#player_anims = {"idle": utils.animation([0,1],[.3,.3]),
#                "run": utils.animation([0,2],[.2,.2])}
#player = utils.animated_sprite(player_anims,"res/img/player.png",utils.vector2(128,128),scale,16,"idle")
player = player.player(utils.vector2(128,128),scale,"res/img/player.png",16,pygame.Rect(128,128,40,60),pygame.Rect(128,128,40,60))

previous_time = 0
current_time = 0

camera_pos = utils.vector2(0,0)

#Edit mode variable only for dev:
edit_mode = False
current_cam_speed = 0.0
cursor_pos = (0,0)
current_selected_tile_index = 0
print(gen.generate_chamber(rooms,[],15,10))
ennemi = enemy.Enemy(utils.vector2(300, 300), scale, "res/img/mace.png", 16)
while running:
    current_time = pygame.time.get_ticks()
    delta_time = (current_time-previous_time)/1000
    previous_time = current_time
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                #w = int(input("Width of the map:"))
                #h = int(input("Height of the map:"))
                rooms[current_room_index].clear_main_layer()
            if event.key == pygame.K_e:
                edit_mode = not edit_mode
                if not edit_mode:
                    camera_pos = utils.vector2(0,0)
            if event.key == pygame.K_g and edit_mode:
                if current_room_index < len(rooms)-1:
                    current_room_index +=1
                else:
                    current_room_index=0
            if event.key == pygame.K_KP_PLUS:
                if current_selected_tile_index < len(rooms[current_room_index].main_layer.images)-1:
                    current_selected_tile_index+=1
                else:
                    current_selected_tile_index = 0
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not cursor_pos == None and edit_mode:
            rooms[current_room_index].change_tile(cursor_pos,current_selected_tile_index)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and not cursor_pos == None and edit_mode:
            rooms[current_room_index].change_tile(cursor_pos,-1)

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
        if not cursor_pos==None:
            print(cursor_pos)
    else:
        player.update(delta_time,camera_pos,rooms[current_room_index].main_layer)
        ennemi.update(delta_time, rooms[current_room_index].main_layer, player.pos)
        #if rooms[current_room_index].check_player_collisions(player,camera_pos):
        #    if player.vel.x != 0:
        #        player.pos.x = player.last_pos.x
        #    if player.vel.y != 0:
        #        player.pos.y = player.last_pos.y
        #    print("yeayah")
        #player.last_pos = player.pos
        

    screen.fill("black")

    rooms[current_room_index].draw(screen,camera_pos)
    if edit_mode:
        if not cursor_pos == None:
            transparent_surface = pygame.Surface((1280, 720), pygame.SRCALPHA)
            pygame.draw.rect(transparent_surface,pygame.Color(255,255,255,50),pygame.Rect((utils.vector2(cursor_pos[0]*16*scale,cursor_pos[1]*16*scale)+rooms[current_room_index].pos - camera_pos).to_tuple(),
                                                                            (16*scale,16*scale)))
            screen.blit(transparent_surface,(0,0))
        #rooms[current_room_index].debug_draw_all_tiles(screen)
    else:
        player.draw(screen,camera_pos,delta_time)
        ennemi.draw(screen, camera_pos)
        screen.blit(ui_sprite,(0,0))
        
    pygame.display.flip()

