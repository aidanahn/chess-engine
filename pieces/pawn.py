from .piece import Piece, Color

class Pawn(Piece):
    def __init__(self, color: Color) -> None:
        super().__init__(color, 'pawn')