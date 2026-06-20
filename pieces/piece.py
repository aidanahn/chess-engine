import pygame
from typing import Literal

Color = Literal['white', 'black']
PieceType = Literal['pawn', 'bishop', 'rook', 'queen', 'king', 'knight']

class Piece:
    def __init__(self, color: Color, piece_type: PieceType) -> None:
        self.color = color
        self.image = pygame.transform.smoothscale(
            pygame.image.load(f'assets/{color}_{piece_type}.png'), 
            (720 // 8, 720 // 8)
        )