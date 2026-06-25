import pygame
from typing import TYPE_CHECKING, Optional

from .dragstate import DragState
from .game import PROMOTION_CHOICES

if TYPE_CHECKING:
    from .game import Game, MoveResult
    from .move import Move

class Renderer:
    SCREEN_WIDTH: int = 720
    SCREEN_HEIGHT: int = 720
    FRAMES_PER_SECOND: int = 60
    SQUARE_SIZE: int = SCREEN_WIDTH // 8

    DARK_SQUARE: tuple[int, int, int] = (115, 149, 82)
    LIGHT_SQUARE: tuple[int, int, int] = (235, 236, 208)
    MOVE_HINT_COLOR: tuple[int, int, int, int] = (95, 95, 75, 90)
    PROMOTION_PANEL_RADIUS: int = 2
    
    def __init__(self, game: 'Game') -> None:
        self.game = game
        self._drag: Optional[DragState] = None
        self._move_hints: list[Move] = []

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
        self.game_over_sound = pygame.mixer.Sound('assets/sounds/game_end.mp3')
        self.piece_images = self._load_piece_images()
        self._cursor = pygame.SYSTEM_CURSOR_ARROW

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
            
            case pygame.MOUSEBUTTONDOWN if event.button == 1 and self.game.pending_promotion:
                self._on_promotion_click(*pygame.mouse.get_pos())

            case pygame.MOUSEBUTTONDOWN if event.button == 1:
                self._on_mouse_down(*pygame.mouse.get_pos())

            case pygame.MOUSEMOTION if self._drag:
                self._drag.mouse_x, self._drag.mouse_y = pygame.mouse.get_pos()

            case pygame.MOUSEBUTTONUP if event.button == 1 and self._drag:
                self._on_mouse_up(*pygame.mouse.get_pos())

    def _on_mouse_down(self, x: int, y: int) -> None:
        row, col = self._pixel_to_cell(x, y)
        if not self.game.is_in_bounds((row, col)):
            return

        piece = self.game.piece_at((row, col))

        if self.game.can_select((row, col)):
            self._drag = DragState(piece, x, y)
            self._move_hints = [
                move for move in self.game.legal_moves()
                if move.from_sq == (row, col)
            ]

    def _on_mouse_up(self, x: int, y: int) -> None:
        origin_row, origin_col = self._pixel_to_cell(self._drag.origin_x, self._drag.origin_y)
        target_row, target_col = self._pixel_to_cell(x, y)

        if not self.game.is_in_bounds((target_row, target_col)):
            self._drag = None
            return

        result = self.game.try_move(
            (origin_row, origin_col),
            (target_row, target_col)
        )

        if result.ok and not result.needs_promotion:
            self._play_move_sound(result)

        self._drag = None
        self._move_hints = []

    def _play_move_sound(self, result: 'MoveResult') -> None:
        if result.is_checkmate:
            self.check_sound.play()
            self.game_over_sound.play()
            return
        
        if result.is_stalemate:
            self.game_over_sound.play()
            return

        if result.gives_check:
            sound = self.check_sound

        elif result.move and result.move.is_castling:
            sound = self.castle_sound

        elif result.captured:
            sound = self.capture_sound

        else:
            sound = (
                self.self_move_sound 
                if result.piece_color == 'white' 
                else self.opponent_move_sound
            )

        sound.play()

    def _render(self) -> None:
        self.screen.fill((0, 0, 0))
        self._draw_board()
        self._draw_move_hints()
        self._draw_pieces()
        self._draw_drag()
        self._draw_promotion_picker()

    def _draw_board(self) -> None:
        for row in range(8):
            for col in range(8):
                color = Renderer.LIGHT_SQUARE if (row + col) % 2 == 0 else Renderer.DARK_SQUARE
                rect = (col * Renderer.SQUARE_SIZE, row * Renderer.SQUARE_SIZE, 
                        Renderer.SQUARE_SIZE, Renderer.SQUARE_SIZE)
                pygame.draw.rect(self.screen, color, rect)

    def _draw_move_hints(self) -> None:
        if not self._move_hints:
            return

        hint_surface = pygame.Surface(
            (Renderer.SCREEN_WIDTH, Renderer.SCREEN_HEIGHT),
            pygame.SRCALPHA
        )

        for move in self._move_hints:
            row, col = move.to_sq
            center = (
                col * Renderer.SQUARE_SIZE + Renderer.SQUARE_SIZE // 2,
                row * Renderer.SQUARE_SIZE + Renderer.SQUARE_SIZE // 2
            )

            if move.captured:
                radius = Renderer.SQUARE_SIZE // 2
                width = 8
            else:
                radius = Renderer.SQUARE_SIZE // 6
                width = 0

            self._draw_antialiased_circle(
                hint_surface,
                Renderer.MOVE_HINT_COLOR,
                center,
                radius,
                width
            )

        self.screen.blit(hint_surface, (0, 0))

    def _draw_antialiased_circle(
            self,
            surface: pygame.Surface,
            color: tuple[int, int, int, int],
            center: tuple[int, int],
            radius: int,
            width: int=0
    ) -> None:
        scale = 4
        scaled_radius = radius * scale
        scaled_width = width * scale
        padding = max(scaled_width, scale * 2)
        scaled_size = scaled_radius * 2 + padding * 2
        circle_surface = pygame.Surface((scaled_size, scaled_size), pygame.SRCALPHA)

        pygame.draw.circle(
            circle_surface,
            color,
            (scaled_size // 2, scaled_size // 2),
            scaled_radius,
            scaled_width
        )

        final_size = scaled_size // scale
        circle_surface = pygame.transform.smoothscale(
            circle_surface,
            (final_size, final_size)
        )
        rect = circle_surface.get_rect(center=center)
        surface.blit(circle_surface, rect)

    def _draw_pieces(self) -> None:
        for (row, col), piece in self.game.pieces():
            if self._drag:
                origin_row, origin_col = self._pixel_to_cell(self._drag.origin_x, self._drag.origin_y)
                if (row, col) == (origin_row, origin_col):
                    continue

            x_pos = col * Renderer.SQUARE_SIZE
            y_pos = row * Renderer.SQUARE_SIZE
            self.screen.blit(self._piece_image(piece), (x_pos, y_pos))

    def _draw_drag(self) -> None:
        if self._drag:
            self.screen.blit(
                self._piece_image(self._drag.piece), 
                (self._drag.mouse_x - Renderer.SQUARE_SIZE // 2, self._drag.mouse_y - Renderer.SQUARE_SIZE // 2)
            )

    def _pixel_to_cell(self, x: int, y: int) -> tuple[int, int]:
        return y // Renderer.SQUARE_SIZE, x // Renderer.SQUARE_SIZE

    def _load_piece_images(self) -> dict[tuple[str, str], pygame.Surface]:
        images = {}
        piece_types = ('pawn', 'bishop', 'rook', 'queen', 'king', 'knight')

        for color in ('white', 'black'):
            for piece_type in piece_types:
                image = pygame.image.load(f'assets/pieces/{color}_{piece_type}.png').convert_alpha()
                images[(color, piece_type)] = pygame.transform.smoothscale(
                    image,
                    (Renderer.SQUARE_SIZE, Renderer.SQUARE_SIZE)
                )

        return images

    def _piece_image(self, piece) -> pygame.Surface:
        return self.piece_images[(piece.color, piece.piece_type)]

    def _promotion_rects(self) -> list[tuple[str, pygame.Rect]]:
        pending = self.game.pending_promotion
        if pending is None:
            return []

        option_size = Renderer.SQUARE_SIZE
        close_height = option_size // 2
        total_height = option_size * len(PROMOTION_CHOICES) + close_height
        row, col = pending.square
        x = col * option_size
        y = 0 if row == 0 else Renderer.SCREEN_HEIGHT - total_height

        rects = [
            (
                piece_type,
                pygame.Rect(x, y + index * option_size, option_size, option_size)
            )
            for index, piece_type in enumerate(PROMOTION_CHOICES)
        ]
        rects.append(
            (
                'close',
                pygame.Rect(x, y + len(PROMOTION_CHOICES) * option_size, option_size, close_height)
            )
        )
        return rects

    def _on_promotion_click(self, x: int, y: int) -> None:
        for piece_type, rect in self._promotion_rects():
            if not rect.collidepoint(x, y):
                continue

            if piece_type == 'close':
                self.game.cancel_promotion()
                self._set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                return

            else:
                result = self.game.promote(piece_type)
                if result.ok:
                    self._play_move_sound(result)
                return

    def _draw_promotion_picker(self) -> None:
        pending = self.game.pending_promotion
        if pending is None:
            self._set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            return

        rects = self._promotion_rects()
        panel_rect = rects[0][1].unionall([rect for _, rect in rects[1:]])
        pygame.draw.rect(
            self.screen,
            (255, 255, 255),
            panel_rect,
            border_radius=Renderer.PROMOTION_PANEL_RADIUS
        )

        close_rect = rects[-1][1]
        footer_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        footer_rect = close_rect.move(-panel_rect.x, -panel_rect.y)
        pygame.draw.rect(footer_surface, (238, 238, 238), footer_rect)

        panel_mask = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            panel_mask,
            (255, 255, 255, 255),
            panel_mask.get_rect(),
            border_radius=Renderer.PROMOTION_PANEL_RADIUS
        )
        footer_surface.blit(panel_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.screen.blit(footer_surface, panel_rect.topleft)

        mouse_pos = pygame.mouse.get_pos()
        for piece_type, rect in rects:
            if piece_type == 'close':
                font = pygame.font.SysFont(None, 36)
                text = font.render('x', True, (130, 130, 130))
                text_rect = text.get_rect(center=rect.center)
                self.screen.blit(text, text_rect)
            else:
                image = self.piece_images[(pending.piece_color, piece_type)]
                self.screen.blit(image, rect.topleft)

        is_hovering_picker = any(rect.collidepoint(mouse_pos) for _, rect in rects)
        cursor = pygame.SYSTEM_CURSOR_HAND if is_hovering_picker else pygame.SYSTEM_CURSOR_ARROW
        self._set_cursor(cursor)

    def _set_cursor(self, cursor: int) -> None:
        if self._cursor == cursor:
            return

        try:
            pygame.mouse.set_cursor(cursor)
            self._cursor = cursor
        except pygame.error:
            pass
