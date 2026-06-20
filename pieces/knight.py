from .piece import Piece, Color

class Knight(Piece):
    def __init__(self, color: Color) -> None:
        super().__init__(color, 'knight')