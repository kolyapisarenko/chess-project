from src.bitboards.logic import board, bitboard_utils, move_gen
from src.bitboards.logic.adapter import to_matrix
from collections import Counter

class BitboardEngine:
    def __init__(self):
        #Board setup
        self.new_board = board.Board()
        self.attack_tables = move_gen.AttackTables()

        #Castling consts
        self.WK = 1
        self.WQ = 2
        self.BK = 4
        self.BQ = 8

        #Turn to move
        self.white_to_move = True

        #Spesial states
        self.castling_rights = 0b1111
        self.prev_castling_rights = 0b1111
        self.en_passant_sq = -1
        self.prev_en_passant_sq = -1
        self.move_log = []
        self.in_check_flag = False
        self.position_history = []

        #Game state
        self.board = to_matrix(self.new_board)
        self.white_time = 600000
        self.black_time = 600000
        self.on_time = False
        self.stealmate = False
        self.checkmate = False

    #Function to get the material info of the current board state
    def get_material_info(self):
        self.piece_value = {"pawn": 1, "knight": 3, "bishop": 3, "rook": 5, "queen": 9, "king": 0}
        white_pieces = []
        black_pieces = []
        balance = 0

        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece != "--" and piece != "":
                    color = piece[0]
                    piece_type = piece[2:]
                    if piece_type not in self.piece_value:
                        continue
                    value = self.piece_value[piece_type]
                    if color == "w":
                        if piece_type != "king":
                            white_pieces.append(piece_type)
                            balance += value
                    elif color == "b":
                        if piece_type != "king":
                            black_pieces.append(piece_type)
                            balance -= value

        w_counter = Counter(white_pieces)
        b_counter = Counter(black_pieces)
        white_advantage = list((w_counter - b_counter).elements())
        black_advantage = list((b_counter - w_counter).elements())

        white_advantage.sort(key=lambda x: self.piece_value[x])
        black_advantage.sort(key=lambda x: self.piece_value[x])

        return balance, white_advantage, black_advantage

    #Function that fits old name in main.py to new function name
    def get_valid_moves(self):
        return self.generate_legal_moves()

    #Function to check if the current player is in check
    def in_check(self):
        self.generate_pin_and_check_mask()
        return self.in_check_flag

    #Function to check if the game could be drawn due to insufficient material
    def check_insufficient_material(self):
        b = self.new_board

        if b.white_pawns or b.black_pawns or b.white_rooks or b.black_rooks or b.white_queen or b.black_queen:
            return False
        w_knight_count = bin(b.white_knights).count("1")
        b_knight_count = bin(b.black_knights).count("1")
        w_bishop_count = bin(b.white_bishops).count("1")
        b_bishop_count = bin(b.black_bishops).count("1")
        total_minor_pieces = w_knight_count + b_knight_count + w_bishop_count + b_bishop_count
        if total_minor_pieces == 0:
            return True
        if total_minor_pieces == 1:
            return True
        return False

    #Function to update the game status based on the current board state
    def _update_game_status(self):
        moves = self.generate_legal_moves()
        if len(moves) == 0:
            if self.in_check_flag:
                self.checkmate = True
                self.move_log[-1].is_mate = True
            else:
                self.stealmate = True
        else:
            self.checkmate = False
            self.stealmate = False
            if self.position_history.count(self.get_position_hash()) >= 3 or self.check_insufficient_material():
                self.stealmate = True
        if not self.checkmate and self.in_check() and len(moves) > 0:
            self.move_log[-1].is_check = True

    #Vizualize board method
    def draw_board(self):
        return self.new_board.display_board()

    def get_position_hash(self):
        nb = self.new_board
        return (nb.white_pawns, nb.white_rooks, nb.white_knights, nb.white_bishops, nb.white_queen, nb.white_king, nb.black_pawns, nb.black_rooks, nb.black_knights, nb.black_bishops, nb.black_queen, nb.black_king, self.white_to_move)

    #Method to make a move on the board
    def make_move(self, move):
        #Getting start and target square
        s_quare = move.start_sq
        t_arget = move.target_sq

        #Changing castling rights and en passant square
        move.prev_en_passant_sq = self.en_passant_sq
        move.prev_castling_rights = self.castling_rights
        self.en_passant_sq = -1

        #Updating bitboards for moved piece and captured piece
        move_mask = (1 << s_quare) | (1 << t_arget)
        moved_attr = self.new_board.piece_map[move.piece_moved]
        setattr(self.new_board, moved_attr, getattr(self.new_board, moved_attr) ^ move_mask)

        #Finding out type of move and updating the board accordingly
        #If the move is a capture, we need to remove the captured piece from the board
        if move.piece_captured:
            #Special case for en passant capture, we need to remove the captured pawn from the board
            if move.is_enpassant:
                ep_capture_sq = t_arget - 8 if self.white_to_move else t_arget + 8
                capture_mask = 1 << ep_capture_sq
            #Default case for normal capture, we need to remove the captured piece from the board
            else:
                capture_mask = 1 << t_arget
            capture_attr = self.new_board.piece_map[move.piece_captured]
            setattr(self.new_board, capture_attr, getattr(self.new_board, capture_attr) ^ capture_mask)

        #If the move is a promotion, we need to remove the pawn from the board and add the promoted piece to the board
        if move.is_promotion:
            setattr(self.new_board, moved_attr, getattr(self.new_board, moved_attr) ^ (1 << t_arget))
            p_piece = move.promotion_piece if self.white_to_move else move.promotion_piece.lower()
            promoted_attr = self.new_board.piece_map[p_piece]
            setattr(self.new_board, promoted_attr, getattr(self.new_board, promoted_attr) ^ (1 << t_arget))

        #If the move is a castling, we need to move the rook to the correct square
        if move.is_castling:
            if t_arget == 6:
                rook_mask = (1 << 7) | (1 << 5)
                self.new_board.white_rooks ^= rook_mask
            elif t_arget == 2:
                rook_mask = (1 << 0) | (1 << 3)
                self.new_board.white_rooks ^= rook_mask
            elif t_arget == 62:
                rook_mask = (1 << 63) | (1 << 61)
                self.new_board.black_rooks ^= rook_mask
            elif t_arget == 58:
                rook_mask = (1 << 56) | (1 << 59)
                self.new_board.black_rooks ^= rook_mask

        #Updating castling rights based on the moved piece and the squares involved in the move
        if move.piece_moved == "K":
            self.castling_rights &= ~(self.WK | self.WQ)
        elif move.piece_moved == "k":
            self.castling_rights &= ~(self.BK | self.BQ)
        
        #Updating castling rights based on the squares involved in the move
        if s_quare == 7 or t_arget == 7: self.castling_rights &= ~self.WK
        if s_quare == 0 or t_arget == 0: self.castling_rights &= ~self.WQ
        if s_quare == 63 or t_arget == 63: self.castling_rights &= ~self.BK
        if s_quare == 56 or t_arget == 56: self.castling_rights &= ~self.BQ

        #Updating en passant square if the move is a double pawn push
        if move.piece_moved.lower() == "p" and abs(s_quare - t_arget) == 16:
            self.en_passant_sq = (s_quare + t_arget) // 2

        #Changing turn and logging move
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        self.position_history.append(self.get_position_hash())
        self.new_board._update_occupancy()

        self.board = to_matrix(self.new_board)
        self._update_game_status()

    def undo_move(self):
        if self.move_log:
            #Getting last move
            move = self.move_log.pop()

            #Getting start and target square
            s_square = move.start_sq
            t_arget = move.target_sq

            #Reverting the moved piece back to its original square
            self.en_passant_sq = move.prev_en_passant_sq
            self.castling_rights = move.prev_castling_rights
            self.white_to_move = not self.white_to_move

            #Reverting the moved piece back to its original square
            if move.is_promotion:
                p_piece = move.promotion_piece if self.white_to_move else move.promotion_piece.lower()
                promoted_attr = self.new_board.piece_map[p_piece]
                setattr(self.new_board, promoted_attr, getattr(self.new_board, promoted_attr) ^ (1 << t_arget))
                moved_attr = self.new_board.piece_map[move.piece_moved]
                setattr(self.new_board, moved_attr, getattr(self.new_board, moved_attr) ^ (1 << t_arget))

            #Reverting the captured piece back to its original square
            if move.is_castling:
                if t_arget == 6:
                    rook_mask = (1 << 7) | (1 << 5)
                    self.new_board.white_rooks ^= rook_mask
                elif t_arget == 2:
                    rook_mask = (1 << 0) | (1 << 3)
                    self.new_board.white_rooks ^= rook_mask
                elif t_arget == 62:
                    rook_mask = (1 << 63) | (1 << 61)
                    self.new_board.black_rooks ^= rook_mask
                elif t_arget == 58:
                    rook_mask = (1 << 56) | (1 << 59)
                    self.new_board.black_rooks ^= rook_mask

            #Updating bitboards for moved piece and captured piece via XOR with same mask
            move_mask = (1 << s_square) | (1 << t_arget)
            moved_attr = self.new_board.piece_map[move.piece_moved]
            setattr(self.new_board, moved_attr, getattr(self.new_board, moved_attr) ^ move_mask)
            if move.piece_captured:
                if move.is_enpassant:
                    ep_capture_sq = t_arget - 8 if self.white_to_move else t_arget + 8
                    capture_mask = 1 << ep_capture_sq
                else:
                    capture_mask = 1 << t_arget
                capture_attr = self.new_board.piece_map[move.piece_captured]
                setattr(self.new_board, capture_attr, getattr(self.new_board, capture_attr) ^ capture_mask)
            
            self.new_board._update_occupancy()
            self.board = to_matrix(self.new_board)
            if len(self.position_history) > 0:
                self.position_history.pop()
            self._update_game_status()

    #Function to get the square of the king for the current player
    def get_king_square(self, white_to_move):
        if white_to_move:
            king_bitboard = self.new_board.white_king
        else:
            king_bitboard = self.new_board.black_king
        return king_bitboard.bit_length() - 1 if king_bitboard else -1

    #Function to generate pin and check masks for the current player
    def generate_pin_and_check_mask(self):
        #Getting the square of the king for the current player
        king_square = self.get_king_square(self.white_to_move)
        if king_square == -1:
            return 0, [0xFFFFFFFFFFFFFFFF] * 64

        #Initializing masks and checkers
        check_mask = 0xFFFFFFFFFFFFFFFF
        pin_mask = [0xFFFFFFFFFFFFFFFF] * 64
        in_check = False
        check_ers = 0

        #Getting enemy pieces based on the current player
        if self.white_to_move:
            enemy_knight = self.new_board.black_knights
            enemy_rooks = self.new_board.black_rooks
            enemy_bishops = self.new_board.black_bishops
            enemy_pawns = self.new_board.black_pawns
            enemy_queen = self.new_board.black_queen
        else:
            enemy_knight = self.new_board.white_knights
            enemy_rooks = self.new_board.white_rooks
            enemy_bishops = self.new_board.white_bishops
            enemy_pawns = self.new_board.white_pawns
            enemy_queen = self.new_board.white_queen

        #Calculating checkers and pins
        check_ers |= self.attack_tables.KNIGHT_ATTACKS[king_square] & enemy_knight
        all_occ = self.new_board.all_pieces
        check_ers |= self.attack_tables.get_rook_attacks(king_square, all_occ) & (enemy_rooks | enemy_queen)
        check_ers |= self.attack_tables.get_bishop_attacks(king_square, all_occ) & (enemy_bishops | enemy_queen)
        
        #Calculating pawn attacks based on the current player
        pawn_attacks = 0
        king_bit = 1 << king_square
        if self.white_to_move:
            if king_bit & bitboard_utils.BitboardConstants.NOT_H_FILE:
                pawn_attacks |= 1 << (king_square + 9) & move_gen.AttackTables.mask
            if king_bit & bitboard_utils.BitboardConstants.NOT_A_FILE:
                pawn_attacks |= 1 << (king_square + 7) & move_gen.AttackTables.mask
        else:
            if king_bit & bitboard_utils.BitboardConstants.NOT_A_FILE:
                pawn_attacks |= 1 << (king_square - 9) & move_gen.AttackTables.mask
            if king_bit & bitboard_utils.BitboardConstants.NOT_H_FILE:
                pawn_attacks |= 1 << (king_square - 7) & move_gen.AttackTables.mask
        check_ers |= pawn_attacks & enemy_pawns

        #Counting the number of checkers and updating the in_check status and check_mask accordingly
        count = bin(check_ers).count("1")
        if count == 0:
            self.in_check_flag = False
        elif count == 1:
            self.in_check_flag = True
            checker_square = check_ers.bit_length() - 1
            checker_bit = 1 << checker_square
            if checker_bit & (enemy_knight | enemy_pawns):
                check_mask = checker_bit
            else:
                is_rook_type = ((checker_bit & enemy_rooks) or (checker_bit & enemy_queen)) and ((king_square // 8 == checker_square // 8) or (king_square % 8 == checker_square % 8))
                if is_rook_type:
                    ray_from_king = self.attack_tables.get_rook_attacks(king_square, all_occ)
                    ray_from_checker = self.attack_tables.get_rook_attacks(checker_square, all_occ)
                else:
                    ray_from_king = self.attack_tables.get_bishop_attacks(king_square, all_occ)
                    ray_from_checker = self.attack_tables.get_bishop_attacks(checker_square, all_occ)
                check_mask = ray_from_king & ray_from_checker | checker_bit
        else:
            self.in_check_flag = True
            check_mask = 0

        if self.in_check_flag:
            bitboard_utils.BitboardConstants.print_bitboard(check_mask)
        
        #Getting our pieces based on the current player
        if self.white_to_move:
            our_pieces = self.new_board.white_pieces
        else:
            our_pieces = self.new_board.black_pieces
        enemy_pieces = (enemy_knight | enemy_rooks | enemy_bishops | enemy_pawns | enemy_queen)

        #Calculating pins for rooks
        rook_xray = self.attack_tables.get_rook_attacks(king_square, enemy_pieces)
        pinners_flat = rook_xray & (enemy_rooks | enemy_queen)
        while pinners_flat:
            pinner_sq = (pinners_flat & -pinners_flat).bit_length() - 1
            line = (self.attack_tables.get_rook_attacks(king_square, all_occ) & self.attack_tables.get_rook_attacks(pinner_sq, all_occ)) | (1 << pinner_sq)
            our_pieces_on_line = line & our_pieces
            if bin(our_pieces_on_line).count("1") == 1:
                pinned_sq = our_pieces_on_line.bit_length() - 1
                pin_mask[pinned_sq] = line
            pinners_flat ^= 1 << pinner_sq

        #Calculating pins for bishops
        bishop_xray = self.attack_tables.get_bishop_attacks(king_square, enemy_pieces)
        pinners_flat = bishop_xray & (enemy_bishops | enemy_queen)
        while pinners_flat:
            pinner_sq = (pinners_flat & -pinners_flat).bit_length() - 1
            line = (self.attack_tables.get_bishop_attacks(king_square, all_occ) & self.attack_tables.get_bishop_attacks(pinner_sq, all_occ)) | (1 << pinner_sq)
            our_pieces_on_line = line & our_pieces
            if bin(our_pieces_on_line).count("1") == 1:
                pinned_sq = our_pieces_on_line.bit_length() - 1
                pin_mask[pinned_sq] = line
            pinners_flat ^= 1 << pinner_sq

        return check_mask, pin_mask

    #Function to get the captured piece based on the target square and the current player
    def get_captured_piece(self, target_bit):
        b = self.new_board
        if self.white_to_move:
            if target_bit & b.black_pawns:
                return "p"
            elif target_bit & b.black_rooks:
                return "r"
            elif target_bit & b.black_knights:
                return "n"
            elif target_bit & b.black_bishops:
                return "b"
            elif target_bit & b.black_queen:
                return "q"
        else:
            if target_bit & b.white_pawns:
                return "P"
            elif target_bit & b.white_rooks:
                return "R"
            elif target_bit & b.white_knights:
                return "N"
            elif target_bit & b.white_bishops:
                return "B"
            elif target_bit & b.white_queen:
                return "Q"
        return None

    #Function to generate all legal moves for the current player, considering checks and pins
    def generate_legal_moves(self):
        moves = []
        check_mask, pin_mask = self.generate_pin_and_check_mask()

        #Considering the pieces of the current player and the enemy pieces based on whose turn it is
        if self.white_to_move:
            our_pieces = self.new_board.white_pieces
            our_knights = self.new_board.white_knights
            our_rooks = self.new_board.white_rooks
            our_bishops = self.new_board.white_bishops
            our_queen = self.new_board.white_queen
            our_pawns = self.new_board.white_pawns
            enemy_knights = self.new_board.black_knights
            enemy_rooks = self.new_board.black_rooks
            enemy_bishops = self.new_board.black_bishops
            enemy_queen = self.new_board.black_queen
            enemy_pawns = self.new_board.black_pawns
            enemy_king = self.new_board.black_king
            enemy_pieces = self.new_board.black_pieces
        else:
            our_pieces = self.new_board.black_pieces
            our_knights = self.new_board.black_knights
            our_rooks = self.new_board.black_rooks
            our_bishops = self.new_board.black_bishops
            our_queen = self.new_board.black_queen
            our_pawns = self.new_board.black_pawns
            enemy_knights = self.new_board.white_knights
            enemy_rooks = self.new_board.white_rooks
            enemy_bishops = self.new_board.white_bishops
            enemy_queen = self.new_board.white_queen
            enemy_pawns = self.new_board.white_pawns
            enemy_king = self.new_board.white_king
            enemy_pieces = self.new_board.white_pieces

        out_king_sq = self.get_king_square(self.white_to_move)
        our_king_bit = 1 << out_king_sq if out_king_sq != -1 else 0
        all_occ = self.new_board.all_pieces
        all_occ_minus_king = self.new_board.all_pieces & ~our_king_bit
        enemy_attacks = 0
        
        #Calculating enemy attacks based on the enemy pieces and their attack patterns
        temp_knights = enemy_knights
        temp_rooks = enemy_rooks
        temp_bishops = enemy_bishops
        temp_queen = enemy_queen
        temp_king = enemy_king

        #Calculating enemy attacks for knights, rooks, bishops, and queens
        while temp_knights:
            sq = (temp_knights & -temp_knights).bit_length() - 1
            enemy_attacks |= self.attack_tables.KNIGHT_ATTACKS[sq]
            temp_knights &= temp_knights - 1
        while temp_rooks:
            sq = (temp_rooks & -temp_rooks).bit_length() - 1
            enemy_attacks |= self.attack_tables.get_rook_attacks(sq, all_occ_minus_king)
            temp_rooks &= temp_rooks - 1
        while temp_bishops:
            sq = (temp_bishops & -temp_bishops).bit_length() - 1
            enemy_attacks |= self.attack_tables.get_bishop_attacks(sq, all_occ_minus_king)
            temp_bishops &= temp_bishops - 1
        while temp_queen:
            sq = (temp_queen & -temp_queen).bit_length() - 1
            enemy_attacks |= self.attack_tables.get_queen_attacks(sq, all_occ_minus_king)
            temp_queen &= temp_queen - 1
        while temp_king:
            sq = (temp_king & -temp_king).bit_length() - 1
            enemy_attacks |= self.attack_tables.KING_ATTACKS[sq]
            temp_king &= temp_king - 1

        #Calculating enemy pawn attacks based on the current player's turn
        if self.white_to_move:
            enemy_attacks |= (enemy_pawns & bitboard_utils.BitboardConstants.NOT_A_FILE) >> 9
            enemy_attacks |= (enemy_pawns & bitboard_utils.BitboardConstants.NOT_H_FILE) >> 7
        else:
            enemy_attacks |= (enemy_pawns & bitboard_utils.BitboardConstants.NOT_H_FILE) << 9
            enemy_attacks |= (enemy_pawns & bitboard_utils.BitboardConstants.NOT_A_FILE) << 7

        #Setting piece characters based on the current player's turn
        p_char = "P" if self.white_to_move else "p"
        q_char = "Q" if self.white_to_move else "q"
        r_char = "R" if self.white_to_move else "r"
        b_char = "B" if self.white_to_move else "b"
        n_char = "N" if self.white_to_move else "n"
        k_char = "K" if self.white_to_move else "k"

        #All pieces are considered for generating legal moves, but only if the king is not in check or if there is a single checker. If there are multiple checkers, only king moves are generated.
        if check_mask != 0 or not self.in_check_flag:
            #Generating legal moves for knights
            temp_our_knights = our_knights
            while temp_our_knights:
                sq = (temp_our_knights & -temp_our_knights).bit_length() - 1
                legal_attacks = self.attack_tables.KNIGHT_ATTACKS[sq] & check_mask & pin_mask[sq] & ~our_pieces
                while legal_attacks:
                    target_sq = (legal_attacks & -legal_attacks).bit_length() - 1
                    target_bit = 1 << target_sq
                    capture = self.get_captured_piece(target_bit)
                    moves.append(Move(sq, target_sq, piece_moved=n_char, piece_captured=capture))
                    legal_attacks &= legal_attacks - 1
                temp_our_knights &= temp_our_knights - 1

            #Generating legal moves for rooks
            temp_our_rooks = our_rooks
            while temp_our_rooks:
                sq = (temp_our_rooks & -temp_our_rooks).bit_length() - 1
                legal_attacks = self.attack_tables.get_rook_attacks(sq, all_occ) & check_mask & pin_mask[sq] & ~our_pieces
                while legal_attacks:
                    target_sq = (legal_attacks & -legal_attacks).bit_length() - 1
                    target_bit = 1 << target_sq
                    capture = self.get_captured_piece(target_bit)
                    moves.append(Move(sq, target_sq, piece_moved=r_char, piece_captured=capture))
                    legal_attacks &= legal_attacks - 1
                temp_our_rooks &= temp_our_rooks - 1

            #Generating legal moves for bishops
            temp_our_bishops = our_bishops
            while temp_our_bishops:
                sq = (temp_our_bishops & -temp_our_bishops).bit_length() - 1
                legal_attacks = self.attack_tables.get_bishop_attacks(sq, all_occ) & check_mask & pin_mask[sq] & ~our_pieces
                while legal_attacks:
                    target_sq = (legal_attacks & -legal_attacks).bit_length() - 1
                    target_bit = 1 << target_sq
                    capture = self.get_captured_piece(target_bit)
                    moves.append(Move(sq, target_sq, piece_moved=b_char, piece_captured=capture))
                    legal_attacks &= legal_attacks - 1
                temp_our_bishops &= temp_our_bishops - 1

            #Generating legal moves for queens
            temp_our_queen = our_queen
            while temp_our_queen:
                sq = (temp_our_queen & -temp_our_queen).bit_length() - 1
                legal_attacks = self.attack_tables.get_queen_attacks(sq, all_occ) & check_mask & pin_mask[sq] & ~our_pieces
                while legal_attacks:
                    target_sq = (legal_attacks & -legal_attacks).bit_length() - 1
                    target_bit = 1 << target_sq
                    capture = self.get_captured_piece(target_bit)
                    moves.append(Move(sq, target_sq, piece_moved=q_char, piece_captured=capture))
                    legal_attacks &= legal_attacks - 1
                temp_our_queen &= temp_our_queen - 1

            #Generating legal moves for pawns, including promotions and captures
            temp_our_pawns = our_pawns
            while temp_our_pawns:
                sq = (temp_our_pawns & -temp_our_pawns).bit_length() - 1
                pawn_bit = 1 << sq

                if self.white_to_move:
                    forward_one = sq + 8
                    forward_two = sq + 16
                    start_rank_mask = 0x000000000000FF00
                    promotion_rank_mask = 0xFF00000000000000
                    cap_left_sq = sq + 7 if (pawn_bit & bitboard_utils.BitboardConstants.NOT_A_FILE) else -1
                    cap_right_sq = sq + 9 if (pawn_bit & bitboard_utils.BitboardConstants.NOT_H_FILE) else -1
                else:
                    forward_one = sq - 8
                    forward_two = sq - 16
                    start_rank_mask = 0x00FF000000000000
                    promotion_rank_mask = 0x00000000000000FF
                    cap_left_sq = sq - 9 if (pawn_bit & bitboard_utils.BitboardConstants.NOT_A_FILE) else -1
                    cap_right_sq = sq - 7 if (pawn_bit & bitboard_utils.BitboardConstants.NOT_H_FILE) else -1

                if not (all_occ & (1 << forward_one)):
                    if (1 << forward_one) & check_mask & pin_mask[sq]:
                        if (1 << forward_one) & promotion_rank_mask:
                            for piece in ["Q", "R", "B", "N"]:
                                moves.append(Move(sq, forward_one, piece_moved=p_char, piece_captured=None, is_promotion=True, promotion_piece=piece))
                        else:
                            moves.append(Move(sq, forward_one, piece_moved=p_char, piece_captured=None))
                    if (pawn_bit & start_rank_mask) and not (all_occ & (1 << forward_two)):
                        if (1 << forward_two) & check_mask & pin_mask[sq]:
                            moves.append(Move(sq, forward_two, piece_moved=p_char, piece_captured=None))
                for target_sq in [cap_left_sq, cap_right_sq]:
                    if target_sq != -1:
                        target_bit = 1 << target_sq
                        if (target_bit & enemy_pieces) and (target_bit & check_mask & pin_mask[sq]):
                            capture = self.get_captured_piece(target_bit)
                            if target_bit & promotion_rank_mask:
                                for piece in ["Q", "R", "B", "N"]:
                                    if not self.white_to_move:
                                        piece = piece.lower()
                                    moves.append(Move(sq, target_sq, piece_moved=p_char, piece_captured=capture, is_promotion=True, promotion_piece=piece))
                            else:
                                moves.append(Move(sq, target_sq, piece_moved=p_char, piece_captured=capture))
                        elif target_sq == self.en_passant_sq:
                            moves.append(Move(sq, target_sq, piece_moved=p_char, piece_captured="p" if self.white_to_move else "P", is_enpassant=True))

                temp_our_pawns &= temp_our_pawns - 1

        #Generating legal moves for the king, including castling
        king_square = self.get_king_square(self.white_to_move)
        if king_square != -1:
            king_legal_attacks = self.attack_tables.KING_ATTACKS[king_square] & ~our_pieces & ~enemy_attacks
            while king_legal_attacks:
                target_sq = (king_legal_attacks & -king_legal_attacks).bit_length() - 1
                target_bit = 1 << target_sq
                capture = self.get_captured_piece(target_bit)
                moves.append(Move(king_square, target_sq, piece_moved=k_char, piece_captured=capture))
                king_legal_attacks &= king_legal_attacks - 1
            if not self.in_check_flag:
                if self.white_to_move:
                    if (self.castling_rights & self.WK) and not (all_occ & ((1 << 5) | (1 << 6))):
                        if not (enemy_attacks & ((1 << 5) | (1 << 6))):
                            moves.append(Move(4, 6, piece_moved=k_char, is_castling=True))
                    if (self.castling_rights & self.WQ) and not (all_occ & ((1 << 1) | (1 << 2) | (1 << 3))):
                        if not (enemy_attacks & ((1 << 2) | (1 << 3))):
                            moves.append(Move(4, 2, piece_moved=k_char, is_castling=True))
                else:
                    if (self.castling_rights & self.BK) and not (all_occ & ((1 << 61) | (1 << 62))):
                        if not (enemy_attacks & ((1 << 61) | (1 << 62))):
                            moves.append(Move(60, 62, piece_moved=k_char, is_castling=True))
                    if (self.castling_rights & self.BQ) and not (all_occ & ((1 << 57) | (1 << 58) | (1 << 59))):
                        if not (enemy_attacks & ((1 << 58) | (1 << 59))):
                            moves.append(Move(60, 58, piece_moved=k_char, is_castling=True))

        return moves
                

class Move:
    #Dictionaries for notation of square
    ranks_to_rows = {"1" : 0, "2" : 1, "3" : 2, "4" : 3, "5" : 4, "6": 5, "7" : 6, "8" : 7}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a" : 0, "b" : 1, "c" : 2, "d" : 3, "e" : 4, "f" : 5, "g" : 6, "h" : 7}
    cols_to_files = {v : k for k, v in files_to_cols.items()}
    
    def __init__(self, start_sq, target_sq, piece_moved, piece_captured=None, is_enpassant=False, is_castling=False, is_promotion=False, promotion_piece=None):
        self.start_sq = start_sq
        self.target_sq = target_sq
        self.piece_moved = piece_moved
        self.piece_captured = piece_captured
        self.move_id = start_sq * 100 + target_sq
        self.is_enpassant = is_enpassant
        self.is_castling = is_castling
        self.is_promotion = is_promotion
        self.promotion_piece = promotion_piece
        self.is_check = False
        self.is_mate = False

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False
    
    def __str__(self):
        return self.cols_to_files[self.start_sq % 8] + self.rows_to_ranks[self.start_sq // 8] + self.cols_to_files[self.target_sq % 8] + self.rows_to_ranks[self.target_sq // 8]

    def get_chess_notation(self):
        if hasattr(self, 'is_castling') and self.is_castling:
            return "O-O" if self.target_sq % 8 == 6 else "O-O-O"
        else:    
            names = {"p": "", "q": "Q", "r" : "R", "b": "B", "n" : "N", "k" : "K"}
            piece = self.piece_moved.lower()
            prefix = names.get(piece, "")

            if piece == "p" and self.piece_captured != None:
                prefix = self.cols_to_files[self.start_sq % 8] + "x"
            elif self.piece_captured != None:
                prefix += "x"

            notation = prefix + self.get_rank_file(self.target_sq // 8, self.target_sq % 8)

        if self.is_mate:
            notation += "#"
        elif self.is_check:
            notation += "+"

        return notation

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]

if __name__ == "__main__":
    engine = BitboardEngine()
    engine.draw_board()