import pygame
import math
from src import config

class BoardRenderer:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.piece_images = {}
        self.material_piece_images = {}
        self.load_piece_images()
        self.load_material_piece_images()

        light_img = self.light_cell = pygame.image.load(config.CELL_PATH + "square_brown_light.png")
        dark_img = self.dark_cell = pygame.image.load(config.CELL_PATH + "square_brown_dark.png")
        analyse_light_img = self.analyse_light_cell = pygame.image.load(config.CELL_PATH + "square_gray_light.png")
        analyse_dark_img = self.analyse_dark_cell = pygame.image.load(config.CELL_PATH + "square_gray_dark.png")

        self.light_cell = pygame.transform.scale(light_img, (config.CELL_SIZE, config.CELL_SIZE))
        self.dark_cell = pygame.transform.scale(dark_img, (config.CELL_SIZE, config.CELL_SIZE))
        self.analyse_light_cell = pygame.transform.scale(analyse_light_img, (config.CELL_SIZE, config.CELL_SIZE))
        self.analyse_dark_cell = pygame.transform.scale(analyse_dark_img, (config.CELL_SIZE, config.CELL_SIZE))

    def draw_board(self):
        for row in range(config.ROWS):
            for col in range(config.COLS):
                image = self.light_cell if (row + col) % 2 == 0 else self.dark_cell
                x = config.ORIGIN_X + col * config.CELL_SIZE
                y = config.ORIGIN_Y + row * config.CELL_SIZE
                self.screen.blit(image, (x, y))

    def draw_analyse_highlight(self, highlighting_set):
        for row, col in highlighting_set:
            image = self.analyse_light_cell if (row + col) % 2 == 0 else self.analyse_dark_cell
            x = config.ORIGIN_X + col * config.CELL_SIZE
            y = config.ORIGIN_Y + row * config.CELL_SIZE
            self.screen.blit(image, (x, y))

    def draw_arrows(self, arrows):
        arrows_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        color = (255, 255, 0, 100)
        line_width = 20
        head_len = 45

        for arrow in arrows:
            start_row = arrow[0][0]
            start_col = arrow[0][1]
            end_row = arrow[1][0]
            end_col = arrow[1][1]

            x1 = config.ORIGIN_X + (start_col * config.CELL_SIZE) + (config.CELL_SIZE // 2)
            y1 = config.ORIGIN_Y + (start_row * config.CELL_SIZE) + (config.CELL_SIZE // 2)
            x2 = config.ORIGIN_X + (end_col * config.CELL_SIZE) + (config.CELL_SIZE // 2)
            y2 = config.ORIGIN_Y + (end_row * config.CELL_SIZE) + (config.CELL_SIZE // 2)

            pivot_x, pivot_y = x1, y1
            if (abs(start_row - end_row) == 2 and abs(start_col - end_col) == 1):
                pivot_x, pivot_y = x1, y2
            elif (abs(start_row - end_row) == 1 and abs(start_col - end_col) == 2):
                pivot_x, pivot_y = x2, y1
            angle = math.atan2(y2 - pivot_y, x2 - pivot_x)
            shorten_dist = 25
            line_end_x = x2 - shorten_dist * math.cos(angle)
            line_end_y = y2 - shorten_dist * math.sin(angle)

            if (abs(start_row - end_row) == 2 and abs(start_col - end_col) == 1) or (abs(start_row - end_row) == 1 and abs(start_col - end_col) == 2):
                pygame.draw.line(arrows_surface, color, (x1, y1), (pivot_x, pivot_y), line_width)
                pygame.draw.circle(arrows_surface, color, (pivot_x, pivot_y), line_width // 2)
                pygame.draw.line(arrows_surface, color, (pivot_x, pivot_y), (line_end_x, line_end_y), line_width)
            else:
                perl_angle = angle + math.pi / 2
                dx = (line_width / 2) * math.cos(perl_angle)
                dy = (line_width / 2) * math.sin(perl_angle)
                p1 = (x1 + dx, y1 + dy)
                p2 = (x1 - dx, y1 - dy)
                p3 = (line_end_x - dx, line_end_y - dy)
                p4 = (line_end_x + dx, line_end_y + dy)
                pygame.draw.polygon(arrows_surface, color, [p1, p2, p3, p4])

            point = (x2, y2)
            left = (x2 - head_len * math.cos(angle - 0.6), y2 - head_len * math.sin(angle - 0.6))
            right = (x2 - head_len * math.cos(angle + 0.6), y2 - head_len * math.sin(angle + 0.6))
            pygame.draw.polygon(arrows_surface, color, [point, left, right])

        self.screen.blit(arrows_surface, (0, 0))

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

    def load_material_piece_images(self):
        size = config.CELL_SIZE // 4
        pieces = ["w_pawn", "w_rook", "w_knight", "w_bishop", "w_queen", "w_king",
                "b_pawn", "b_rook", "b_knight", "b_bishop", "b_queen", "b_king"]
        for piece in pieces:
            img = pygame.image.load(config.PIECES_PATH + piece + "_png_128px.png")
            self.material_piece_images[piece] = pygame.transform.scale(img, (size, size))

    def draw_pieces(self, game_state):
        for row in range(config.ROWS):
            for col in range(config.COLS):
                piece = game_state.board[row][col]
                if piece != "--":
                    x = config.ORIGIN_X + (col * config.CELL_SIZE) + config.OFFSET
                    y = config.ORIGIN_Y + (row * config.CELL_SIZE) + config.OFFSET
                    self.screen.blit(self.piece_images[piece], (x, y))

    def _draw_selected_square(self, game_state, selected_square, valid_moves):
        if len(game_state.move_log) > 0:
            last_move = game_state.move_log[-1]

            history_surface = pygame.Surface((config.CELL_SIZE, config.CELL_SIZE))
            history_surface.fill(config.HIGHLIGHT_COLOR)
            history_surface.set_alpha(80)

            start_x = config.ORIGIN_X + (last_move.start_col * config.CELL_SIZE)
            start_y = config.ORIGIN_Y + (last_move.start_row * config.CELL_SIZE)
            self.screen.blit(history_surface, (start_x, start_y))

            end_x = config.ORIGIN_X + (last_move.end_col * config.CELL_SIZE)
            end_y = config.ORIGIN_Y + (last_move.end_row * config.CELL_SIZE)
            self.screen.blit(history_surface, (end_x, end_y))

        if selected_square:
                row, col = selected_square
                if game_state.board[row][col] != "--":
                    x = config.ORIGIN_X + (col * config.CELL_SIZE)
                    y = config.ORIGIN_Y + (row * config.CELL_SIZE)
                    highlight = pygame.Surface((config.CELL_SIZE, config.CELL_SIZE))
                    highlight.fill(config.HIGHLIGHT_COLOR)
                    highlight.set_alpha(150)
                    self.screen.blit(highlight, (x, y))

        if selected_square:
            row, col = selected_square
            piece = game_state.board[row][col]
            if piece != "--" and (piece[0] == "w" if game_state.white_to_move else "b"):
                for move in valid_moves:
                    if move.start_row == row and move.start_col == col:
                        center_x = config.ORIGIN_X + (move.end_col * config.CELL_SIZE)
                        center_y = config.ORIGIN_Y + (move.end_row * config.CELL_SIZE)

                        target = game_state.board[move.end_row][move.end_col]
                        hint_color = (0, 0, 0, 80)

                        if target == "--" and not move.is_enpassant_move:
                            s = pygame.Surface((config.CELL_SIZE, config.CELL_SIZE), pygame.SRCALPHA)
                            pygame.draw.circle(s, hint_color, (config.CELL_SIZE // 2, config.CELL_SIZE // 2), 12)
                            self.screen.blit(s, (center_x, center_y))
                        elif target != "--" or move.is_enpassant_move:
                            s = pygame.Surface((config.CELL_SIZE, config.CELL_SIZE), pygame.SRCALPHA)
                            pygame.draw.circle(s, hint_color, (config.CELL_SIZE // 2, config.CELL_SIZE // 2), config.CELL_SIZE // 2 - 2, 6)
                            self.screen.blit(s, (center_x, center_y)) 

    def draw_promotion_menu(self, is_white):
        color = "w" if is_white else "b"
        pieces = ["queen", "rook", "bishop", "knight"]

        menu_width = config.CELL_SIZE * 4
        menu_height = config.CELL_SIZE
        start_x = (config.SCREEN_WIDTH - menu_width) // 2
        start_y = (config.SCREEN_HEIGHT - menu_height) // 2

        menu_rect = pygame.Rect(start_x, start_y, menu_width, menu_height)
        pygame.draw.rect(self.screen, (50, 50, 50), menu_rect)
        pygame.draw.rect(self.screen, (200, 200, 200), menu_rect, 3)

        piece_rects = []
        for i, piece_name in enumerate(pieces):
            piece_img_rect = f"{color}_{piece_name}"
            img = self.piece_images[piece_img_rect]
            rect = pygame.Rect(start_x + i * config.CELL_SIZE, start_y, config.CELL_SIZE, config.CELL_SIZE)
            img_rect = img.get_rect(center=rect.center)
            self.screen.blit(img, img_rect)
            piece_rects.append((rect, piece_name))
        pygame.display.flip()
        return piece_rects

    def draw_color_selection(self):
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((10, 10, 10))
        self.screen.blit(overlay, (0, 0))

        selection_width = config.CELL_SIZE * 3
        selection_height = config.CELL_SIZE
        start_x = (config.SCREEN_WIDTH - selection_width) // 2
        start_y = (config.SCREEN_HEIGHT - selection_height) // 2
        
        title_font = pygame.font.SysFont("Arial", 32, bold=True)
        title_surf = title_font.render("CHOOSE YOUR SIDE", True, (212, 175, 55))
        title_rect = title_surf.get_rect(center=(config.SCREEN_WIDTH // 2, start_y - 40))
        self.screen.blit(title_surf, title_rect)

        selection_rect = pygame.Rect(start_x, start_y, selection_width, selection_height)
        pygame.draw.rect(self.screen, (40, 40, 40), selection_rect)
        pygame.draw.rect(self.screen, (212, 175, 55), selection_rect, 2)
        
        big_font = pygame.font.SysFont("Arial", 70, bold=True)
        
        buttons_config = [
            (0, "w", self.piece_images["w_king"]),
            (1, "r", "?"),
            (2, "b", self.piece_images["b_king"])
        ]
        
        click_rects = []
        mouse_pos = pygame.mouse.get_pos()
        
        for i, key, content in buttons_config:
            rect = pygame.Rect(start_x + i * config.CELL_SIZE, start_y, config.CELL_SIZE, config.CELL_SIZE)
            click_rects.append((rect, key))
            
            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (60, 60, 60), rect)
                pygame.draw.rect(self.screen, (255, 215, 0), rect, 2)

            if isinstance(content, pygame.Surface):
                content_rect = content.get_rect(center=(rect.centerx, rect.centery - 5))
                self.screen.blit(content, content_rect)
            else:
                surf = big_font.render(content, True, (255, 215, 0))
                self.screen.blit(surf, surf.get_rect(center=(rect.centerx, rect.centery - 5)))
                

        return click_rects

    def draw_timers(self, game_state):
        def format_time(ms):
            seconds = ms // 1000
            minutes = seconds // 60
            seconds = seconds % 60
            return f"{minutes:02d}:{seconds:02d}"
        
        timer_font = pygame.font.SysFont("Consolas", 32, bold=True)
        
        timer_x = config.ORIGIN_X - 2 * config.CELL_SIZE
        timer_width = 110
        timer_height = 45

        row_3_center_y = config.ORIGIN_Y + (5 * config.CELL_SIZE) + (config.CELL_SIZE // 2)
        row_6_center_y = config.ORIGIN_Y + (2 * config.CELL_SIZE) + (config.CELL_SIZE // 2)

        black_str = format_time(game_state.black_time)
        black_surf = timer_font.render(black_str, True, (255, 255, 255))
        black_rect = black_surf.get_rect(center=(timer_x + timer_width // 2, row_6_center_y))
        
        bg_black = pygame.Rect(timer_x, black_rect.y - 5, timer_width, timer_height)
        pygame.draw.rect(self.screen, (30, 30, 30), bg_black, border_radius=5)
        pygame.draw.rect(self.screen, (200, 200, 200), bg_black, 2, border_radius=5)
        self.screen.blit(black_surf, black_rect)

        white_str = format_time(game_state.white_time)
        white_surf = timer_font.render(white_str, True, (0, 0, 0))
        white_rect = white_surf.get_rect(center=(timer_x + timer_width // 2, row_3_center_y))
        
        bg_white = pygame.Rect(timer_x, white_rect.y - 5, timer_width, timer_height)
        pygame.draw.rect(self.screen, (240, 240, 240), bg_white, border_radius=5)
        pygame.draw.rect(self.screen, (50, 50, 50), bg_white, 2, border_radius=5)
        self.screen.blit(white_surf, white_rect)

    def draw_move_log(self, game_state):
        log_rect = pygame.Rect(config.ORIGIN_X + config.BOARD_SIZE + 100, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, config.COLOR_PANEL, log_rect)

        font = pygame.font.SysFont("Helvetica", 18, bold=False)
        title_font = pygame.font.SysFont("Helvetica", 22, bold=True)

        title_surf = title_font.render("Move History", True, config.COLOR_TEXT)
        self.screen.blit(title_surf, (config.ORIGIN_X + config.BOARD_SIZE + 170, 20))

        move_log = game_state.move_log

        total_rows = (len(move_log) + 1) // 2
        max_visible_rows = (config.SCREEN_HEIGHT - config.LOG_PADDING_TOP - 20) // config.LOG_LINE_HEIGHT
        scroll_offset = 0
        if total_rows > max_visible_rows:
            scroll_offset = (total_rows - max_visible_rows) * config.LOG_LINE_HEIGHT

        log_entries_surf = pygame.Surface((config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT - config.LOG_PADDING_TOP), pygame.SRCALPHA)
        
        for i in range(0, len(move_log), 2):
            row_index = i // 2
            y_pos = row_index * config.LOG_LINE_HEIGHT - scroll_offset
            
            if -config.LOG_LINE_HEIGHT < y_pos < config.SCREEN_HEIGHT:
                move_num = row_index + 1
                
                num_text = font.render(f"{move_num}.", True, (120, 120, 120))
                log_entries_surf.blit(num_text, (config.LOG_PADDING_LEFT, y_pos))
                
                white_move = font.render(move_log[i].get_chess_notation(), True, (255, 255, 255))
                log_entries_surf.blit(white_move, (config.LOG_PADDING_LEFT + 40, y_pos))
                
                if i + 1 < len(move_log):
                    black_move = font.render(move_log[i+1].get_chess_notation(), True, (255, 255, 255))
                    log_entries_surf.blit(black_move, (config.LOG_PADDING_LEFT + 120, y_pos))

        self.screen.blit(log_entries_surf, (config.BOARD_SIZE + config.ORIGIN_X + 100, config.LOG_PADDING_TOP))

    def draw_material_advantage(self, game_state):
        font = pygame.font.SysFont("Helvetica", 18, bold=False)
        balance, white_adv, black_adv = game_state.get_material_info()
        icon_size = config.CELL_SIZE // 4
        padding = 5
        if black_adv or balance < 0:
            x_pos = config.ORIGIN_X
            y_pos = config.ORIGIN_Y - 30
            for b_piece in black_adv:
                self.screen.blit(self.material_piece_images["b_" + b_piece], (x_pos, y_pos))
                x_pos += icon_size - 5

            if balance < 0:
                text = "+" + str(abs(balance))
                black_material = font.render(text, True, (255, 255, 255))
                self.screen.blit(black_material, (x_pos + padding, y_pos))

        if white_adv or balance > 0:
            x_pos = config.ORIGIN_X
            y_pos = config.BOARD_SIZE + config.ORIGIN_Y + 30
            for w_piece in white_adv:
                self.screen.blit(self.material_piece_images["w_" + w_piece], (x_pos, y_pos))
                x_pos += icon_size - 5

            if balance > 0:
                text = "+" + str(balance)
                white_material = font.render(text, True, (255, 255, 255))
                self.screen.blit(white_material, (x_pos + padding, y_pos))

    def draw_game_over(self, result_text, sub_text):
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        panel_width, panel_height = 450, 280
        panel_x = (config.SCREEN_WIDTH - panel_width) // 2
        panel_y = (config.SCREEN_HEIGHT - panel_height) // 2

        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (30, 30, 30), panel_rect)
        pygame.draw.rect(self.screen, (200, 180, 100), panel_rect, 3) 

        font_big = pygame.font.SysFont("Garamond", 48, bold=True)
        res_surface = font_big.render(result_text, True, (255, 255, 255))
        res_rect = res_surface.get_rect(center=(config.SCREEN_WIDTH // 2, panel_y + 60))
        self.screen.blit(res_surface, res_rect)

        font_small = pygame.font.SysFont("Arial", 24)
        sub_surface = font_small.render(sub_text, True, (180, 180, 180))
        sub_rect = sub_surface.get_rect(center=(config.SCREEN_WIDTH // 2, panel_y + 110))
        self.screen.blit(sub_surface, sub_rect)

        button_w, button_h = 140, 45
        spacing = 20
        btn_y = panel_y + 180
        
        restart_button_rect = pygame.Rect(
            (config.SCREEN_WIDTH // 2) - button_w - (spacing // 2), 
            btn_y, 
            button_w, 
            button_h
        )
        
        quit_button_rect = pygame.Rect(
            (config.SCREEN_WIDTH // 2) + (spacing // 2), 
            btn_y, 
            button_w, 
            button_h
        )

        btn_font = pygame.font.SysFont("Arial", 20, bold=True)

        pygame.draw.rect(self.screen, (50, 70, 50), restart_button_rect)
        pygame.draw.rect(self.screen, (200, 180, 100), restart_button_rect, 2)
        restart_text = btn_font.render("RESTART", True, (255, 255, 255))
        self.screen.blit(restart_text, restart_text.get_rect(center=restart_button_rect.center))

        pygame.draw.rect(self.screen, (70, 40, 40), quit_button_rect)
        pygame.draw.rect(self.screen, (200, 180, 100), quit_button_rect, 2)
        quit_text = btn_font.render("QUIT", True, (255, 255, 255))
        self.screen.blit(quit_text, quit_text.get_rect(center=quit_button_rect.center))

        return restart_button_rect, quit_button_rect

    def draw_main_menu(self):
        self.screen.fill((20, 20, 20))

        title_font = pygame.font.SysFont("Garamond", 72, bold=True)
        title_surface = title_font.render("CHESS PROJECT", True, (200, 180, 100))
        title_rect = title_surface.get_rect(center=(config.SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_surface, title_rect)

        button_w, button_h = 250, 60
        center_x = (config.SCREEN_WIDTH - button_w) // 2
        
        start_btn_rect = pygame.Rect(center_x, 300, button_w, button_h)
        ai_btn_rect = pygame.Rect(center_x, 380, button_w, button_h)

        pygame.draw.rect(self.screen, (50, 80, 50), start_btn_rect)
        pygame.draw.rect(self.screen, (200, 180, 100), start_btn_rect, 2)
        
        btn_font = pygame.font.SysFont("Arial", 24, bold=True)
        start_text = btn_font.render("START GAME", True, (255, 255, 255))
        self.screen.blit(start_text, start_text.get_rect(center=start_btn_rect.center))

        pygame.draw.rect(self.screen, (35, 30, 20), ai_btn_rect)
        pygame.draw.rect(self.screen, (212, 175, 55), ai_btn_rect, 2)
        ai_text = btn_font.render("PLAY WITH AI", True, (235, 230, 200))
        self.screen.blit(ai_text, ai_text.get_rect(center=ai_btn_rect.center))
        return start_btn_rect, ai_btn_rect

    def render(self, game_state, selected_square, valid_moves, highlighting_set, arrows):
        self.draw_board()
        self.draw_coordinates()
        self._draw_selected_square(game_state, selected_square, valid_moves)
        self.draw_analyse_highlight(highlighting_set)
        self.draw_arrows(arrows)
        self.draw_pieces(game_state)
        self.draw_timers(game_state)
        self.draw_move_log(game_state)
        self.draw_material_advantage(game_state)
        if game_state.checkmate or game_state.stealmate or game_state.on_time or game_state.check_insufficient_material():
            res_txt = "GAME OVER"
            sub_txt = ""

            if game_state.checkmate:
                res_txt = "CHECKMATE"
                winner = "Black" if game_state.white_to_move else "White"
                sub_txt = f"{winner} wins by technical superiority"
            
            elif game_state.stealmate:
                res_txt = "STALEMATE"
                sub_txt = "Draw: No legal moves"
            
            elif game_state.on_time:
                res_txt = "TIME OUT"
                winner = "Black" if game_state.white_time <= 0 else "White"
                sub_txt = f"{winner} wins on time"
            
            elif game_state.check_insufficient_material():
                res_txt = "DRAW"
                sub_txt = "Insufficient material to mate"
            return self.draw_game_over(res_txt, sub_txt)