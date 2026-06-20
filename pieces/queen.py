from .piece import Piece, Color
from typing import Optional

class Queen(Piece):
    DELTAS = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]

    def __init__(self, color: Color) -> None:
        super().__init__(color, 'queen')

    def get_moves(self, row: int, col: int, board: list[list[Optional['Piece']]]) -> list[tuple[int, int]]:
        moves = []

        for delta_row, delta_col in Queen.DELTAS:
            target_row, target_col = row + delta_row, col + delta_col

            while self._is_in_bounds(target_row, target_col):                
                target = board[target_row][target_col]

                if target is None:
                    moves.append((target_row, target_col))
                elif target.color != self.color:
                    moves.append((target_row, target_col))
                    break
                else:
                    break

                target_row += delta_row
                target_col += delta_col
        
        return moves