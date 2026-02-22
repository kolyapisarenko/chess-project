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

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(config.BG_COLOR)
        renderer.render()
        pygame.display.flip()
        clock.tick(config.FPS)
    pygame.quit()

if __name__ == "__main__":
    main()