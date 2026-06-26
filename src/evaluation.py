from __future__ import annotations

from typing import TYPE_CHECKING

from pieces.piece import Color, PieceType

if TYPE_CHECKING:
    from .board import Board, Square

PIECE_VALUES: dict[PieceType, int] = {
    'pawn': 100,
    'knight': 320,
    'bishop': 330,
    'rook': 500,
    'queen': 900,
    'king': 0
}

PIECE_SQUARE_TABLES: dict[PieceType, tuple[tuple[int, ...], ...]] = {
    'pawn': (
        (0, 0, 0, 0, 0, 0, 0, 0),
        (50, 50, 50, 50, 50, 50, 50, 50),
        (10, 10, 20, 30, 30, 20, 10, 10),
        (5, 5, 10, 25, 25, 10, 5, 5),
        (0, 0, 0, 20, 20, 0, 0, 0),
        (5, -5, -10, 0, 0, -10, -5, 5),
        (5, 10, 10, -20, -20, 10, 10, 5),
        (0, 0, 0, 0, 0, 0, 0, 0)
    ),
    'knight': (
        (-50, -40, -30, -30, -30, -30, -40, -50),
        (-40, -20, 0, 5, 5, 0, -20, -40),
        (-30, 5, 10, 15, 15, 10, 5, -30),
        (-30, 0, 15, 20, 20, 15, 0, -30),
        (-30, 5, 15, 20, 20, 15, 5, -30),
        (-30, 0, 10, 15, 15, 10, 0, -30),
        (-40, -20, 0, 0, 0, 0, -20, -40),
        (-50, -40, -30, -30, -30, -30, -40, -50)
    ),
    'bishop': (
        (-20, -10, -10, -10, -10, -10, -10, -20),
        (-10, 5, 0, 0, 0, 0, 5, -10),
        (-10, 10, 10, 10, 10, 10, 10, -10),
        (-10, 0, 10, 10, 10, 10, 0, -10),
        (-10, 5, 5, 10, 10, 5, 5, -10),
        (-10, 0, 5, 10, 10, 5, 0, -10),
        (-10, 0, 0, 0, 0, 0, 0, -10),
        (-20, -10, -10, -10, -10, -10, -10, -20)
    ),
    'rook': (
        (0, 0, 0, 5, 5, 0, 0, 0),
        (-5, 0, 0, 0, 0, 0, 0, -5),
        (-5, 0, 0, 0, 0, 0, 0, -5),
        (-5, 0, 0, 0, 0, 0, 0, -5),
        (-5, 0, 0, 0, 0, 0, 0, -5),
        (-5, 0, 0, 0, 0, 0, 0, -5),
        (5, 10, 10, 10, 10, 10, 10, 5),
        (0, 0, 0, 0, 0, 0, 0, 0)
    ),
    'queen': (
        (-20, -10, -10, -5, -5, -10, -10, -20),
        (-10, 0, 5, 0, 0, 0, 0, -10),
        (-10, 5, 5, 5, 5, 5, 0, -10),
        (0, 0, 5, 5, 5, 5, 0, -5),
        (-5, 0, 5, 5, 5, 5, 0, -5),
        (-10, 0, 5, 5, 5, 5, 0, -10),
        (-10, 0, 0, 0, 0, 0, 0, -10),
        (-20, -10, -10, -5, -5, -10, -10, -20)
    ),
    'king': (
        (20, 30, 10, 0, 0, 10, 30, 20),
        (20, 20, 0, 0, 0, 0, 20, 20),
        (-10, -20, -20, -20, -20, -20, -20, -10),
        (-20, -30, -30, -40, -40, -30, -30, -20),
        (-30, -40, -40, -50, -50, -40, -40, -30),
        (-30, -40, -40, -50, -50, -40, -40, -30),
        (-30, -40, -40, -50, -50, -40, -40, -30),
        (-30, -40, -40, -50, -50, -40, -40, -30)
    )
}

def evaluate_board(board: Board, perspective: Color='white') -> int:
    score = 0

    for square, piece in board.pieces():
        piece_score = PIECE_VALUES[piece.piece_type] + _piece_square_bonus(piece.piece_type, piece.color, square)
        score += piece_score if piece.color == 'white' else -piece_score

    return score if perspective == 'white' else -score

def _piece_square_bonus(piece_type: PieceType, color: Color, square: Square) -> int:
    row, col = square
    table_row = row if color == 'white' else 7 - row
    return PIECE_SQUARE_TABLES[piece_type][table_row][col]
