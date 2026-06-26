from __future__ import annotations

from dataclasses import dataclass
from math import inf

from pieces.piece import Color

from .board import Board
from .evaluation import PIECE_VALUES, evaluate_board
from .move import Move

MATE_SCORE = 100_000

@dataclass
class SearchResult:
    move: Move | None
    score: int
    nodes: int

def minimax(board: Board, depth: int, color: Color, perspective: Color | None=None) -> SearchResult:
    _validate_depth(depth)
    perspective = perspective or color
    nodes = [0]
    move, score = _search_minimax(board, depth, color, perspective, nodes, ply=0)
    return SearchResult(move=move, score=score, nodes=nodes[0])

def alpha_beta(
    board: Board,
    depth: int,
    color: Color,
    perspective: Color | None=None,
    alpha: int=-MATE_SCORE,
    beta: int=MATE_SCORE
) -> SearchResult:
    _validate_depth(depth)
    perspective = perspective or color
    nodes = [0]
    move, score = _search_alpha_beta(board, depth, color, perspective, alpha, beta, nodes, ply=0)
    return SearchResult(move=move, score=score, nodes=nodes[0])

def _search_minimax(
    board: Board,
    depth: int,
    color: Color,
    perspective: Color,
    nodes: list[int],
    ply: int
) -> tuple[Move | None, int]:
    nodes[0] += 1
    moves = board.get_all_legal_moves(color)

    if depth == 0 or not moves:
        return None, _score_position(board, color, perspective, moves, ply)

    maximizing = color == perspective
    best_move = None
    best_score = -inf if maximizing else inf

    for move in _ordered_moves(moves):
        state = board.apply_move(move)
        _, score = _search_minimax(board, depth - 1, _opponent(color), perspective, nodes, ply + 1)
        board.undo_move(state)

        if maximizing and score > best_score:
            best_move = move
            best_score = score
        elif not maximizing and score < best_score:
            best_move = move
            best_score = score

    return best_move, int(best_score)

def _search_alpha_beta(
    board: Board,
    depth: int,
    color: Color,
    perspective: Color,
    alpha: int,
    beta: int,
    nodes: list[int],
    ply: int
) -> tuple[Move | None, int]:
    nodes[0] += 1
    moves = board.get_all_legal_moves(color)

    if depth == 0 or not moves:
        return None, _score_position(board, color, perspective, moves, ply)

    maximizing = color == perspective
    best_move = None

    if maximizing:
        best_score = -inf

        for move in _ordered_moves(moves):
            state = board.apply_move(move)
            _, score = _search_alpha_beta(board, depth - 1, _opponent(color), perspective, alpha, beta, nodes, ply + 1)
            board.undo_move(state)

            if score > best_score:
                best_move = move
                best_score = score
            alpha = max(alpha, int(best_score))
            if alpha >= beta:
                break
    else:
        best_score = inf

        for move in _ordered_moves(moves):
            state = board.apply_move(move)
            _, score = _search_alpha_beta(board, depth - 1, _opponent(color), perspective, alpha, beta, nodes, ply + 1)
            board.undo_move(state)

            if score < best_score:
                best_move = move
                best_score = score
            beta = min(beta, int(best_score))
            if alpha >= beta:
                break

    return best_move, int(best_score)

def _score_position(board: Board, color: Color, perspective: Color, moves: list[Move], ply: int) -> int:
    if moves:
        return evaluate_board(board, perspective)

    if board.is_in_check(color):
        return -MATE_SCORE + ply if color == perspective else MATE_SCORE - ply

    return 0

def _ordered_moves(moves: list[Move]) -> list[Move]:
    return sorted(moves, key=_move_order_score, reverse=True)

def _move_order_score(move: Move) -> int:
    score = 0

    if move.captured is not None:
        score += 10_000 + PIECE_VALUES[move.captured.piece_type]

    if move.promotion is not None:
        score += 1_000 + PIECE_VALUES[move.promotion]

    if move.is_castling:
        score += 50

    return score

def _opponent(color: Color) -> Color:
    return 'white' if color == 'black' else 'black'

def _validate_depth(depth: int) -> None:
    if depth < 0:
        raise ValueError('Search depth cannot be negative')
