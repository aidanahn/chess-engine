from .renderer import Renderer
from .board import Board

class Game:
    def __init__(self) -> None:
        self.board = Board()
        self.renderer = Renderer(self.board)

    def run(self) -> None:
        self.renderer.run()