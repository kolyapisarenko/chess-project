import pygame
from src import config

class BoardRenderer:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font

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

    def render(self):
        self.draw_board()
        self.draw_coordinates()