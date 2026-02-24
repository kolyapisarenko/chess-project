import pygame
from src import config
from src.ui.renderer import BoardRenderer

def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption(config.TITLE)
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 24)
    renderer = BoardRenderer(screen, font)
    player_clicks = []
    selected_square = ()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    location = pygame.mouse.get_pos()
                    col = (location[0] - config.ORIGIN_X) // config.CELL_SIZE
                    row = (location[1] - config.ORIGIN_Y) // config.CELL_SIZE
                    if 0 <= col < config.COLS and 0 <= row < config.ROWS:
                        print(f"Clicked on cell: ({row}, {col})")
                        selected_square = (row, col)
                        player_clicks.append(selected_square)
                else:
                    pass

        screen.fill(config.BG_COLOR)
        renderer.render()
        pygame.display.flip()
        clock.tick(config.FPS)
    pygame.quit()

if __name__ == "__main__":
    main()