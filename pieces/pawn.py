from .piece import Piece, Color
from typing import Optional

class Pawn(Piece):
    def __init__(self, color: Color) -> None:
        super().__init__(color, 'pawn')

    def get_moves(self, row: int, col: int, board: list[list[Optional['Piece']]]) -> list[tuple[int, int]]:
        pass