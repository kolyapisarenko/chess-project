from src.bitboards.engine import ai_engine, ai_evaluator, bitboard_engine
from src.bitboards.scripts.db_logger import init_db, log_game_to_db
import random
import time
import uuid
import multiprocessing

def select_move(gs, depth, epsilon=0.1):
    legal_moves = gs.get_valid_moves()
    if not legal_moves:
        return None

    scored_moves = ai_engine.get_scored_moves(gs, depth)
    reverse_sort = gs.white_to_move
    scored_moves.sort(key=lambda x: x[1], reverse=reverse_sort)
        
    if random.random() < epsilon:
        top_candidates = scored_moves[:5]
        chosen_pair = random.choice(top_candidates)
        return chosen_pair[0]
    else:
        return scored_moves[0][0]

def play_single_game(depth=4, epsilon=0.1):
    gs = bitboard_engine.BitboardEngine()
    game_id = str(uuid.uuid4())
    position_hashes = []

    half_move_counter = 0
    max_random_half_moves = 8

    last_time = time.time() * 1000

    while not (gs.checkmate or gs.stealmate or gs.on_time or gs.check_insufficient_material()):
        current_time = time.time() * 1000
        delta_time = current_time - last_time
        last_time = current_time
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

        position_hashes.append(gs.get_position_hash())
        legal_moves = gs.get_valid_moves()
        if not legal_moves:
            break

        if half_move_counter < max_random_half_moves:
            chosen_move = random.choice(legal_moves)
        else:
            chosen_move = select_move(gs, depth, epsilon)

        gs.make_move(chosen_move)
        half_move_counter += 1
    
        gs.new_board.display_board()
        print()
        s = gs.black_time / 1000
        S = gs.white_time / 1000
        print(f"White time - {int(S // 60)} : {S % 60:.2f}")
        print(f"Black time - {int(s // 60)} : {s % 60:.2f}")
        print()
    final_result = 0.0
    if gs.checkmate:
        final_result = -1.0 if gs.white_to_move else 1.0
    elif gs.on_time:
        final_result = -1.0 if gs.white_time <= 0 else 1.0

    log_game_to_db(game_id, position_hashes, final_result)
    return final_result

def play_chess_game_worker(worker_id, depth=4, epsilon=0.1):
    print(f"[Worker {worker_id}] is running. Start genering 10 games on depth {depth}...")
    game_counter = 1
    while True:
        gs = bitboard_engine.BitboardEngine()
        game_id = str(uuid.uuid4())
        position_hashes = []

        half_move_counter = 0
        max_random_half_moves = 8

        last_time = time.time() * 1000

        while not (gs.checkmate or gs.stealmate or gs.on_time or gs.check_insufficient_material()):
            current_time = time.time() * 1000
            delta_time = current_time - last_time
            last_time = current_time
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

            position_hashes.append(gs.get_position_hash())
            legal_moves = gs.get_valid_moves()
            if not legal_moves:
                break

            if half_move_counter < max_random_half_moves:
                chosen_move = random.choice(legal_moves)
            else:
                chosen_move = select_move(gs, depth, epsilon)

            gs.make_move(chosen_move)
            half_move_counter += 1
        final_result = 0.0
        if gs.checkmate:
            final_result = -1.0 if gs.white_to_move else 1.0
        elif gs.on_time:
            final_result = -1.0 if gs.white_time <= 0 else 1.0

        log_game_to_db(game_id, position_hashes, final_result)
        if game_counter == 200:
            break
        print(f"[Worker {worker_id}] ended game №{game_counter}/10. Result: {final_result}. Added into db.")
        game_counter += 1
        

if __name__ == "__main__":
    NUM_CORES = 2
    TARGET_DEPTH = 3
    processes = []
    init_db()
    for i in range(NUM_CORES):
        p = multiprocessing.Process(target=play_chess_game_worker, args=(i, TARGET_DEPTH))
        processes.append(p)
        p.start()
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        for p in processes:
            p.terminate()
            p.join()