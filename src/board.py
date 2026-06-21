from pieces import Rook, Knight, Bishop, Pawn, King, Queen, Piece
from pieces.piece import Color
from typing import Iterator, Optional
from .move import Move

Square = tuple[int, int]

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

    def is_in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < 8 and 0 <= col < 8

    def piece_at(self, square: Square) -> Optional[Piece]:
        row, col = square
        if not self.is_in_bounds(row, col):
            return None
        return self.board[row][col]

    def set_piece(self, square: Square, piece: Optional[Piece]) -> None:
        row, col = square
        if not self.is_in_bounds(row, col):
            raise ValueError(f"Square out of bounds: {square}")
        self.board[row][col] = piece

    def pieces(self) -> Iterator[tuple[Square, Piece]]:
        for row, rank in enumerate(self.board):
            for col, piece in enumerate(rank):
                if piece is not None:
                    yield (row, col), piece

    def find_legal_move(self, from_sq: Square, to_sq: Square) -> Optional[Move]:
        from_row, from_col = from_sq
        for move in self.get_legal_moves(from_row, from_col):
            if move.to_sq == to_sq:
                return move
        return None

    def get_legal_moves(self, row: int, col: int) -> list[Move]:
        if not self.is_in_bounds(row, col):
            return []

        piece = self.piece_at((row, col))
        if piece is None:
            return []

        pseudo_moves = piece.get_moves(row, col, self.board, self._is_square_attacked)
        return [
            move for move in pseudo_moves
            if not isinstance(move.captured, King) and not self._would_leave_king_in_check(move, piece.color)
        ]

    def _is_in_check(self, color: Color) -> bool:
        king_pos = None
        for row, rank in enumerate(self.board):
            for col, piece in enumerate(rank):
                if isinstance(piece, King) and piece.color == color:
                    king_pos = (row, col)
                    break

        if king_pos is None:
            return True

        for row, rank in enumerate(self.board):
            for col, piece in enumerate(rank):
                if piece and piece.color != color:
                    for move in piece.get_attacks(row, col, self.board):
                        if move.to_sq == king_pos:
                            return True
        return False

    def _would_leave_king_in_check(self, move: Move, color: Color) -> bool:
        self.make_move(move, mark_moved=False)
        in_check = self._is_in_check(color)
        self.unmake_move(move)
        return in_check
    
    def _is_square_attacked(self, row: int, col: int, by_color: Color) -> bool:
        for r, rank in enumerate(self.board):
            for c, piece in enumerate(rank):
                if piece and piece.color == by_color:
                    for move in piece.get_attacks(r, c, self.board):
                        if move.to_sq == (row, col):
                            return True
        return False
        
    def make_move(self, move: Move, mark_moved: bool=True) -> None:
        from_row, from_col = move.from_sq
        to_row, to_col = move.to_sq

        piece = self.piece_at(move.from_sq)
        self.set_piece(move.to_sq, piece)
        self.set_piece(move.from_sq, None)

        if move.is_castling:
            if to_col == 6:
                rook = self.piece_at((to_row, 7))
                self.set_piece((to_row, 5), rook)
                self.set_piece((to_row, 7), None)
            else:
                rook = self.piece_at((to_row, 0))
                self.set_piece((to_row, 3), rook)
                self.set_piece((to_row, 0), None)

            if mark_moved and rook is not None:
                rook.has_moved = True

        if mark_moved and piece is not None:
            piece.has_moved = True

    def unmake_move(self, move: Move) -> None:
        from_row, from_col = move.from_sq
        to_row, to_col = move.to_sq

        self.set_piece(move.from_sq, self.piece_at(move.to_sq))
        self.set_piece(move.to_sq, move.captured)

        if move.is_castling:
            if to_col == 6:
                rook = self.piece_at((to_row, 5))
                self.set_piece((to_row, 7), rook)
                self.set_piece((to_row, 5), None)
            else:
                rook = self.piece_at((to_row, 3))
                self.set_piece((to_row, 0), rook)
                self.set_piece((to_row, 3), None)
