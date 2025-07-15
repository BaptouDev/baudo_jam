import pygame
from . import utils

class Enemy:
    def __init__(self, pos: utils.vector2, scale, sheet_path: str, tile_size: int, speed: float = 100):
        self.pos = pos
        self.scale = scale
        self.tile_size = tile_size
        self.speed = speed
        self.direction = utils.vector2(1, 0) 
        self.sprite = pygame.image.load(sheet_path).convert_alpha()
        self.image = pygame.transform.scale(self.sprite, (tile_size * scale, tile_size * scale))
        self.collision_box = pygame.Rect(self.pos.x, self.pos.y, tile_size * scale, tile_size * scale)

    def update(self, dt, collision_layer: utils.level, player_pos=None):
        next_pos = self.pos + self.direction * self.speed * dt
        next_box = pygame.Rect(next_pos.x, next_pos.y, self.tile_size * self.scale, self.tile_size * self.scale)
        if collision_layer.check_player_collision(next_box, utils.vector2(0, 0)):
            self.direction.x *= -1 
        else:
            self.pos = next_pos
        self.collision_box.topleft = (self.pos.x, self.pos.y)

    def draw(self, screen, camera_pos):
        screen.blit(self.image, (self.pos.x - camera_pos.x, self.pos.y - camera_pos.y)) 