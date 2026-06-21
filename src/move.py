from dataclasses import dataclass
from typing import Optional
from pieces.piece import Piece

@dataclass
class Move:
    from_sq: tuple[int, int]
    to_sq: tuple[int, int]
    captured: Optional[Piece] = None
    is_castling: bool = False
