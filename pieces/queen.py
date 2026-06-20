from .piece import Piece, Color

class Queen(Piece):
    def __init__(self, color: Color) -> None:
        super().__init__(color, 'queen')