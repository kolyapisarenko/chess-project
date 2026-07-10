from src.bitboards.engine.bitboard_engine import BitboardEngine
from src.bitboards.logic.bitboard_utils import BitboardConstants
import time

def perft(gs, depth):
    nodes = 0
    if depth == 0:
        return 1
    else:
        moves = gs.get_valid_moves()
        for move in moves:
            gs.make_move(move)
            nodes += perft(gs, depth - 1)
            gs.undo_move()
    return nodes

def perft_divide(gs, depth):
    total_nodes = 0
    if depth == 0:
        return 0
    moves = gs.get_valid_moves()
    for move in moves:
        gs.make_move(move)
        nodes_for_this_move = perft(gs, depth - 1)
        gs.undo_move()
        total_nodes += nodes_for_this_move
        print(str(move) + f" - {nodes_for_this_move}")
    return total_nodes

def read_from_fen(fen_string):
        fen_board = BitboardEngine()
        fen_board.new_board.clear_board()
        parts = fen_string.split(" ")
        position_part = parts[0]
        row, col = 7, 0
        
        for figure in position_part:
            if figure == "/":
                row -= 1
                col = 0
            elif figure.isdigit():
                col += int(figure)
            else:
                square = row * 8 + col
                if figure == "r":
                    fen_board.new_board.black_rooks = BitboardConstants.set_bit(fen_board.new_board.black_rooks, square)
                elif figure == "R":
                    fen_board.new_board.white_rooks = BitboardConstants.set_bit(fen_board.new_board.white_rooks, square)
                elif figure == "q":
                    fen_board.new_board.black_queen = BitboardConstants.set_bit(fen_board.new_board.black_queen, square)
                elif figure == "Q":
                    fen_board.new_board.white_queen = BitboardConstants.set_bit(fen_board.new_board.white_queen, square)
                elif figure == "b":
                    fen_board.new_board.black_bishops = BitboardConstants.set_bit(fen_board.new_board.black_bishops, square)
                elif figure == "B":
                    fen_board.new_board.white_bishops = BitboardConstants.set_bit(fen_board.new_board.white_bishops, square)
                elif figure == "n":
                    fen_board.new_board.black_knights = BitboardConstants.set_bit(fen_board.new_board.black_knights, square)
                elif figure == "N":
                    fen_board.new_board.white_knights = BitboardConstants.set_bit(fen_board.new_board.white_knights, square)
                elif figure == "k":
                    fen_board.new_board.black_king = BitboardConstants.set_bit(fen_board.new_board.black_king, square)
                elif figure == "K":
                    fen_board.new_board.white_king = BitboardConstants.set_bit(fen_board.new_board.white_king, square)
                elif figure == "p":
                    fen_board.new_board.black_pawns = BitboardConstants.set_bit(fen_board.new_board.black_pawns, square)
                elif figure == "P":
                    fen_board.new_board.white_pawns = BitboardConstants.set_bit(fen_board.new_board.white_pawns, square)
                col += 1
        fen_board.white_to_move = (parts[1] == "w")
        
        fen_board.castling_rights = 0
        castling_part = parts[2]
        
        if castling_part != "-":
            if "K" in castling_part:
                fen_board.castling_rights |= fen_board.WK
            if "Q" in castling_part:
                fen_board.castling_rights |= fen_board.WQ
            if "k" in castling_part:
                fen_board.castling_rights |= fen_board.BK
            if "q" in castling_part:
                fen_board.castling_rights |= fen_board.BQ
        
        fen_board.prev_castling_rights = fen_board.castling_rights

        ep_part = parts[3]
        if ep_part == "-":
            fen_board.en_passant_sq = -1
        else:
            ep_col = ord(ep_part[0]) - ord('a')
            ep_row = int(ep_part[1]) - 1
            fen_board.en_passant_sq = ep_row * 8 + ep_col  
        fen_board.prev_en_passant_sq = fen_board.en_passant_sq
        
        fen_board.new_board._update_occupancy()
        return fen_board

    

if __name__ == "__main__":
    start_time = time.perf_counter()
    #gs = read_from_fen("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq -")
    #print(perft_divide(gs, 4))
    gs = read_from_fen("8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1")
    print(perft_divide(gs, 4))
    gs = read_from_fen("r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1")
    print(perft_divide(gs, 4))
    #gs = read_from_fen("r2q1rk1/pP1p2pp/Q4n2/bbp1p3/Np6/1B3NBn/pPPP1PPP/R3K2R b KQ - 0 1")
    #print(perft_divide(gs, 4))
    gs = read_from_fen("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8")
    print(perft_divide(gs, 4))
    gs = read_from_fen("r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10")
    print(perft_divide(gs, 4))
    end_time = time.perf_counter()
    print(f"Execution time - {end_time-start_time:.4f} seconds")
