import pygame
from board import Board

class Renderer:
    SCREEN_WIDTH = 720
    SCREEN_HEIGHT = 720
    FRAMES_PER_SECOND = 60
    DARK_SQUARE = (115, 149, 82)
    LIGHT_SQUARE = (235, 236, 208)
    SQUARE_SIZE = SCREEN_WIDTH // 8

    def __init__(self, board: Board) -> None:
        self.board = board

        pygame.init()
        pygame.display.set_caption("Chess")
        self.screen = pygame.display.set_mode((Renderer.SCREEN_WIDTH, Renderer.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self) -> None:
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.clear_board()
            self.draw_board()

            pygame.display.flip()

            self.clock.tick(Renderer.FRAMES_PER_SECOND)

        pygame.quit()

    def clear_board(self) -> None:
        self.screen.fill((0, 0, 0))

    def draw_board(self) -> None:
        is_light = True

        for rank in range(8):
            for file in range(8):
                color = Renderer.LIGHT_SQUARE if is_light else Renderer.DARK_SQUARE
                rect = (file * Renderer.SQUARE_SIZE, rank * Renderer.SQUARE_SIZE, 
                        Renderer.SQUARE_SIZE, Renderer.SQUARE_SIZE)
                
                pygame.draw.rect(self.screen, color, rect)
                is_light = not is_light

            is_light = not is_light