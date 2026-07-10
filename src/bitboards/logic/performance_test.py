from src.bitboards.engine.bitboard_engine import BitboardEngine
from src.bitboards.logic.adapter import to_bitboard
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

if __name__ == "__main__":
    start_time = time.perf_counter()
    gs = BitboardEngine()
    print(perft_divide(gs, 4))
    end_time = time.perf_counter()
    print(f"Execution time - {end_time-start_time:.4f} seconds")
