from src import config
PIECE_VALUES = {"pawn" : 100, "knight" : 320, "bishop" : 330, "rook" : 500, "queen" : 900, "king" : 0}

knight_scores = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]

pawn_scores = [
     80,  80,  80,  80,  80,  80,  80,  80,
     50,  50,  50,  50,  50,  50,  50,  50,
     10,  10,  20,  30,  30,  20,  10,  10,
      5,   5,  10,  25,  25,  10,   5,   5,
      0,   0,   0,  20,  20,   0,   0,   0,
      5,  -5, -10,   0,   0, -10,  -5,   5,
      5,  10,  10, -20, -20,  10,  10,   5,
      0,   0,   0,   0,   0,   0,   0,   0
]

bishop_scores = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -10,   0,   5,  10,  10,   5,   0, -10,
    -10,   5,   5,  10,  10,   5,   5, -10,
    -10,   0,  10,  10,  10,  10,   0, -10,
    -10,  10,  10,  10,  10,  10,  10, -10,
    -10,   5,   0,   0,   0,   0,   5, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
]

rook_scores = [
      0,   0,   0,   5,   5,   0,   0,   0,
      5,  10,  10,  10,  10,  10,  10,   5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
      0,   0,   0,   5,   5,   0,   0,   0
]

queen_scores = [
    -20, -10, -10,  -5,  -5, -10, -10, -20,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -10,   0,   5,   5,   5,   5,   0, -10,
     -5,   0,   5,   5,   5,   5,   0,  -5,
      0,   0,   5,   5,   5,   5,   0,  -5,
    -10,   5,   5,   5,   5,   5,   0, -10,
    -10,   0,   5,   0,   0,   0,   0, -10,
    -20, -10, -10,  -5,  -5, -10, -10, -20
]

king_scores = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
     20,  20,   0,   0,   0,   0,  20,  20,
     20,  30,  10,   0,   0,  10,  30,  20
]

PIECE_SQUARE_TABLE = {"knight" : knight_scores, "pawn" : pawn_scores, "bishop" : bishop_scores, "rook" : rook_scores, "queen" : queen_scores, "king" : king_scores}

def evaluate(gs):
    white_position = 0
    black_position = 0
    if gs.checkmate:
        if gs.white_to_move:
            return -99999
        else:
            return 99999
    if gs.stealmate:
        return 0
    
    white_bitboards = {"pawn" : gs.new_board.white_pawns, "knight" : gs.new_board.white_knights, "bishop" : gs.new_board.white_bishops, "rook" : gs.new_board.white_rooks, "queen" : gs.new_board.white_queen}
    black_bitboards = {"pawn" : gs.new_board.black_pawns, "knight" : gs.new_board.black_knights, "bishop" : gs.new_board.black_bishops, "rook" : gs.new_board.black_rooks, "queen" : gs.new_board.black_queen}

    for piece_type, bitboard in white_bitboards.items():
        temp_bb = bitboard
        while temp_bb:
            square = (temp_bb & -temp_bb).bit_length() - 1
            white_position += PIECE_SQUARE_TABLE[piece_type][square] + PIECE_VALUES[piece_type]
            temp_bb &= temp_bb - 1
    
    for piece_type, bitboard in black_bitboards.items():
        temp_bb = bitboard
        while temp_bb:
            square = (temp_bb & -temp_bb).bit_length() - 1
            black_position += PIECE_SQUARE_TABLE[piece_type][63 - square] + PIECE_VALUES[piece_type]
            temp_bb &= temp_bb - 1
    
    w_king_bb = gs.new_board.white_king
    if w_king_bb:
        w_king_sq = (w_king_bb & -w_king_bb).bit_length() - 1
        white_position += PIECE_SQUARE_TABLE["king"][w_king_sq] + PIECE_VALUES["king"]
        
    b_king_bb = gs.new_board.black_king
    if b_king_bb:
        b_king_sq = (b_king_bb & -b_king_bb).bit_length() - 1
        black_position += PIECE_SQUARE_TABLE["king"][63 - b_king_sq] + PIECE_VALUES["king"]
    """
    for r in range(config.ROWS):
        for c in range(config.COLS):
            if gs.board[r][c] != "--":
                piece = gs.board[r][c]
                piece_color = piece[0]
                piece_type = piece[2:]
                square = r * 8 + c  
                if piece_color == "w":
                    white_position += PIECE_SQUARE_TABLE[piece_type][square] + PIECE_VALUES[piece_type]
                else:
                    black_position += PIECE_SQUARE_TABLE[piece_type][63 - square] + PIECE_VALUES[piece_type]"""

    return white_position - black_position
