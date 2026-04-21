import random
from src.engine.ai_evaluator import evaluate

def find_best_move(gs, depth = 4):
    best_move = None
    turn = gs.white_to_move
    if turn:
        best_score = float("-inf")
    else:
        best_score = float("inf")
    moves = gs.get_valid_moves()
    random.shuffle(moves)
    moves.sort(key=lambda m: m.piece_captured != "--", reverse=True)

    alpha = float("-inf")
    beta = float("inf")

    for move in moves:
        gs.make_move(move)
        score = minimax(gs, not turn, depth - 1, alpha, beta)
        gs.undo_move()
        if turn:
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score) 
        else:    
            if score < best_score:
                best_score = score
                best_move = move
            beta = min(beta, best_score)

    return best_move

def minimax(gs, is_maximazing, depth, alpha, beta):
    if depth == 0 or gs.checkmate or gs.stealmate:
        return evaluate(gs)
    moves = gs.get_valid_moves()
    if is_maximazing:
        max_eval = float("-inf")
        for move in moves:
            gs.make_move(move)
            score = minimax(gs, False, depth - 1, alpha, beta)
            gs.undo_move()
            max_eval = max(max_eval, score)
            alpha = max(alpha, score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float("inf")
        for move in moves:
            gs.make_move(move)
            score = minimax(gs, True, depth - 1, alpha, beta)
            gs.undo_move()
            min_eval = min(min_eval, score)
            beta = min(beta, score)
            if beta <= alpha:
                break
        return min_eval