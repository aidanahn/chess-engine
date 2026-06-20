import pygame

class Renderer:
    SCREEN_WIDTH = 720
    SCREEN_HEIGHT = 720
    FRAMES_PER_SECOND = 60
    DARK_SQUARE = (115, 149, 82)
    LIGHT_SQUARE = (235, 236, 208)
    SQUARE_SIZE = SCREEN_WIDTH // 8

    def __init__(self, board):
        self.board = board.board

        pygame.init()
        pygame.display.set_caption("Chess")
        self.screen = pygame.display.set_mode((Renderer.SCREEN_WIDTH, Renderer.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.drag = None

    def run(self):
        while self.running:
            for event in pygame.event.get():
                self._handle_event(event)

            self.clear_board()
            self.draw_board()
            self.draw_pieces()

            pygame.display.flip()

            self.clock.tick(Renderer.FRAMES_PER_SECOND)

        pygame.quit()

    def _handle_event(self, event):
        match event.type:
            case pygame.QUIT:
                self.running = False
            
            case pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    row, col = self.pixel_to_cell(mouse_x, mouse_y)
                    piece = self.board[row][col]
                    if piece:
                        self.board[row][col] = None
                        self.drag = {'piece': piece, 'mouse': (mouse_x, mouse_y)}

            case pygame.MOUSEMOTION:
                if self.drag:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.drag['mouse'] = (mouse_x, mouse_y)

            case pygame.MOUSEBUTTONUP:
                if self.drag:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    row, col = self.pixel_to_cell(mouse_x, mouse_y)
                    self.board[row][col] = self.drag['piece']
                    self.drag = None

    def clear_board(self):
        self.screen.fill((0, 0, 0))

    def draw_board(self):
        is_light = True

        for row in range(8):
            for col in range(8):
                x_pos = col * Renderer.SQUARE_SIZE
                y_pos = row * Renderer.SQUARE_SIZE

                color = Renderer.LIGHT_SQUARE if is_light else Renderer.DARK_SQUARE
                rect = (x_pos, y_pos, Renderer.SQUARE_SIZE, Renderer.SQUARE_SIZE)
                
                pygame.draw.rect(self.screen, color, rect)
                is_light = not is_light

            is_light = not is_light

    def draw_pieces(self):
        for row, rank in enumerate(self.board):
            for col, piece in enumerate(rank):
                if piece is not None:
                    x_pos = col * Renderer.SQUARE_SIZE
                    y_pos = row * Renderer.SQUARE_SIZE
                    self.screen.blit(piece.image, (x_pos, y_pos))

        if self.drag:
            self.screen.blit(self.drag['piece'].image, (self.drag['mouse'][0] - Renderer.SQUARE_SIZE // 2, self.drag['mouse'][1] - Renderer.SQUARE_SIZE // 2))

    def pixel_to_cell(self, x, y):
        col = x // Renderer.SQUARE_SIZE
        row = y // Renderer.SQUARE_SIZE

        return row, col