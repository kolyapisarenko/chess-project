import random
from src.bitboards.engine.ai_evaluator import evaluate, PIECE_VALUES, PIECE_SQUARE_TABLE

bit_to_matrix_dict = {"p" : "pawn", "n" : "knight", "b" : "bishop", "r" : "rook", "q" : "queen", "k" : "king"}

def find_best_move(gs, depth = 4):
    best_move = None
    turn = gs.white_to_move
    if turn:
        best_score = float("-inf")
    else:
        best_score = float("inf")
    moves = gs.get_valid_moves()
    moves.sort(key=score_moves, reverse=True)

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

def get_scored_moves(gs, depth=4):
    result = []
    best_score = None
    turn = gs.white_to_move
    if turn:
        best_score = float("-inf")
    else:
        best_score = float("inf")
    moves = gs.get_valid_moves()
    moves.sort(key=score_moves, reverse=True)

    alpha = float("-inf")
    beta = float("inf")

    for move in moves:
        gs.make_move(move)
        score = minimax(gs, not turn, depth - 1, alpha, beta)
        gs.undo_move()
        if turn:
            if score > best_score:
                best_score = score
            alpha = max(alpha, best_score)
        else:
            if score < best_score:
                best_score = score
            beta = min(beta, best_score)
        result.append((move, score))
    return result

def score_moves(move):
    bonus = 0
    if move.piece_captured != None:
        piece_captured_type = move.piece_captured
        bonus += (PIECE_VALUES[bit_to_matrix_dict[piece_captured_type.lower()]] * 100) - PIECE_VALUES[bit_to_matrix_dict[move.piece_moved.lower()]]
    if move.is_promotion:
        if move.promotion_piece == "q":
            bonus += 900
        elif move.promotion_piece == "r":
            bonus += 500
        elif move.promotion_piece == "b":
            bonus += 330
        elif move.promotion_piece == "n":
            bonus += 320
    if move.is_check:
        bonus += 500

    return bonus

def minimax(gs, is_maximazing, depth, alpha, beta):
    if depth == 0 or gs.checkmate or gs.stealmate:
        return evaluate(gs)
    moves = gs.get_valid_moves()
    moves.sort(key=score_moves, reverse=True)
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