from typing import Optional
from pieces.piece import Piece

class Move:
    def __init__(self, from_sq: tuple[int, int], to_sq: tuple[int, int], captured: Optional[Piece]=None):
        self.from_sq = from_sq
        self.to_sq = to_sq
        self.captured = captured