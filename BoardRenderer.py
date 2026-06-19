import pygame

class BoardRenderer:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FRAMES_PER_SECOND = 60

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Chess")

        self.screen = pygame.display.set_mode((BoardRenderer.SCREEN_WIDTH, BoardRenderer.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.fill("purple")

            pygame.display.flip()

            self.clock.tick(BoardRenderer.FRAMES_PER_SECOND)

        pygame.quit()

if __name__ == "__main__":
    renderer = BoardRenderer()
    renderer.run()