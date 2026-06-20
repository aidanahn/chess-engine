from .piece import Piece, Color
from typing import Optional
from src.move import Move

class King(Piece):
    DELTAS = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]

    def __init__(self, color: Color) -> None:
        super().__init__(color, 'king')

    def get_moves(self, row: int, col: int, board: list[list[Optional['Piece']]]) -> list[Move]:
        moves = []

        for dr, dc in King.DELTAS:
            tr, tc = row + dr, col + dc

            if not self._is_in_bounds(tr, tc):
                continue

            target = board[tr][tc]

            if target is None:
                moves.append(Move((row, col), (tr, tc)))
            elif target.color != self.color:
                moves.append(Move((row, col), (tr, tc), captured=target))

        return moves