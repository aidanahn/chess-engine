from .piece import Piece, Color

class Bishop(Piece):
    def __init__(self, color: Color) -> None:
        super().__init__(color, 'bishop')