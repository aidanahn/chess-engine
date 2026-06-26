from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterator

from pieces import Pawn

from .board import Board
from .move import Move

if TYPE_CHECKING:
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
    previous_halfmove_clock: int
    previous_draw_reason: str | None

@dataclass
class MoveResult:
    move: Move | None = None
    piece_color: Color | None = None
    captured: bool = False
    gives_check: bool = False
    is_checkmate: bool = False
    is_stalemate: bool = False
    is_draw: bool = False
    draw_reason: str | None = None
    needs_promotion: bool = False

    @property
    def ok(self) -> bool:
        return self.move is not None

@dataclass
class MoveHistoryEntry:
    move: Move
    piece_color: Color
    piece_type: str
    captured_piece_type: str | None
    piece_had_moved: bool
    rook_had_moved: bool | None
    previous_en_passant_sq: Square | None
    previous_halfmove_clock: int
    previous_draw_reason: str | None
    previous_current_turn: Color
    previous_is_game_over: bool
    position_key_after: tuple
    is_castling: bool
    is_en_passant: bool
    promotion: str | None
    gives_check: bool
    is_checkmate: bool
    is_stalemate: bool
    is_draw: bool
    draw_reason: str | None

class Game:
    def __init__(self) -> None:
        self.board = Board()
        self.current_turn: Color = 'white'
        self.is_game_over = False
        self.draw_reason: str | None = None
        self.halfmove_clock = 0
        self.pending_promotion: PendingPromotion | None = None
        self.move_history: list[MoveHistoryEntry] = []
        self._position_counts: dict[tuple, int] = {self._position_key(): 1}

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

    def is_draw(self) -> bool:
        return self.draw_reason is not None

    def legal_moves(self, color: Color | None=None) -> list[Move]:
        return self.board.get_all_legal_moves(color or self.current_turn)

    def try_move(self, from_sq: Square, to_sq: Square) -> MoveResult:
        if self.is_game_over or self.pending_promotion:
            return MoveResult()

        piece = self.piece_at(from_sq)
        if piece is None or piece.color != self.current_turn:
            return MoveResult()

        matching_moves = [
            move for move in self.board.get_legal_moves(*from_sq)
            if move.to_sq == to_sq
        ]
        if not matching_moves:
            return MoveResult()

        move = matching_moves[0]
        promotion_move = next((move for move in matching_moves if move.promotion is not None), None)
        if promotion_move is not None:
            move = Move(
                from_sq=promotion_move.from_sq,
                to_sq=promotion_move.to_sq,
                captured=promotion_move.captured,
                is_en_passant=promotion_move.is_en_passant
            )

        captured = move.captured is not None
        piece_color = piece.color
        piece_had_moved = piece.has_moved
        rook_had_moved = self._castling_rook_had_moved(move)
        previous_en_passant_sq = self.board.en_passant_sq
        previous_halfmove_clock = self.halfmove_clock
        previous_current_turn = self.current_turn
        previous_is_game_over = self.is_game_over
        previous_draw_reason = self.draw_reason
        self.board.make_move(move)

        if self.board.is_promotion_square(move.to_sq, piece_color) and piece.piece_type == 'pawn':
            self.pending_promotion = PendingPromotion(
                move=move,
                piece_color=piece_color,
                captured=captured,
                square=move.to_sq,
                piece_had_moved=piece_had_moved,
                previous_en_passant_sq=previous_en_passant_sq,
                previous_halfmove_clock=previous_halfmove_clock,
                previous_draw_reason=previous_draw_reason
            )
            return MoveResult(
                move=move,
                piece_color=piece_color,
                captured=captured,
                needs_promotion=True
            )

        return self._finish_turn(
            move,
            piece_color,
            captured,
            piece_had_moved=piece_had_moved,
            rook_had_moved=rook_had_moved,
            previous_en_passant_sq=previous_en_passant_sq,
            previous_halfmove_clock=previous_halfmove_clock,
            previous_current_turn=previous_current_turn,
            previous_is_game_over=previous_is_game_over,
            previous_draw_reason=previous_draw_reason
        )

    def cancel_promotion(self) -> None:
        if self.pending_promotion is None:
            return

        pending = self.pending_promotion
        self.pending_promotion = None
        self.board.unmake_move(pending.move)
        self.board.en_passant_sq = pending.previous_en_passant_sq
        self.halfmove_clock = pending.previous_halfmove_clock
        self.draw_reason = pending.previous_draw_reason

        piece = self.board.piece_at(pending.move.from_sq)
        if piece is not None:
            piece.has_moved = pending.piece_had_moved

    def promote(self, piece_type: str) -> MoveResult:
        if self.pending_promotion is None or piece_type not in PROMOTION_CHOICES:
            return MoveResult()

        pending = self.pending_promotion
        self.pending_promotion = None
        pending.move.promotion = piece_type
        self.board.promote_pawn(pending.square, piece_type)

        return self._finish_turn(
            pending.move,
            pending.piece_color,
            pending.captured,
            piece_had_moved=pending.piece_had_moved,
            previous_en_passant_sq=pending.previous_en_passant_sq,
            previous_halfmove_clock=pending.previous_halfmove_clock,
            previous_current_turn=pending.piece_color,
            previous_is_game_over=False,
            previous_draw_reason=pending.previous_draw_reason,
            promotion=piece_type
        )

    def undo_last_move(self) -> MoveHistoryEntry | None:
        if self.pending_promotion:
            self.cancel_promotion()
            return None

        if not self.move_history:
            return None

        entry = self.move_history.pop()
        self._decrement_position_count(entry.position_key_after)
        self.current_turn = entry.previous_current_turn
        self.is_game_over = entry.previous_is_game_over
        self.halfmove_clock = entry.previous_halfmove_clock
        self.draw_reason = entry.previous_draw_reason

        if entry.promotion:
            pawn = Pawn(entry.piece_color)
            pawn.has_moved = entry.piece_had_moved
            self.board.set_piece(entry.move.from_sq, pawn)
            self.board.set_piece(entry.move.to_sq, entry.move.captured)
        else:
            self.board.unmake_move(entry.move)
            piece = self.board.piece_at(entry.move.from_sq)
            if piece is not None:
                piece.has_moved = entry.piece_had_moved

        if entry.is_castling and entry.rook_had_moved is not None:
            rook = self.board.piece_at(self._castling_rook_square(entry.move))
            if rook is not None:
                rook.has_moved = entry.rook_had_moved

        self.board.en_passant_sq = entry.previous_en_passant_sq
        return entry

    def _finish_turn(
        self,
        move: Move,
        piece_color: Color,
        captured: bool,
        piece_had_moved: bool,
        previous_en_passant_sq: Square | None,
        previous_halfmove_clock: int,
        previous_current_turn: Color,
        previous_is_game_over: bool,
        previous_draw_reason: str | None,
        rook_had_moved: bool | None=None,
        promotion: str | None=None
    ) -> MoveResult:
        moved_piece = self.board.piece_at(move.to_sq)
        if moved_piece is None:
            raise ValueError(f"No moved piece found at {move.to_sq}")

        piece_type = 'pawn' if promotion else moved_piece.piece_type
        captured_piece_type = move.captured.piece_type if move.captured is not None else None
        opponent = self._opponent(piece_color)
        self.current_turn = opponent
        self.halfmove_clock = (
            0
            if piece_type == 'pawn' or captured
            else previous_halfmove_clock + 1
        )
        
        gives_check = self.is_in_check(opponent)
        is_checkmate = self.is_in_checkmate(opponent)
        is_stalemate = self.is_in_stalemate(opponent)
        position_key_after = self._position_key()
        self._position_counts[position_key_after] = self._position_counts.get(position_key_after, 0) + 1
        draw_reason = self._draw_reason(is_checkmate, is_stalemate)
        is_draw = draw_reason is not None
        self.draw_reason = draw_reason
        self.is_game_over = is_checkmate or is_stalemate or is_draw

        self.move_history.append(
            MoveHistoryEntry(
                move=move,
                piece_color=piece_color,
                piece_type=piece_type,
                captured_piece_type=captured_piece_type,
                piece_had_moved=piece_had_moved,
                rook_had_moved=rook_had_moved,
                previous_en_passant_sq=previous_en_passant_sq,
                previous_halfmove_clock=previous_halfmove_clock,
                previous_draw_reason=previous_draw_reason,
                previous_current_turn=previous_current_turn,
                previous_is_game_over=previous_is_game_over,
                position_key_after=position_key_after,
                is_castling=move.is_castling,
                is_en_passant=move.is_en_passant,
                promotion=promotion,
                gives_check=gives_check,
                is_checkmate=is_checkmate,
                is_stalemate=is_stalemate,
                is_draw=is_draw,
                draw_reason=draw_reason
            )
        )

        return MoveResult(
            move=move,
            piece_color=piece_color,
            captured=captured,
            gives_check=gives_check,
            is_checkmate=is_checkmate,
            is_stalemate=is_stalemate,
            is_draw=is_draw,
            draw_reason=draw_reason
        )

    def _opponent(self, color: Color) -> Color:
        return 'white' if color == 'black' else 'black'

    def _draw_reason(self, is_checkmate: bool, is_stalemate: bool) -> str | None:
        if is_checkmate or is_stalemate:
            return None

        if self._has_insufficient_material():
            return 'insufficient_material'

        if self.halfmove_clock >= 100:
            return 'fifty_move_rule'

        if self._position_counts.get(self._position_key(), 0) >= 3:
            return 'threefold_repetition'

        return None

    def _has_insufficient_material(self) -> bool:
        pieces = [
            (square, piece)
            for square, piece in self.board.pieces()
            if piece.piece_type != 'king'
        ]

        if not pieces:
            return True

        if any(piece.piece_type in ('pawn', 'rook', 'queen') for _, piece in pieces):
            return False

        if len(pieces) == 1:
            return pieces[0][1].piece_type in ('bishop', 'knight')

        if all(piece.piece_type == 'bishop' for _, piece in pieces):
            return len({self._square_color(square) for square, _ in pieces}) == 1

        return False

    def _position_key(self) -> tuple:
        pieces = tuple(
            sorted(
                (
                    row,
                    col,
                    piece.color,
                    piece.piece_type
                )
                for (row, col), piece in self.board.pieces()
            )
        )
        return (
            self.current_turn,
            pieces,
            self._castling_rights_key(),
            self.board.en_passant_sq
        )

    def _castling_rights_key(self) -> tuple[bool, bool, bool, bool]:
        return (
            self._can_still_castle('white', kingside=True),
            self._can_still_castle('white', kingside=False),
            self._can_still_castle('black', kingside=True),
            self._can_still_castle('black', kingside=False)
        )

    def _can_still_castle(self, color: Color, kingside: bool) -> bool:
        row = 7 if color == 'white' else 0
        rook_col = 7 if kingside else 0
        king = self.board.piece_at((row, 4))
        rook = self.board.piece_at((row, rook_col))
        return (
            king is not None
            and rook is not None
            and king.piece_type == 'king'
            and rook.piece_type == 'rook'
            and king.color == color
            and rook.color == color
            and not king.has_moved
            and not rook.has_moved
        )

    def _square_color(self, square: Square) -> int:
        row, col = square
        return (row + col) % 2

    def _decrement_position_count(self, position_key: tuple) -> None:
        count = self._position_counts.get(position_key, 0)
        if count <= 1:
            self._position_counts.pop(position_key, None)
        else:
            self._position_counts[position_key] = count - 1

    def _castling_rook_had_moved(self, move: Move) -> bool | None:
        if not move.is_castling:
            return None

        rook = self.board.piece_at(self._castling_rook_square(move))
        return rook.has_moved if rook is not None else None

    def _castling_rook_square(self, move: Move) -> Square:
        row, _ = move.from_sq
        _, to_col = move.to_sq
        return (row, 7) if to_col == 6 else (row, 0)
