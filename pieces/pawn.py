from .piece import Piece, Color
from typing import Optional
from src.move import Move

class Pawn(Piece):
    def __init__(self, color: Color) -> None:
        super().__init__(color, 'pawn')

    def get_moves(self, row: int, col: int, board: list[list[Optional['Piece']]], is_attacked=None) -> list[Move]:
        moves = []
        direction = 1 if self.color == 'black' else -1

        r1, c1 = row + direction, col
        if self._is_in_bounds(r1, c1) and board[r1][c1] is None:
            moves.append(Move((row, col), (r1, c1)))

            r2, c2 = row + direction * 2, col
            if not self.has_moved and self._is_in_bounds(r2, c2) and board[r2][c2] is None:
                moves.append(Move((row, col), (r2, c2)))

        for dc in (-1, 1):
            tr, tc = row + direction, col + dc
            if self._is_in_bounds(tr, tc):
                target = board[tr][tc]
                if target is not None and target.color != self.color:
                    moves.append(Move((row, col), (tr, tc), captured=target))

        return moves
    
    def get_attacks(self, row: int, col: int, board: list[list[Optional['Piece']]]) -> list[Move]:
        direction = 1 if self.color == 'black' else -1
        attacks = []

        for dc in (-1, 1):
            tr, tc = row + direction, col + dc
            if self._is_in_bounds(tr, tc):
                attacks.append(Move((row, col), (tr, tc)))

        return attacks