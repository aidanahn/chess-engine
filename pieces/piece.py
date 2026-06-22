from abc import ABC, abstractmethod
from typing import Literal, Optional

import pygame

Color = Literal['white', 'black']
PieceType = Literal['pawn', 'bishop', 'rook', 'queen', 'king', 'knight']

class Piece(ABC):
    def __init__(self, color: Color, piece_type: PieceType) -> None:
        self.color = color
        self.has_moved = False
        self.image = pygame.transform.smoothscale(
            pygame.image.load(f'assets/pieces/{color}_{piece_type}.png'), 
            (720 // 8, 720 // 8)
        )

    @abstractmethod
    def get_moves(self, row: int, col: int, board: list[list[Optional['Piece']]], is_attacked=None):
        pass

    def get_attacks(self, row: int, col: int, board: list[list[Optional['Piece']]]):
        return self.get_moves(row, col, board)

    def _is_in_bounds(self, row: int, col: int) -> bool:
        return 0 <= col < 8 and 0 <= row < 8
