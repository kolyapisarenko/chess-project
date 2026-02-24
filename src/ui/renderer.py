import pygame
from src import config

class BoardRenderer:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.piece_images = {}
        self.load_piece_images()

        light_img = self.light_cell = pygame.image.load(config.CELL_PATH + "square_brown_light.png")
        dark_img = self.dark_cell = pygame.image.load(config.CELL_PATH + "square_brown_dark.png")

        self.light_cell = pygame.transform.scale(light_img, (config.CELL_SIZE, config.CELL_SIZE))
        self.dark_cell = pygame.transform.scale(dark_img, (config.CELL_SIZE, config.CELL_SIZE))

    def draw_board(self):
        for row in range(config.ROWS):
            for col in range(config.COLS):
                image = self.light_cell if (row + col) % 2 == 0 else self.dark_cell
                x = config.ORIGIN_X + col * config.CELL_SIZE
                y = config.ORIGIN_Y + row * config.CELL_SIZE
                self.screen.blit(image, (x, y))

    def draw_coordinates(self):
        letters = ["a", "b", "c", "d", "e", "f", "g", "h"]
        numbers = ["8", "7", "6", "5", "4", "3", "2", "1"]

        for i in range(config.ROWS):
            text = self.font.render(letters[i], True, (255, 255, 255))
            x_pos = config.ORIGIN_X + (i * config.CELL_SIZE) + (config.CELL_SIZE // 2)
            y_pos = config.ORIGIN_Y + (config.BOARD_SIZE) + 10
            text_rect = text.get_rect(center=(x_pos, y_pos))

            self.screen.blit(text, text_rect)

            num = self.font.render(numbers[i], True, (255, 255, 255))
            x_pos = config.ORIGIN_X - 20
            y_pos = config.ORIGIN_Y + (i * config.CELL_SIZE) + (config.CELL_SIZE // 2)
            text_rect = num.get_rect(center=(x_pos, y_pos))
            self.screen.blit(num, text_rect)

    def load_piece_images(self):
        pieces = ["w_pawn", "w_rook", "w_knight", "w_bishop", "w_queen", "w_king",
                "b_pawn", "b_rook", "b_knight", "b_bishop", "b_queen", "b_king"]
        for piece in pieces:
            img = pygame.image.load(config.PIECES_PATH + piece + "_png_128px.png")
            self.piece_images[piece] = pygame.transform.scale(img, (config.PIECE_SIZE, config.PIECE_SIZE))

    def draw_pieces(self, game_state):
        for row in range(config.ROWS):
            for col in range(config.COLS):
                piece = game_state.board[row][col]
                if piece != "--":
                    x = config.ORIGIN_X + (col * config.CELL_SIZE) + config.OFFSET
                    y = config.ORIGIN_Y + (row * config.CELL_SIZE) + config.OFFSET
                    self.screen.blit(self.piece_images[piece], (x, y))

    def _draw_selected_square(self, selected_square):
        if len(selected_square) == 2:
            row, col = selected_square
            x = config.ORIGIN_X + (col * config.CELL_SIZE)
            y = config.ORIGIN_Y + (row * config.CELL_SIZE)
            highlight = pygame.Surface((config.CELL_SIZE, config.CELL_SIZE))
            highlight.fill(config.HIGHLIGHT_COLOR)
            highlight.set_alpha(100)
            self.screen.blit(highlight, (x, y))

    def render(self, game_state, selected_square):
        self.draw_board()
        self.draw_coordinates()
        self._draw_selected_square(selected_square)
        self.draw_pieces(game_state)