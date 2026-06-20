from .piece import Piece, Color
from typing import Optional

class Knight(Piece):
    DELTAS = [
        (1, 2), (-1, 2), (1, -2), (-1, -2), 
        (2, 1), (-2, 1), (2, -1), (-2, -1)
    ]

    def __init__(self, color: Color) -> None:
        super().__init__(color, 'knight')

    def get_moves(self, row: int, col: int, board: list[list[Optional['Piece']]]) -> list[tuple[int, int]]:
        moves = []

        for delta_row, delta_col in Knight.DELTAS:
            target_row, target_col = row + delta_row, col + delta_col

            if not self._is_in_bounds(target_row, target_col):
                continue

            target = board[target_row][target_col]

            if target is None or target.color != self.color:
                moves.append((target_row, target_col))

        return moves