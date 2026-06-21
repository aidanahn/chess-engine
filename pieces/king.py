from .piece import Piece, Color
from typing import Optional
from src.move import Move
from .rook import Rook

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

        return moves + self._get_castle_moves(row, col, board)
    
    def _get_castle_moves(self, row: int, col:int, board: list[list[Optional['Piece']]]) -> list[Move]:
        moves = []

        if self.has_moved:
            return moves
        
        kingside_rook = board[row][7]
        if isinstance(kingside_rook, Rook) and not kingside_rook.has_moved and board[row][5] is None and board[row][6] is None:
            moves.append(Move((row, col), (row, 6), is_castling=True))

        queenside_rook = board[row][0]
        if isinstance(queenside_rook, Rook) and not queenside_rook.has_moved and board[row][1] is None and board[row][2] is None and board[row][3] is None:
            moves.append(Move((row, col), (row, 2), is_castling=True))

        return moves