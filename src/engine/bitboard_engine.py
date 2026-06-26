from src.logic import board, bitboard_utils, move_gen

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
        self.en_passant_sq = -1
        self.move_log = []

    #Vizualize board method
    def draw_board(self):
        return self.new_board.display_board()

    def make_move(self, move):
        #Getting start and target square
        s_quare = move.start_sq
        t_arget = move.target_sq

        #Updating bitboards for moved piece and captured piece
        move_mask = (1 << s_quare) | (1 << t_arget)
        moved_attr = self.new_board.piece_map[move.piece_moved]
        setattr(self.new_board, moved_attr, getattr(self.new_board, moved_attr) ^ move_mask)
        if move.piece_captured:
            capture_mask = 1 << t_arget
            capture_attr = self.new_board.piece_map[move.piece_captured]
            setattr(self.new_board, capture_attr, getattr(self.new_board, capture_attr) ^ capture_mask)

        #Changing turn and logging move
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        self.new_board._update_occupancy()

    def undo_move(self):
        if self.move_log:
            #Getting last move
            move = self.move_log.pop()

            #Getting start and target square
            s_square = move.start_sq
            t_arget = move.target_sq

            #Updating bitboards for moved piece and captured piece via XOR with same mask
            move_mask = (1 << s_square) | (1 << t_arget)
            moved_attr = self.new_board.piece_map[move.piece_moved]
            setattr(self.new_board, moved_attr, getattr(self.new_board, moved_attr) ^ move_mask)
            if move.piece_captured:
                capture_mask = 1 << t_arget
                capture_attr = self.new_board.piece_map[move.piece_captured]
                setattr(self.new_board, capture_attr, getattr(self.new_board, capture_attr) ^ capture_mask)
            self.white_to_move = not self.white_to_move
            self.new_board._update_occupancy()


class Move:
    #Dictionaries for notation of square
    ranks_to_rows = {"1" : 0, "2" : 1, "3" : 2, "4" : 3, "5" : 4, "6": 5, "7" : 6, "8" : 7}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a" : 0, "b" : 1, "c" : 2, "d" : 3, "e" : 4, "f" : 5, "g" : 6, "h" : 7}
    cols_to_files = {v : k for k, v in files_to_cols.items()}
    
    def __init__(self, start_sq, target_sq, piece_moved, piece_captured=None, is_enpasant=False, is_castling=False, is_promotion=False):
        self.start_sq = start_sq
        self.target_sq = target_sq
        self.piece_moved = piece_moved
        self.piece_captured = piece_captured
        self.move_id = start_sq * 100 + target_sq
        self.is_enpassant = is_enpasant
        self.is_castling = is_castling
        self.is_promotion = is_promotion

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False
    
    def __str__(self):
        return self.cols_to_files[self.start_sq % 8] + self.rows_to_ranks[self.start_sq // 8] + self.cols_to_files[self.target_sq % 8] + self.rows_to_ranks[self.target_sq // 8]


if __name__ == "__main__":
    engine = BitboardEngine()
    engine.draw_board()