from .piece import Piece, Color

class King(Piece):
    def __init__(self, color: Color) -> None:
        super().__init__(color, 'king')