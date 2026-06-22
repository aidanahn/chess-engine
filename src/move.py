from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pieces.piece import Piece

@dataclass
class Move:
    from_sq: tuple[int, int]
    to_sq: tuple[int, int]
    captured: Piece | None = None
    is_castling: bool = False
