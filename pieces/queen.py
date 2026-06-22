from typing import Optional

from src.move import Move

from .piece import Color, Piece

class Queen(Piece):
    DELTAS = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]

    def __init__(self, color: Color) -> None:
        super().__init__(color, 'queen')

    def get_moves(self, row: int, col: int, board: list[list[Optional['Piece']]], is_attacked=None) -> list[Move]:
        moves = []

        for dr, dc in Queen.DELTAS:
            tr, tc = row + dr, col + dc

            while self._is_in_bounds(tr, tc):
                target = board[tr][tc]

                if target is None:
                    moves.append(Move((row, col), (tr, tc)))
                elif target.color != self.color:
                    moves.append(Move((row, col), (tr, tc), captured=target))
                    break
                else:
                    break

                tr += dr
                tc += dc

        return moves
