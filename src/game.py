from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterator

from .board import Board

if TYPE_CHECKING:
    from .move import Move
    from pieces import Piece
    from pieces.piece import Color

Square = tuple[int, int]
PROMOTION_CHOICES = ('queen', 'knight', 'rook', 'bishop')

@dataclass
class PendingPromotion:
    move: Move
    piece_color: Color
    captured: bool
    square: Square
    piece_had_moved: bool
    previous_en_passant_sq: Square | None

@dataclass
class MoveResult:
    move: Move | None = None
    piece_color: Color | None = None
    captured: bool = False
    gives_check: bool = False
    is_checkmate: bool = False
    is_stalemate: bool = False
    needs_promotion: bool = False

    @property
    def ok(self) -> bool:
        return self.move is not None

class Game:
    def __init__(self) -> None:
        self.board = Board()
        self.current_turn: Color = 'white'
        self.is_game_over = False
        self.pending_promotion: PendingPromotion | None = None

    def run(self) -> None:
        from .renderer import Renderer

        Renderer(self).run()

    def is_in_bounds(self, square: Square) -> bool:
        row, col = square
        return self.board.is_in_bounds(row, col)

    def piece_at(self, square: Square) -> Piece | None:
        return self.board.piece_at(square)

    def pieces(self) -> Iterator[tuple[Square, Piece]]:
        return self.board.pieces()

    def can_select(self, square: Square) -> bool:
        if self.is_game_over or self.pending_promotion:
            return False

        piece = self.piece_at(square)
        return piece is not None and piece.color == self.current_turn

    def is_in_check(self, color: Color) -> bool:
        return self.board.is_in_check(color)
    
    def is_in_checkmate(self, color: Color) -> bool:
        return self.board.is_in_checkmate(color)

    def is_in_stalemate(self, color: Color) -> bool:
        return self.board.is_in_stalemate(color)

    def try_move(self, from_sq: Square, to_sq: Square) -> MoveResult:
        if self.is_game_over or self.pending_promotion:
            return MoveResult()

        piece = self.piece_at(from_sq)
        if piece is None or piece.color != self.current_turn:
            return MoveResult()

        move = self.board.find_legal_move(from_sq, to_sq)
        if move is None:
            return MoveResult()

        captured = move.captured is not None
        piece_color = piece.color
        piece_had_moved = piece.has_moved
        previous_en_passant_sq = self.board.en_passant_sq
        self.board.make_move(move)

        if self.board.is_promotion_square(move.to_sq, piece_color) and piece.piece_type == 'pawn':
            self.pending_promotion = PendingPromotion(
                move=move,
                piece_color=piece_color,
                captured=captured,
                square=move.to_sq,
                piece_had_moved=piece_had_moved,
                previous_en_passant_sq=previous_en_passant_sq
            )
            return MoveResult(
                move=move,
                piece_color=piece_color,
                captured=captured,
                needs_promotion=True
            )

        return self._finish_turn(move, piece_color, captured)

    def cancel_promotion(self) -> None:
        if self.pending_promotion is None:
            return

        pending = self.pending_promotion
        self.pending_promotion = None
        self.board.unmake_move(pending.move)
        self.board.en_passant_sq = pending.previous_en_passant_sq

        piece = self.board.piece_at(pending.move.from_sq)
        if piece is not None:
            piece.has_moved = pending.piece_had_moved

    def promote(self, piece_type: str) -> MoveResult:
        if self.pending_promotion is None or piece_type not in PROMOTION_CHOICES:
            return MoveResult()

        pending = self.pending_promotion
        self.pending_promotion = None
        self.board.promote_pawn(pending.square, piece_type)

        return self._finish_turn(
            pending.move,
            pending.piece_color,
            pending.captured
        )

    def _finish_turn(self, move: Move, piece_color: Color, captured: bool) -> MoveResult:
        opponent = self._opponent(piece_color)
        self.current_turn = opponent
        
        gives_check = self.is_in_check(opponent)
        is_checkmate = self.is_in_checkmate(opponent)
        is_stalemate = self.is_in_stalemate(opponent)
        self.is_game_over = is_checkmate or is_stalemate

        return MoveResult(
            move=move,
            piece_color=piece_color,
            captured=captured,
            gives_check=gives_check,
            is_checkmate=is_checkmate,
            is_stalemate=is_stalemate
        )

    def _opponent(self, color: Color) -> Color:
        return 'white' if color == 'black' else 'black'
