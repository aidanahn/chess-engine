from __future__ import annotations

from dataclasses import dataclass
from math import inf

from pieces.piece import Color

from .board import Board
from .evaluation import PIECE_VALUES, evaluate_board
from .move import Move

MATE_SCORE = 100_000
DEFAULT_QUIESCENCE_DEPTH = 4

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
    beta: int=MATE_SCORE,
    quiescence_depth: int=DEFAULT_QUIESCENCE_DEPTH
) -> SearchResult:
    _validate_depth(depth)
    _validate_depth(quiescence_depth)
    perspective = perspective or color
    nodes = [0]
    move, score = _search_alpha_beta(
        board,
        depth,
        color,
        perspective,
        alpha,
        beta,
        nodes,
        ply=0,
        quiescence_depth=quiescence_depth
    )
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
    ply: int,
    quiescence_depth: int
) -> tuple[Move | None, int]:
    nodes[0] += 1
    moves = board.get_all_legal_moves(color)

    if not moves:
        return None, _score_terminal_position(board, color, perspective, ply)

    if depth == 0:
        return None, _quiescence(board, alpha, beta, color, perspective, nodes, ply, quiescence_depth)

    maximizing = color == perspective
    best_move = None

    if maximizing:
        best_score = -inf

        for move in _ordered_moves(moves):
            state = board.apply_move(move)
            _, score = _search_alpha_beta(
                board,
                depth - 1,
                _opponent(color),
                perspective,
                alpha,
                beta,
                nodes,
                ply + 1,
                quiescence_depth
            )
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
            _, score = _search_alpha_beta(
                board,
                depth - 1,
                _opponent(color),
                perspective,
                alpha,
                beta,
                nodes,
                ply + 1,
                quiescence_depth
            )
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

    return _score_terminal_position(board, color, perspective, ply)

def _score_terminal_position(board: Board, color: Color, perspective: Color, ply: int) -> int:
    if board.is_in_check(color):
        return -MATE_SCORE + ply if color == perspective else MATE_SCORE - ply

    return 0

def _quiescence(
    board: Board,
    alpha: int,
    beta: int,
    color: Color,
    perspective: Color,
    nodes: list[int],
    ply: int,
    depth_remaining: int
) -> int:
    nodes[0] += 1
    legal_moves = board.get_all_legal_moves(color)

    if not legal_moves:
        return _score_terminal_position(board, color, perspective, ply)

    stand_pat = evaluate_board(board, perspective)

    if color == perspective:
        if stand_pat >= beta:
            return beta
        alpha = max(alpha, stand_pat)
    else:
        if stand_pat <= alpha:
            return alpha
        beta = min(beta, stand_pat)

    if depth_remaining == 0:
        return stand_pat

    captures = [move for move in legal_moves if move.captured is not None]

    if not captures:
        return stand_pat

    if color == perspective:
        best_score = stand_pat

        for move in _ordered_moves(captures):
            state = board.apply_move(move)
            score = _quiescence(
                board,
                alpha,
                beta,
                _opponent(color),
                perspective,
                nodes,
                ply + 1,
                depth_remaining - 1
            )
            board.undo_move(state)

            best_score = max(best_score, score)
            alpha = max(alpha, best_score)
            if alpha >= beta:
                break

        return best_score

    best_score = stand_pat

    for move in _ordered_moves(captures):
        state = board.apply_move(move)
        score = _quiescence(
            board,
            alpha,
            beta,
            _opponent(color),
            perspective,
            nodes,
            ply + 1,
            depth_remaining - 1
        )
        board.undo_move(state)

        best_score = min(best_score, score)
        beta = min(beta, best_score)
        if alpha >= beta:
            break

    return best_score

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
