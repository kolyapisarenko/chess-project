import pygame
import sys
import random
from src import config
from src.ui.renderer import BoardRenderer
from src.engine.chess_engine import GameState, Move
from src.engine.ai_engine import find_best_move

def main():
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption(config.TITLE)
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 24)
    renderer = BoardRenderer(screen, font)
    
    gs = GameState()
    valid_moves = gs.get_valid_moves()
    
    player_clicks = []
    selected_square = ()
    move_made = False
    last_time = pygame.time.get_ticks()
    highlighting_set = set()
    arrows = []
    arrow_start = None
    
    game_started = False 
    game_over_sound_played = False
    game_mode = "PvP"
    player_color = "w"

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        delta_time = current_time - last_time
        last_time = current_time

        if not game_started:
            screen.fill(config.BG_COLOR)
            start_btn_rect, ai_btn_rect = renderer.draw_main_menu() 
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if start_btn_rect.collidepoint(event.pos):
                        game_mode = "PvP"
                        game_started = True
                        last_time = pygame.time.get_ticks()
                    elif ai_btn_rect.collidepoint(event.pos):
                        color_rects = renderer.draw_color_selection()
                        pygame.display.flip()
                        waiting = True
                        while waiting:
                            for e in pygame.event.get():
                                if e.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                                    m_pos = pygame.mouse.get_pos()
                                    for r, c_code in color_rects:
                                        if r.collidepoint(m_pos):
                                            if c_code == "r":
                                                player_color = random.choice(["w", "b"])
                                            else:
                                                player_color = c_code
                                            game_mode = "PvE"
                                            game_started = True
                                            waiting = False
                                            last_time = pygame.time.get_ticks()
            
            pygame.display.flip()
            clock.tick(config.FPS)
            continue

        game_over = gs.checkmate or gs.stealmate or gs.on_time or gs.check_insufficient_material()
        
        if not game_over:
            if gs.white_to_move:
                gs.white_time -= delta_time
            else:
                gs.black_time -= delta_time

            if gs.white_time <= 0:
                gs.white_time = 0
                gs.on_time = True
            if gs.black_time <= 0:
                gs.black_time = 0
                gs.on_time = True

        human_turn = (gs.white_to_move and player_color == "w") or \
                     (not gs.white_to_move and player_color == "b") or \
                     game_mode == "PvP"

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not game_over and human_turn:
                    location = event.pos
                    if event.button == 1:
                        highlighting_set.clear()
                        arrows.clear()
                        
                        col = (location[0] - config.ORIGIN_X) // config.CELL_SIZE
                        row = (location[1] - config.ORIGIN_Y) // config.CELL_SIZE
                        
                        if 0 <= row < config.ROWS and 0 <= col < config.COLS:
                            if (row, col) == selected_square:
                                selected_square = ()
                                player_clicks = []
                            else:        
                                piece = gs.board[row][col]
                                piece_color = True if piece[0] == "w" else False
                                selected_square = (row, col)
                                player_clicks.append(selected_square)
                                
                                if len(player_clicks) == 1:
                                    if (piece_color != gs.white_to_move) or (piece == "--"):
                                        selected_square = ()
                                        player_clicks = []
                                
                                if len(player_clicks) == 2:
                                    move = Move(player_clicks[0], player_clicks[1], gs.board, enpassant_possible=gs.enpassant_possible)
                                    found_move = next((m for m in valid_moves if move == m), None)

                                    if found_move:
                                        if found_move.is_pawn_promotion:
                                            piece_rects = renderer.draw_promotion_menu(gs.white_to_move)
                                            pygame.display.flip()
                                            waiting = True
                                            while waiting:
                                                for e in pygame.event.get():
                                                    if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                                                    if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                                                        m_pos = pygame.mouse.get_pos()
                                                        for r, p_name in piece_rects:
                                                            if r.collidepoint(m_pos):
                                                                found_move.promotion_piece = p_name
                                                                waiting = False
                                        
                                        gs.make_move(found_move)
                                        move_made = True
                                        play_move_sound(found_move, gs)
                                        selected_square = ()
                                        player_clicks = []
                                        valid_moves = gs.get_valid_moves()
                                    else:
                                        if piece_color == gs.white_to_move:
                                            selected_square = (row, col)
                                            player_clicks = [selected_square]
                                        else:
                                            selected_square = ()
                                            player_clicks = []

                if event.button == 3:
                    location = event.pos
                    col = (location[0] - config.ORIGIN_X) // config.CELL_SIZE
                    row = (location[1] - config.ORIGIN_Y) // config.CELL_SIZE
                    if 0 <= row < 8 and 0 <= col < 8:
                        arrow_start = (row, col)
        
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3 and arrow_start is not None:
                    location = pygame.mouse.get_pos()
                    col = (location[0] - config.ORIGIN_X) // config.CELL_SIZE
                    row = (location[1] - config.ORIGIN_Y) // config.CELL_SIZE
                    if 0 <= row < 8 and 0 <= col < 8:
                        arrow_end = (row, col)
                        if arrow_start == arrow_end:
                            if arrow_end in highlighting_set: highlighting_set.remove(arrow_end)
                            else: highlighting_set.add(arrow_end)
                        else:
                            new_arrow = (arrow_start, arrow_end)
                            if new_arrow in arrows: arrows.remove(new_arrow)
                            else: arrows.append(new_arrow)
                    arrow_start = None

        if not game_over and not human_turn and game_started:
            start_thinking = pygame.time.get_ticks()
            ai_move = find_best_move(gs, depth=4)
            end_thinking = pygame.time.get_ticks()
            duration = end_thinking - start_thinking
            if ai_move:
                if gs.white_to_move:
                    gs.white_time -= duration
                else:
                    gs.black_time -= duration
                gs.make_move(ai_move)
                move_made = True
                play_move_sound(ai_move, gs)
                valid_moves = gs.get_valid_moves()
                last_time = pygame.time.get_ticks()

        screen.fill(config.BG_COLOR)
        buttons = renderer.render(gs, selected_square, valid_moves, highlighting_set, arrows)
        
        if game_over and not game_over_sound_played:
            if gs.checkmate:
                pygame.mixer.Sound(config.SOUND_PATH + "move-check.wav").play()
                pygame.time.delay(300) 
                pygame.mixer.Sound(config.SOUND_PATH + "game-over.wav").play()
            else:
                pygame.mixer.Sound(config.SOUND_PATH + "game-over.wav").play()
            game_over_sound_played = True

        if game_over and buttons:
            restart_btn_rect, quit_btn_rect = buttons
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if restart_btn_rect.collidepoint(event.pos):
                        gs = GameState()
                        valid_moves = gs.get_valid_moves()
                        player_clicks, selected_square = [], ()
                        highlighting_set.clear()
                        arrows.clear()
                        move_made = False
                        game_over_sound_played = False
                        game_started = False
                    
                    elif quit_btn_rect.collidepoint(event.pos):
                        running = False
        
        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()

def play_move_sound(move, gs):
    sound_file = "move-self.wav"
    if move.is_pawn_promotion: 
        sound_file = "promote.wav"
    elif move.is_castle_move: 
        sound_file = "castle.wav"
    elif move.piece_captured != "--": 
        sound_file = "capture.wav"
    
    if gs.in_check() and not gs.checkmate:
        sound_file = "move-check.wav"

    pygame.mixer.Sound(config.SOUND_PATH + sound_file).play()

if __name__ == "__main__":
    main()