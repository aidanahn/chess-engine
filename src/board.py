from dataclasses import dataclass
from typing import Iterator, Optional

from pieces import Bishop, King, Knight, Pawn, Piece, Queen, Rook
from pieces.piece import Color

from .move import Move

Square = tuple[int, int]

@dataclass
class BoardMoveState:
    move: Move
    moved_piece: Piece
    captured_piece: Piece | None
    piece_had_moved: bool
    rook: Piece | None
    rook_had_moved: bool | None
    previous_en_passant_sq: Square | None

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
        self.en_passant_sq: Optional[tuple[int, int]] = None

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

    def find_legal_move(self, from_sq: Square, to_sq: Square, promotion: str | None=None) -> Optional[Move]:
        from_row, from_col = from_sq
        for move in self.get_legal_moves(from_row, from_col):
            if move.to_sq == to_sq and (promotion is None or move.promotion == promotion):
                return move
        return None

    def get_legal_moves(self, row: int, col: int) -> list[Move]:
        if not self.is_in_bounds(row, col):
            return []

        piece = self.piece_at((row, col))
        if piece is None:
            return []

        if isinstance(piece, Pawn):
            pseudo_moves = piece.get_moves(row, col, self.board, self.is_square_attacked, self.en_passant_sq)
        else:
            pseudo_moves = piece.get_moves(row, col, self.board, self.is_square_attacked)

        return [
            move for move in pseudo_moves
            if not isinstance(move.captured, King) and not self._would_leave_king_in_check(move, piece.color)
        ]

    def get_all_legal_moves(self, color: Color) -> list[Move]:
        moves = []

        for (row, col), piece in self.pieces():
            if piece.color != color:
                continue

            moves.extend(self.get_legal_moves(row, col))

        return moves

    def is_in_check(self, color: Color) -> bool:
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
    
    def is_in_checkmate(self, color: Color) -> bool:
        if not self.is_in_check(color):
            return False

        return not self.has_legal_moves(color)

    def is_in_stalemate(self, color: Color) -> bool:
        if self.is_in_check(color):
            return False

        return not self.has_legal_moves(color)

    def has_legal_moves(self, color: Color) -> bool:
        return bool(self.get_all_legal_moves(color))

    def is_promotion_square(self, square: Square, color: Color) -> bool:
        row, _ = square
        return (color == 'white' and row == 0) or (color == 'black' and row == 7)

    def promote_pawn(self, square: Square, piece_type: str) -> None:
        pawn = self.piece_at(square)
        if not isinstance(pawn, Pawn):
            raise ValueError(f"No pawn to promote at {square}")

        self.set_piece(square, self._create_promotion_piece(pawn.color, piece_type))

    def _create_promotion_piece(self, color: Color, piece_type: str) -> Piece:
        promotion_pieces = {
            'queen': Queen,
            'rook': Rook,
            'bishop': Bishop,
            'knight': Knight
        }

        piece_class = promotion_pieces.get(piece_type)
        if piece_class is None:
            raise ValueError(f"Invalid promotion piece: {piece_type}")

        promoted_piece = piece_class(color)
        promoted_piece.has_moved = True
        return promoted_piece

    def _would_leave_king_in_check(self, move: Move, color: Color) -> bool:
        state = self.apply_move(move, mark_moved=False)
        in_check = self.is_in_check(color)
        self.undo_move(state)
        return in_check
    
    def is_square_attacked(self, row: int, col: int, by_color: Color) -> bool:
        for r, rank in enumerate(self.board):
            for c, piece in enumerate(rank):
                if piece and piece.color == by_color:
                    for move in piece.get_attacks(r, c, self.board):
                        if move.to_sq == (row, col):
                            return True
        return False
        
    def apply_move(self, move: Move, mark_moved: bool=True) -> BoardMoveState:
        from_row, from_col = move.from_sq
        to_row, to_col = move.to_sq

        piece = self.piece_at(move.from_sq)
        if piece is None:
            raise ValueError(f"No piece to move at {move.from_sq}")

        rook = None
        rook_had_moved = None
        if move.is_castling:
            rook = self.piece_at((to_row, 7 if to_col == 6 else 0))
            rook_had_moved = rook.has_moved if rook is not None else None

        state = BoardMoveState(
            move=move,
            moved_piece=piece,
            captured_piece=move.captured,
            piece_had_moved=piece.has_moved,
            rook=rook,
            rook_had_moved=rook_had_moved,
            previous_en_passant_sq=self.en_passant_sq
        )

        self.set_piece(move.to_sq, piece)
        self.set_piece(move.from_sq, None)

        if move.is_en_passant:
            self.set_piece((from_row, to_col), None)

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

        if isinstance(piece, Pawn) and abs(to_row - from_row) == 2:
            self.en_passant_sq = ((from_row + to_row) // 2, to_col)
        else:
            self.en_passant_sq = None

        if mark_moved and piece is not None:
            piece.has_moved = True

        if isinstance(piece, Pawn) and move.promotion is not None:
            promoted_piece = self._create_promotion_piece(piece.color, move.promotion)
            promoted_piece.has_moved = mark_moved
            self.set_piece(move.to_sq, promoted_piece)

        return state

    def undo_move(self, state: BoardMoveState) -> None:
        move = state.move
        from_row, from_col = move.from_sq
        to_row, to_col = move.to_sq

        self.set_piece(move.from_sq, state.moved_piece)
        self.set_piece(move.to_sq, None)
        state.moved_piece.has_moved = state.piece_had_moved

        if move.is_en_passant:
            self.set_piece((from_row, to_col), state.captured_piece)
        else:
            self.set_piece(move.to_sq, state.captured_piece)

        if move.is_castling:
            if to_col == 6:
                self.set_piece((to_row, 7), state.rook)
                self.set_piece((to_row, 5), None)
            else:
                self.set_piece((to_row, 0), state.rook)
                self.set_piece((to_row, 3), None)

            if state.rook is not None and state.rook_had_moved is not None:
                state.rook.has_moved = state.rook_had_moved

        self.en_passant_sq = state.previous_en_passant_sq

    def make_move(self, move: Move, mark_moved: bool=True) -> None:
        self.apply_move(move, mark_moved=mark_moved)

    def unmake_move(self, move: Move) -> None:
        from_row, from_col = move.from_sq
        to_row, to_col = move.to_sq

        moved_piece = self.piece_at(move.to_sq)
        if move.promotion is not None and moved_piece is not None:
            restored_piece = Pawn(moved_piece.color)
        else:
            restored_piece = moved_piece

        self.set_piece(move.from_sq, restored_piece)
        self.set_piece(move.to_sq, None)

        if move.is_en_passant:
            self.set_piece((from_row, to_col), move.captured)
        else:
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
