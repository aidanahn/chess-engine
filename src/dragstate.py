from pieces import Piece

class DragState:
    def __init__(self, piece: Piece, mouse_x: int, mouse_y: int) -> None:
        self.piece = piece
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y
        self.origin_x = mouse_x
        self.origin_y = mouse_y