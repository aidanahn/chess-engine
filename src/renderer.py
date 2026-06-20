import pygame
from .dragstate import DragState
from .board import Board
from typing import Optional

class Renderer:
    SCREEN_WIDTH: int = 720
    SCREEN_HEIGHT: int = 720
    FRAMES_PER_SECOND: int = 60
    SQUARE_SIZE: int = SCREEN_WIDTH // 8

    DARK_SQUARE: tuple[int, int, int] = (115, 149, 82)
    LIGHT_SQUARE: tuple[int, int, int] = (235, 236, 208)
    
    def __init__(self, board: Board) -> None:
        self.board = board.board
        self._drag: Optional[DragState] = None

        pygame.init()
        pygame.display.set_caption("Chess")
        self.screen = pygame.display.set_mode((Renderer.SCREEN_WIDTH, Renderer.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self) -> None:
        while self.running:
            for event in pygame.event.get():
                self._handle_event(event)

            self._render()
            pygame.display.flip()
            self.clock.tick(Renderer.FRAMES_PER_SECOND)

        pygame.quit()

    def _handle_event(self, event: pygame.event.Event) -> None:
        match event.type:
            case pygame.QUIT:
                self.running = False
            
            case pygame.MOUSEBUTTONDOWN if event.button == 1:
                self._on_mouse_down(*pygame.mouse.get_pos())

            case pygame.MOUSEMOTION if self._drag:
                self._drag.mouse_x, self._drag.mouse_y = pygame.mouse.get_pos()

            case pygame.MOUSEBUTTONUP if event.button == 1 and self._drag:
                self._on_mouse_up(*pygame.mouse.get_pos())

    def _on_mouse_down(self, x: int, y: int) -> None:
        row, col = self._pixel_to_cell(x, y)
        piece = self.board[row][col]
        if piece:
            self.board[row][col] = None
            self._drag = DragState(piece, x, y)

    def _on_mouse_up(self, x: int, y: int) -> None:
        row, col = self._pixel_to_cell(x, y)
        piece = self.board[row][col]
        if piece and piece.color == self._drag.piece.color:
            row, col = self._pixel_to_cell(self._drag.prev_x, self._drag.prev_y)
            self.board[row][col] = self._drag.piece
            self._drag = None
        else:
            self.board[row][col] = self._drag.piece
            self._drag = None

    def _render(self) -> None:
        self.screen.fill((0, 0, 0))
        self._draw_board()
        self._draw_pieces()

    def _draw_board(self) -> None:
        for row in range(8):
            for col in range(8):
                color = Renderer.LIGHT_SQUARE if (row + col) % 2 == 0 else Renderer.DARK_SQUARE
                rect = (col * Renderer.SQUARE_SIZE, row * Renderer.SQUARE_SIZE, 
                        Renderer.SQUARE_SIZE, Renderer.SQUARE_SIZE)
                pygame.draw.rect(self.screen, color, rect)

    def _draw_pieces(self) -> None:
        for row, rank in enumerate(self.board):
            for col, piece in enumerate(rank):
                if piece is not None:
                    x_pos = col * Renderer.SQUARE_SIZE
                    y_pos = row * Renderer.SQUARE_SIZE
                    self.screen.blit(piece.image, (x_pos, y_pos))

        if self._drag:
            self.screen.blit(
                self._drag.piece.image, 
                (self._drag.mouse_x - Renderer.SQUARE_SIZE // 2, self._drag.mouse_y - Renderer.SQUARE_SIZE // 2)
            )

    def _pixel_to_cell(self, x: int, y: int) -> tuple[int, int]:
        return y // Renderer.SQUARE_SIZE, x // Renderer.SQUARE_SIZE