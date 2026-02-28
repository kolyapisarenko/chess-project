from src import config

class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class GameState:
    def __init__(self):
        self.board = [
            ["b_rook", "b_knight", "b_bishop", "b_queen", "b_king", "b_bishop", "b_knight", "b_rook"],
            ["b_pawn", "b_pawn", "b_pawn", "b_pawn", "b_pawn", "b_pawn", "b_pawn", "b_pawn"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["w_pawn", "w_pawn", "w_pawn", "w_pawn", "w_pawn", "w_pawn", "w_pawn", "w_pawn"],
            ["w_rook", "w_knight", "w_bishop", "w_queen", "w_king", "w_bishop", "w_knight", "w_rook"]
        ]
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.checkmate = False
        self.stealmate = False
        self.position_history = []
        self.enpassant_possible = ()
        self.current_castle_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(True, True, True, True)]

    def make_move(self, move):
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.board[move.start_row][move.start_col] = "--"
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = "--"
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = "--"
            else:
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                self.board[move.end_row][move.end_col - 2] = "--"
        if move.is_pawn_promotion:
            color = move.piece_moved[0]
            self.board[move.end_row][move.end_col] = color + "_" + move.promotion_piece
        self.update_castle_rights(move)
        self.castle_rights_log.append(CastleRights(self.current_castle_rights.wks, self.current_castle_rights.bks, self.current_castle_rights.wqs, self.current_castle_rights.bqs))
        if move.piece_moved == "w_king":
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "b_king":
            self.black_king_location = (move.end_row, move.end_col)
        self.position_history.append(self.get_position_hash())
        if "pawn" in move.piece_moved and abs(move.end_row - move.start_row) == 2:
            self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.enpassant_possible = ()

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.castle_rights_log.pop()
            new_rights = self.castle_rights_log[-1]
            self.current_castle_rights = CastleRights(new_rights.wks, new_rights.bks, new_rights.wqs, new_rights.bqs)
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = "--"
                else:
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = "--"
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = "--"
                self.board[move.start_row][move.end_col] = move.piece_captured
            self.enpassant_possible = move.enpassant_possible_log
            self.white_to_move = not self.white_to_move
            if move.piece_moved == "w_king":
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == "b_king":
                self.black_king_location = (move.start_row, move.start_col)
            if len(self.position_history) > 0:
                self.position_history.pop()

    def update_castle_rights(self, move):
        if move.piece_moved == "w_king":
            self.current_castle_rights.wks = False
            self.current_castle_rights.wqs = False
        elif move.piece_moved == "b_king":
            self.current_castle_rights.bks = False
            self.current_castle_rights.bqs = False
        elif move.piece_moved == "w_rook":
            if move.start_row == 7:
                if move.start_col == 0:
                    self.current_castle_rights.wqs = False
                elif move.start_col == 7:
                    self.current_castle_rights.wks = False
        elif move.piece_moved == "b_rook":
            if move.start_row == 0:
                if move.start_col == 0:
                    self.current_castle_rights.bqs = False
                elif move.start_col == 7:
                    self.current_castle_rights.bks = False
        elif move.piece_captured == 'w_rook':
            if move.end_row == 7:
                if move.end_col == 0: 
                    self.current_castle_rights.wqs = False
                elif move.end_col == 7: 
                    self.current_castle_rights.wks = False
        elif move.piece_captured == 'b_rook':
            if move.end_row == 0:
                if move.end_col == 0: 
                    self.current_castle_rights.bqs = False
                elif move.end_col == 7: 
                    self.current_castle_rights.bks = False

    def square_under_attack(self, r, c):
        enemy_color = "b" if self.white_to_move else "w"

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        knight_directions = ((2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2))

        for j, d in enumerate(directions):
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece != "--":
                        if i == 1:
                            if end_piece == enemy_color + "_king":
                                return True
                        
                        if 0 <= j <= 3:

                            if end_piece == enemy_color + "_queen" or end_piece == enemy_color + "_rook":
                                return True
                        elif 4 <= j <= 7:
                            if end_piece == enemy_color + "_queen" or end_piece == enemy_color + "_bishop":
                                return True
                        break
        
        for kd in knight_directions:
            end_row = r + kd[0]
            end_col = c + kd[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece == enemy_color + "_knight":
                    return True
                
        if enemy_color == 'w':
            pawn_directions = ((1, -1), (1, 1))
        else:
            pawn_directions = ((-1, -1), (-1, 1))

        for pd in pawn_directions:
            end_row = r + pd[0]
            end_col = c + pd[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if self.board[end_row][end_col] == enemy_color + "_pawn":
                    return True
                
    def in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    def check_insufficient_material(self):
        white_pieces = []
        black_pieces = []
        for r in range(config.ROWS):
            for c in range(config.COLS):
                if self.board[r][c] != "--":
                    if "pawn" in self.board[r][c] or "rook" in self.board[r][c] or "queen" in self.board[r][c]:
                        flag_danger = True
                        return False
                    else:
                        if (self.board[r][c][0] == "w"):
                            white_pieces.append((self.board[r][c], r, c))
                        else:
                            black_pieces.append((self.board[r][c], r, c))

        piece_count = len(white_pieces) + len(black_pieces)
        if piece_count <= 3:
            return True
        if piece_count == 4:
            w_bishop = [p for p in white_pieces if "bishop" in p[0]]
            b_bishop = [p for p in black_pieces if "bishop" in p[0]]

            if len(w_bishop) == 1 and len(b_bishop) == 1:
                white_bishop = (w_bishop[0][1] + w_bishop[0][2]) % 2
                black_bishop = (b_bishop[0][1] + b_bishop[0][2]) % 2

                if white_bishop == black_bishop:
                    return True
        return False

    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                piece = self.board[r][c]
                if piece != "--":
                    color = True if piece[0] == "w" else False
                    if color == self.white_to_move:
                        if "pawn" in piece:
                            self.get_pawn_moves(r, c, moves)
                        elif "knight" in piece:
                            self.get_knight_moves(r, c, moves)
                        elif "bishop" in piece:
                            self.get_bishop_moves(r, c, moves)
                        elif "rook" in piece:
                            self.get_rook_moves(r, c, moves)
                        elif "queen" in piece:
                            self.get_queen_moves(r, c, moves)
                        else:
                            self.get_king_moves(r, c, moves)
                else:
                    continue
        return moves

    def get_valid_moves(self):
        moves = self.get_all_possible_moves()
        
        enpassant_backup = self.enpassant_possible
        temp_castle_rights = CastleRights(self.current_castle_rights.wks, self.current_castle_rights.bks, self.current_castle_rights.wqs, self.current_castle_rights.bqs)
        
        for i in range(len(moves) - 1, -1, -1):
            self.make_move(moves[i])
            self.white_to_move = not self.white_to_move
            if self.in_check():
                moves.remove(moves[i])
            self.white_to_move = not self.white_to_move
            self.undo_move()

        if self.white_to_move:
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)

        self.enpassant_possible = enpassant_backup
        self.current_castle_rights = temp_castle_rights

        if len(moves) == 0:
            if self.in_check():
                self.checkmate = True
            else:
                self.stealmate = True
        else:
            if self.check_insufficient_material():
                self.stealmate = True
            current_position = self.get_position_hash()
            if self.position_history.count(current_position) >= 3:
                self.stealmate = True
            self.checkmate = False
        return moves

    def get_position_hash(self):
        board_tuple = tuple(tuple(row) for row in self.board)
        return (board_tuple, self.white_to_move)

    def get_pawn_moves(self, r, c, moves):
        if self.white_to_move:
            if self.board[r - 1][c] == "--":
                moves.append(Move((r, c), (r - 1, c), self.board, enpassant_possible=self.enpassant_possible))
                if (r == 6) and (self.board[r - 1][c] == "--") and (self.board[r - 2][c] == "--"):
                    moves.append(Move((r, c), (r - 2, c), self.board, enpassant_possible=self.enpassant_possible))

            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, enpassant_possible=self.enpassant_possible))
                elif (r - 1, c - 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, enpassant_possible=self.enpassant_possible))
            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, enpassant_possible=self.enpassant_possible))
                elif (r - 1, c + 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, enpassant_possible=self.enpassant_possible))
        else:
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board, enpassant_possible=self.enpassant_possible))
                if (r == 1) and (self.board[r + 1][c] == "--") and (self.board[r + 2][c] == "--"):
                    moves.append(Move((r, c), (r + 2, c), self.board, enpassant_possible=self.enpassant_possible))
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, enpassant_possible=self.enpassant_possible))
                elif (r + 1, c - 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, enpassant_possible=self.enpassant_possible))
            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, enpassant_possible=self.enpassant_possible))
                elif (r + 1, c + 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, enpassant_possible=self.enpassant_possible))

    def get_rook_moves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = "b" if self.white_to_move else "w"

        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((r, c), (end_row, end_col), self.board, enpassant_possible=self.enpassant_possible))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board, enpassant_possible=self.enpassant_possible))
                        break
                    else:
                        break
                else:
                    break
    
    def get_knight_moves(self, r, c, moves):
        directions = ((2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2))
        enemy_color = "b" if self.white_to_move else "w"

        for d in directions:
            end_row = r + d[0]
            end_col = c + d[1]

            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if (end_piece == "--") or (end_piece[0] == enemy_color):
                    moves.append(Move((r, c), (end_row, end_col), self.board, enpassant_possible=self.enpassant_possible))

    def get_bishop_moves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = "b" if self.white_to_move else "w"

        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((r, c), (end_row, end_col), self.board, enpassant_possible=self.enpassant_possible))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board, enpassant_possible=self.enpassant_possible))
                        break
                    else:
                        break
                else:
                    break

    def get_queen_moves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = "b" if self.white_to_move else "w"

        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((r, c), (end_row, end_col), self.board, enpassant_possible=self.enpassant_possible))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board, enpassant_possible=self.enpassant_possible))
                        break
                    else:
                        break
                else:
                    break
    
    def get_castle_moves(self, r, c, moves):
        if self.square_under_attack(r, c):
            return
        if (self.white_to_move and self.current_castle_rights.wks) or (not self.white_to_move and self.current_castle_rights.bks):
            self.get_kingside_castle_moves(r, c, moves)
        if (self.white_to_move and self.current_castle_rights.wqs) or (not self.white_to_move and self.current_castle_rights.bqs):
            self.get_queenside_castle_moves(r, c, moves)

    def get_kingside_castle_moves(self, r, c, moves):
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
            if not self.square_under_attack(r, c + 1) and not self.square_under_attack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, is_castle_move=True))

    def get_queenside_castle_moves(self, r, c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c - 3] == "--":
            if not self.square_under_attack(r, c - 1) and not self.square_under_attack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, is_castle_move=True))

    def get_king_moves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = "b" if self.white_to_move else "w"

        for d in directions:
            end_row = r + d[0]
            end_col = c + d[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece == "--":
                    moves.append(Move((r, c), (end_row, end_col), self.board, enpassant_possible=self.enpassant_possible))
                elif end_piece[0] == enemy_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board, enpassant_possible=self.enpassant_possible))

class Move:
    ranks_to_rows = {"1" : 7, "2" : 6, "3" : 5, "4" : 4, "5" : 3, "6": 2, "7" : 1, "8" : 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a" : 0, "b" : 1, "c" : 2, "d" : 3, "e" : 4, "f" : 5, "g" : 6, "h" : 7}
    cols_to_files = {v : k for k, v in files_to_cols.items()}
    def __init__(self, start_sq, end_sq, board, enpassant_possible = (), is_castle_move = False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]

        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.is_pawn_promotion = ((self.piece_moved == "w_pawn" and self.end_row == 0) or (self.piece_moved == "b_pawn" and self.end_row == 7))
        self.promotion_piece = "queen"
        self.enpassant_possible_log = enpassant_possible
        self.is_enpassant_move = ("pawn" in self.piece_moved and (self.end_row, self.end_col) == self.enpassant_possible_log and self.start_col != self.end_col)
        if self.is_enpassant_move:
            self.piece_captured = "w_pawn" if self.piece_moved == "b_pawn" else "b_pawn"
        self.is_castle_move = is_castle_move or (self.piece_moved[2:] == "king" and abs(self.start_col - self.end_col) == 2)
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)
    
    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
    
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False