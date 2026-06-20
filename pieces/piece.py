import pygame

class Piece:
    def __init__(self, color, piece_type):
        self.color = color
        self.image = pygame.image.load(f'assets/{color}_{piece_type}.png')
        self.image = pygame.transform.smoothscale(self.image, (720 // 8, 720 // 8))