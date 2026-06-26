from __future__ import annotations

from pieces.piece import Color

from .board import Board
from .move import Move

def perft(board: Board, depth: int, color: Color) -> int:
    if depth < 0:
        raise ValueError('Perft depth cannot be negative')

    if depth == 0:
        return 1

    moves = board.get_all_legal_moves(color)
    if depth == 1:
        return len(moves)

    opponent = _opponent(color)
    nodes = 0

    for move in moves:
        state = board.apply_move(move)
        nodes += perft(board, depth - 1, opponent)
        board.undo_move(state)

    return nodes

def perft_divide(board: Board, depth: int, color: Color) -> list[tuple[str, int]]:
    if depth < 1:
        raise ValueError('Perft divide depth must be at least 1')

    opponent = _opponent(color)
    results = []

    for move in board.get_all_legal_moves(color):
        state = board.apply_move(move)
        nodes = perft(board, depth - 1, opponent)
        board.undo_move(state)
        results.append((format_move(move), nodes))

    return results

def format_move(move: Move) -> str:
    move_text = f'{_square_name(move.from_sq)}{_square_name(move.to_sq)}'
    if move.promotion is not None:
        move_text += move.promotion[0]
    return move_text

def _square_name(square: tuple[int, int]) -> str:
    row, col = square
    return f'{chr(ord("a") + col)}{8 - row}'

def _opponent(color: Color) -> Color:
    return 'white' if color == 'black' else 'black'
