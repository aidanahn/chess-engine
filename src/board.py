from pieces import Rook, Knight, Bishop, Pawn, King, Queen, Piece
from pieces.piece import Color
from typing import Optional
from .move import Move

class Board:
    def __init__(self) -> None:
        self.board: list[list[Optional[Piece]]] = [[None] * 8 for _ in range(8)]
        self.board[0] = [
            Rook('black'), Knight('black'), Bishop('black'), Queen('black'), 
            King('black'), Bishop('black'), Knight('black'), Rook('black')
        ]
        self.board[7] = [
            Rook('white'), Knight('white'), Bishop('white'), Queen('white'), 
            King('white'), Bishop('white'), Knight('white'), Rook('white')
        ]
        self.board[1] = [Pawn('black') for _ in range(8)]
        self.board[6] = [Pawn('white') for _ in range(8)]

    def _is_in_check(self, color: Color):
        for row, rank in enumerate(self.board):
            for col, piece in enumerate(rank):
                if piece and piece.color is not color:
                    for move in piece.get_moves(row, col, self.board):
                        if isinstance(move.captured, King):
                            return True
        return False
    
    def make_move(self, move: Move):
        from_row, from_col = move.from_sq
        to_row, to_col = move.to_sq

        move.captured = self.board[to_row][to_col]
        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = None

    def unmake_move(self, move: Move):
        from_row, from_col = move.from_sq
        to_row, to_col = move.to_sq

        self.board[from_row][from_col] = self.board[to_row][to_col]
        self.board[to_row][to_col] = move.captured