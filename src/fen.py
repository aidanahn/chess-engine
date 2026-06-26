from __future__ import annotations

from typing import TYPE_CHECKING

from pieces import Bishop, King, Knight, Pawn, Queen, Rook
from pieces.piece import Color

if TYPE_CHECKING:
    from .board import Board, Square
    from .game import Game

STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

PIECE_TO_FEN = {
    'pawn': 'p',
    'knight': 'n',
    'bishop': 'b',
    'rook': 'r',
    'queen': 'q',
    'king': 'k'
}

FEN_TO_PIECE = {
    'p': Pawn,
    'n': Knight,
    'b': Bishop,
    'r': Rook,
    'q': Queen,
    'k': King
}

def game_to_fen(game: Game) -> str:
    return ' '.join((
        board_to_fen(game.board),
        'w' if game.current_turn == 'white' else 'b',
        castling_rights_to_fen(game.board),
        square_to_fen(game.board.en_passant_sq),
        str(game.halfmove_clock),
        str(game.fullmove_number)
    ))

def load_fen(game: Game, fen: str) -> None:
    parts = fen.split()
    if len(parts) != 6:
        raise ValueError('FEN must have 6 fields')

    placement, active_color, castling_rights, en_passant, halfmove_clock, fullmove_number = parts

    _load_piece_placement(game.board, placement)
    game.current_turn = _parse_active_color(active_color)
    game.board.en_passant_sq = fen_to_square(en_passant)
    game.halfmove_clock = _parse_non_negative_int(halfmove_clock, 'halfmove clock')
    game.fullmove_number = _parse_positive_int(fullmove_number, 'fullmove number')
    game.pending_promotion = None
    game.move_history.clear()
    game.draw_reason = None
    game.is_game_over = False

    _apply_has_moved_from_fen(game.board, castling_rights)
    game._position_counts = {game._position_key(): 1}

def board_to_fen(board: Board) -> str:
    ranks = []

    for row in range(8):
        empty_count = 0
        rank = []

        for col in range(8):
            piece = board.piece_at((row, col))
            if piece is None:
                empty_count += 1
                continue

            if empty_count:
                rank.append(str(empty_count))
                empty_count = 0

            symbol = PIECE_TO_FEN[piece.piece_type]
            rank.append(symbol.upper() if piece.color == 'white' else symbol)

        if empty_count:
            rank.append(str(empty_count))

        ranks.append(''.join(rank))

    return '/'.join(ranks)

def castling_rights_to_fen(board: Board) -> str:
    rights = []

    if _can_castle_from_fen_state(board, 'white', kingside=True):
        rights.append('K')
    if _can_castle_from_fen_state(board, 'white', kingside=False):
        rights.append('Q')
    if _can_castle_from_fen_state(board, 'black', kingside=True):
        rights.append('k')
    if _can_castle_from_fen_state(board, 'black', kingside=False):
        rights.append('q')

    return ''.join(rights) or '-'

def square_to_fen(square: Square | None) -> str:
    if square is None:
        return '-'

    row, col = square
    if not (0 <= row < 8 and 0 <= col < 8):
        raise ValueError(f'Square out of bounds: {square}')

    return f'{chr(ord("a") + col)}{8 - row}'

def fen_to_square(square: str) -> Square | None:
    if square == '-':
        return None

    if len(square) != 2 or square[0] < 'a' or square[0] > 'h' or square[1] < '1' or square[1] > '8':
        raise ValueError(f'Invalid FEN square: {square}')

    return (8 - int(square[1]), ord(square[0]) - ord('a'))

def _load_piece_placement(board: Board, placement: str) -> None:
    ranks = placement.split('/')
    if len(ranks) != 8:
        raise ValueError('FEN piece placement must have 8 ranks')

    for row in range(8):
        for col in range(8):
            board.set_piece((row, col), None)

    for row, rank in enumerate(ranks):
        col = 0

        for char in rank:
            if char.isdigit():
                if char == '0':
                    raise ValueError(f'Invalid empty-square count in FEN rank: {rank}')
                col += int(char)
                if col > 8:
                    raise ValueError(f'Too many squares in FEN rank: {rank}')
                continue

            piece_class = FEN_TO_PIECE.get(char.lower())
            if piece_class is None:
                raise ValueError(f'Invalid FEN piece: {char}')
            if col >= 8:
                raise ValueError(f'Too many squares in FEN rank: {rank}')

            color: Color = 'white' if char.isupper() else 'black'
            piece = piece_class(color)
            piece.has_moved = True
            board.set_piece((row, col), piece)
            col += 1

        if col != 8:
            raise ValueError(f'FEN rank does not contain 8 squares: {rank}')

def _parse_active_color(active_color: str) -> Color:
    if active_color == 'w':
        return 'white'
    if active_color == 'b':
        return 'black'
    raise ValueError(f'Invalid active color in FEN: {active_color}')

def _parse_non_negative_int(value: str, label: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise ValueError(f'FEN {label} cannot be negative')
    return parsed

def _parse_positive_int(value: str, label: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise ValueError(f'FEN {label} must be positive')
    return parsed

def _apply_has_moved_from_fen(board: Board, castling_rights: str) -> None:
    if castling_rights != '-':
        invalid = set(castling_rights) - set('KQkq')
        if invalid:
            raise ValueError(f'Invalid castling rights in FEN: {castling_rights}')
        if len(set(castling_rights)) != len(castling_rights):
            raise ValueError(f'Duplicate castling rights in FEN: {castling_rights}')

    for square, piece in board.pieces():
        if piece.piece_type == 'pawn':
            piece.has_moved = not _is_pawn_on_starting_rank(square, piece.color)
        elif piece.piece_type != 'king' and piece.piece_type != 'rook':
            piece.has_moved = False

    _mark_castling_piece(board, (7, 4), 'white', 'king', 'K' in castling_rights or 'Q' in castling_rights)
    _mark_castling_piece(board, (0, 4), 'black', 'king', 'k' in castling_rights or 'q' in castling_rights)
    _mark_castling_piece(board, (7, 7), 'white', 'rook', 'K' in castling_rights)
    _mark_castling_piece(board, (7, 0), 'white', 'rook', 'Q' in castling_rights)
    _mark_castling_piece(board, (0, 7), 'black', 'rook', 'k' in castling_rights)
    _mark_castling_piece(board, (0, 0), 'black', 'rook', 'q' in castling_rights)

def _is_pawn_on_starting_rank(square: Square, color: Color) -> bool:
    row, _ = square
    return (color == 'white' and row == 6) or (color == 'black' and row == 1)

def _mark_castling_piece(board: Board, square: Square, color: Color, piece_type: str, can_castle: bool) -> None:
    piece = board.piece_at(square)
    if can_castle and (piece is None or piece.color != color or piece.piece_type != piece_type):
        raise ValueError(f'FEN castling right does not match piece on {square_to_fen(square)}')
    if piece is not None and piece.color == color and piece.piece_type == piece_type:
        piece.has_moved = not can_castle

def _can_castle_from_fen_state(board: Board, color: Color, kingside: bool) -> bool:
    row = 7 if color == 'white' else 0
    rook_col = 7 if kingside else 0
    king = board.piece_at((row, 4))
    rook = board.piece_at((row, rook_col))
    return (
        king is not None
        and rook is not None
        and king.color == color
        and rook.color == color
        and king.piece_type == 'king'
        and rook.piece_type == 'rook'
        and not king.has_moved
        and not rook.has_moved
    )
