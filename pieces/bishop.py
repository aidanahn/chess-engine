from .piece import Piece
from typing import Literal

class Bishop(Piece):
    def __init__(self, color: Literal['white', 'black']) -> None:
        super().__init__(color)