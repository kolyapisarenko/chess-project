import pygame
from src import config
from src.ui.renderer import BoardRenderer
from src.engine.chess_engine import GameState, Move

def main():
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption(config.TITLE)
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 24)
    renderer = BoardRenderer(screen, font)
    player_clicks = []
    selected_square = ()

    gs = GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False

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
                    if (row, col) == selected_square:
                        selected_square = ()
                        player_clicks = []
                    else:        
                        piece = gs.board[row][col]
                        color = True if piece[0] == "w" else False
                        if 0 <= col < config.COLS and 0 <= row < config.ROWS:
                            print(f"Clicked on cell: ({row}, {col})")
                            selected_square = (row, col)
                            player_clicks.append(selected_square)
                        if len(player_clicks) == 1:
                            if (color != gs.white_to_move) or (piece == "--"):
                                selected_square = ()
                                player_clicks = []                            
                        if len(player_clicks) == 2:
                            move = Move(player_clicks[0], player_clicks[1], gs.board, enpassant_possible=gs.enpassant_possible)
                            found_move = None
                            for m in valid_moves:
                                if move == m:
                                    found_move = m
                                    break

                            if found_move:
                                if found_move.is_pawn_promotion:
                                    piece_rects = renderer.draw_promotion_menu(gs.white_to_move)
                                    waiting_for_choice = True

                                    while waiting_for_choice:
                                        for e in pygame.event.get():
                                            if e.type == pygame.QUIT:
                                                pygame.quit()
                                                exit()
                                            if e.type == pygame.MOUSEBUTTONDOWN:
                                                if e.button == 1:
                                                    mouse_pos = pygame.mouse.get_pos()
                                                    for rect, piece_name in piece_rects:
                                                        if rect.collidepoint(mouse_pos):
                                                            found_move.promotion_piece = piece_name
                                                            waiting_for_choice = False
                                                            break
                                gs.make_move(found_move)
                                move_made = True
                                move_sound = None

                                if found_move.is_pawn_promotion:
                                    move_sound = pygame.mixer.Sound(config.SOUND_PATH + "promote.wav")
                                elif found_move.is_castle_move:
                                    move_sound = pygame.mixer.Sound(config.SOUND_PATH + "castle.wav")
                                elif found_move.piece_captured != "--":
                                    move_sound = pygame.mixer.Sound(config.SOUND_PATH + "capture.wav")
                                else:
                                    move_sound = pygame.mixer.Sound(config.SOUND_PATH + "move-self.wav")

                                if move_sound:
                                    move_sound.play()
                                    
                                if gs.checkmate or gs.stealmate or gs.in_check():
                                    pygame.time.wait(250) 
                                    if gs.checkmate:
                                        pygame.mixer.Sound(config.SOUND_PATH + "move-check.wav").play()
                                        pygame.time.wait(300)
                                        pygame.mixer.Sound(config.SOUND_PATH + "game-over.wav").play()
                                    elif gs.stealmate:
                                        pygame.mixer.Sound(config.SOUND_PATH + "game-over.wav").play()
                                    elif gs.in_check():
                                        pygame.mixer.Sound(config.SOUND_PATH + "move-check.wav").play()

                                selected_square = ()
                                player_clicks = []
                            else:
                                if color == gs.white_to_move:
                                    selected_square = (row, col)
                                    player_clicks = [selected_square]
                                else:
                                    selected_square = ()
                                    player_clicks = []
                else:
                    pass
        
        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False

        screen.fill(config.BG_COLOR)
        renderer.render(gs, selected_square)
        pygame.display.flip()
        clock.tick(config.FPS)
    pygame.quit()

if __name__ == "__main__":
    main()