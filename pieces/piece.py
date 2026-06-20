from typing import Literal

class Piece:
    def __init__(self, color: Literal['white', 'black']) -> None:
        self.color = color