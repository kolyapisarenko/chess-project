from src.logic.bitboard_utils import BitboardConstants

KNIGHT_ATTACKS = [0] * 64
KING_ATTACKS = [0] * 64
mask = 0xFFFFFFFFFFFFFFFF

def generate_knight_moves(square):
    attacks = 0
    bit = 1 << square
    if (bit << 17) & mask & BitboardConstants.NOT_A_FILE:
        attacks |= (bit << 17) & mask
    if (bit << 10) & mask & BitboardConstants.NOT_AB_FILE:
        attacks |= (bit << 10) & mask
    if (bit << 15) & mask & BitboardConstants.NOT_H_FILE:
        attacks |= (bit << 15) & mask
    if (bit << 6) & mask & BitboardConstants.NOT_GH_FILE:
        attacks |= (bit << 6) & mask
    if (bit >> 17) & mask & BitboardConstants.NOT_H_FILE:
        attacks |= (bit >> 17) & mask
    if (bit >> 10) & mask & BitboardConstants.NOT_GH_FILE:
        attacks |= (bit >> 10) & mask
    if (bit >> 15) & mask & BitboardConstants.NOT_A_FILE:
        attacks |= (bit >> 15) & mask
    if (bit >> 6) & mask & BitboardConstants.NOT_AB_FILE:
        attacks |= (bit >> 6) & mask
    return attacks

def generate_king_attacks(square):
    attack = 0
    bit = 1 << square
    attack |= ((bit << 8) | (bit >> 8)) & mask
    if (bit << 1) & mask & BitboardConstants.NOT_A_FILE:
        attack |= (bit << 1) & mask
    if (bit << 9) & mask & BitboardConstants.NOT_A_FILE:
        attack |= (bit << 9) & mask
    if (bit >> 7) & mask & BitboardConstants.NOT_A_FILE:
        attack |= (bit >> 7) & mask
    if (bit >> 1) & mask & BitboardConstants.NOT_H_FILE:
        attack |= (bit >> 1) & mask
    if (bit >> 9) & mask & BitboardConstants.NOT_H_FILE:
        attack |= (bit >> 9) & mask
    if (bit << 7) & mask & BitboardConstants.NOT_H_FILE:
        attack |= (bit << 7) & mask
    return attack

for sq in range(64):
    KNIGHT_ATTACKS[sq] = generate_knight_moves(sq)
    KING_ATTACKS[sq] = generate_king_attacks(sq)