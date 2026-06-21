from dataclasses import dataclass

from .board import Board
from .move import Move
from pieces.piece import Color

Square = tuple[int, int]

@dataclass
class MoveResult:
    move: Move | None = None
    piece_color: Color | None = None
    captured: bool = False
    gives_check: bool = False

    @property
    def ok(self) -> bool:
        return self.move is not None

class Game:
    def __init__(self) -> None:
        self.board = Board()
        self.current_turn: Color = 'white'

    def run(self) -> None:
        from .renderer import Renderer

        Renderer(self).run()

    def can_select(self, square: Square) -> bool:
        piece = self.board.piece_at(square)
        return piece is not None and piece.color == self.current_turn

    def try_move(self, from_sq: Square, to_sq: Square) -> MoveResult:
        piece = self.board.piece_at(from_sq)
        if piece is None or piece.color != self.current_turn:
            return MoveResult()

        move = self.board.find_legal_move(from_sq, to_sq)
        if move is None:
            return MoveResult()

        captured = move.captured is not None
        piece_color = piece.color
        self.board.make_move(move)

        opponent = self._opponent(piece_color)
        gives_check = self.board._is_in_check(opponent)
        self.current_turn = opponent

        return MoveResult(
            move=move,
            piece_color=piece_color,
            captured=captured,
            gives_check=gives_check
        )

    def _opponent(self, color: Color) -> Color:
        return 'white' if color == 'black' else 'black'
