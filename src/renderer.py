import pygame
from .dragstate import DragState
from .board import Board
from typing import Optional
from pieces.piece import Color

class Renderer:
    SCREEN_WIDTH: int = 720
    SCREEN_HEIGHT: int = 720
    FRAMES_PER_SECOND: int = 60
    SQUARE_SIZE: int = SCREEN_WIDTH // 8

    DARK_SQUARE: tuple[int, int, int] = (115, 149, 82)
    LIGHT_SQUARE: tuple[int, int, int] = (235, 236, 208)
    
    def __init__(self, board: Board) -> None:
        self.board = board
        self._drag: Optional[DragState] = None
        self.current_turn: Color = 'white'

        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("Chess")
        self.screen = pygame.display.set_mode((Renderer.SCREEN_WIDTH, Renderer.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.start_sound = pygame.mixer.Sound('assets/sounds/game_start.mp3')
        self.self_move_sound = pygame.mixer.Sound('assets/sounds/move_self.mp3')
        self.opponent_move_sound = pygame.mixer.Sound('assets/sounds/move_opponent.mp3')
        self.capture_sound = pygame.mixer.Sound('assets/sounds/capture.mp3')
        self.check_sound = pygame.mixer.Sound('assets/sounds/move_check.mp3')
        self.castle_sound = pygame.mixer.Sound('assets/sounds/castle.mp3')

    def run(self) -> None:
        self.start_sound.play()

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
        if not self.board.is_in_bounds(row, col):
            return

        piece = self.board.board[row][col]

        if piece and piece.color == self.current_turn:
            self._drag = DragState(piece, x, y)

    def _on_mouse_up(self, x: int, y: int) -> None:
        origin_row, origin_col = self._pixel_to_cell(self._drag.origin_x, self._drag.origin_y)
        target_row, target_col = self._pixel_to_cell(x, y)

        if not self.board.is_in_bounds(target_row, target_col):
            self._drag = None
            return

        target = self.board.board[target_row][target_col]

        matched_move = None
        for move in self.board.get_legal_moves(origin_row, origin_col):
            if (target_row, target_col) == move.to_sq:
                matched_move = move
                break

        if matched_move:
            self.board.make_move(matched_move)

            opponent = 'white' if self._drag.piece.color == 'black' else 'black'
            if self.board._is_in_check(opponent):
                sound = self.check_sound
            elif matched_move.is_castling:
                sound = self.castle_sound
            elif target:
                sound = self.capture_sound
            else:
                sound = self.self_move_sound if self._drag.piece.color == 'white' else self.opponent_move_sound

            sound.play()
            self.current_turn = opponent

        self._drag = None

    def _render(self) -> None:
        self.screen.fill((0, 0, 0))
        self._draw_board()
        self._draw_pieces()
        self._draw_drag()

    def _draw_board(self) -> None:
        for row in range(8):
            for col in range(8):
                color = Renderer.LIGHT_SQUARE if (row + col) % 2 == 0 else Renderer.DARK_SQUARE
                rect = (col * Renderer.SQUARE_SIZE, row * Renderer.SQUARE_SIZE, 
                        Renderer.SQUARE_SIZE, Renderer.SQUARE_SIZE)
                pygame.draw.rect(self.screen, color, rect)

    def _draw_pieces(self) -> None:
        for row, rank in enumerate(self.board.board):
            for col, piece in enumerate(rank):
                if piece is not None:
                    if self._drag:
                        origin_row, origin_col = self._pixel_to_cell(self._drag.origin_x, self._drag.origin_y)
                        if (row, col) == (origin_row, origin_col):
                            continue

                    x_pos = col * Renderer.SQUARE_SIZE
                    y_pos = row * Renderer.SQUARE_SIZE
                    self.screen.blit(piece.image, (x_pos, y_pos))

    def _draw_drag(self) -> None:
        if self._drag:
            self.screen.blit(
                self._drag.piece.image, 
                (self._drag.mouse_x - Renderer.SQUARE_SIZE // 2, self._drag.mouse_y - Renderer.SQUARE_SIZE // 2)
            )

    def _pixel_to_cell(self, x: int, y: int) -> tuple[int, int]:
        return y // Renderer.SQUARE_SIZE, x // Renderer.SQUARE_SIZE
