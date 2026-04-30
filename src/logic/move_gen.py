from src.logic.bitboard_utils import BitboardConstants
from src.logic.magic_number import get_magic_candidate
from src.logic import magics

class AttackTables:
    def __init__(self):
        self.mask = 0xFFFFFFFFFFFFFFFF
        self.KNIGHT_ATTACKS = [0] * 64
        self.KING_ATTACKS = [0] * 64
        self.ROOK_ATTACKS = [None] * 64
        self.BISHOP_ATTACKS = [None] * 64
        
        self.ROOK_MASKS = [self.mask_rook_occupancy(sq) for sq in range(64)]
        self.BISHOP_MASKS = [self.mask_bishop_occupancy(sq) for sq in range(64)]
        self.ROOK_SHIFTS = [bin(m).count('1') for m in self.ROOK_MASKS]
        self.BISHOP_SHIFTS = [bin(m).count('1') for m in self.BISHOP_MASKS]
        
        self.init_static_attacks()
        self.init_sliders_tables()

    def init_static_attacks(self):
        for sq in range(64):
            self.KNIGHT_ATTACKS[sq] = self.generate_knight_moves(sq)
            self.KING_ATTACKS[sq] = self.generate_king_attacks(sq)

    def generate_knight_moves(self, square):
        attacks = 0
        bit = 1 << square
        if (bit << 17) & self.mask & BitboardConstants.NOT_A_FILE:
            attacks |= (bit << 17) & self.mask
        if (bit << 10) & self.mask & BitboardConstants.NOT_AB_FILE:
            attacks |= (bit << 10) & self.mask
        if (bit << 15) & self.mask & BitboardConstants.NOT_H_FILE:
            attacks |= (bit << 15) & self.mask
        if (bit << 6) & self.mask & BitboardConstants.NOT_GH_FILE:
            attacks |= (bit << 6) & self.mask
        if (bit >> 17) & self.mask & BitboardConstants.NOT_H_FILE:
            attacks |= (bit >> 17) & self.mask
        if (bit >> 10) & self.mask & BitboardConstants.NOT_GH_FILE:
            attacks |= (bit >> 10) & self.mask
        if (bit >> 15) & self.mask & BitboardConstants.NOT_A_FILE:
            attacks |= (bit >> 15) & self.mask
        if (bit >> 6) & self.mask & BitboardConstants.NOT_AB_FILE:
            attacks |= (bit >> 6) & self.mask
        return attacks

    def generate_king_attacks(self, square):
        attack = 0
        bit = 1 << square
        attack |= ((bit << 8) | (bit >> 8)) & self.mask
        if (bit << 1) & self.mask & BitboardConstants.NOT_A_FILE:
            attack |= (bit << 1) & self.mask
        if (bit << 9) & self.mask & BitboardConstants.NOT_A_FILE:
            attack |= (bit << 9) & self.mask
        if (bit >> 7) & self.mask & BitboardConstants.NOT_A_FILE:
            attack |= (bit >> 7) & self.mask
        if (bit >> 1) & self.mask & BitboardConstants.NOT_H_FILE:
            attack |= (bit >> 1) & self.mask
        if (bit >> 9) & self.mask & BitboardConstants.NOT_H_FILE:
            attack |= (bit >> 9) & self.mask
        if (bit << 7) & self.mask & BitboardConstants.NOT_H_FILE:
            attack |= (bit << 7) & self.mask
        return attack

    def mask_rook_occupancy(self, square):
        rook_mask = 0
        r = square // 8
        f = square % 8
        for i in range(r + 1, 7):
            rook_mask |= (1 << (i * 8 + f))
        for i in range(r - 1, 0, -1):
            rook_mask |= (1 << (i * 8 + f))
        for i in range(f + 1, 7):
            rook_mask |= (1 << (r * 8 + i))
        for i in range(f - 1, 0, -1):
            rook_mask |= (1 << (r * 8 + i))
        return rook_mask & 0xFFFFFFFFFFFFFFFF

    def mask_bishop_occupancy(self, square):
        bishop_mask = 0
        r = square // 8
        f = square % 8
        tr, tf = r + 1, f + 1
        while tr < 7 and tf < 7:
            bishop_mask |= (1 << (tr * 8 + tf))
            tr += 1
            tf += 1
        tr, tf = r + 1, f - 1
        while tr < 7 and tf > 0:
            bishop_mask |= (1 << (tr * 8 + tf))
            tr += 1
            tf -= 1
        tr, tf = r - 1, f + 1
        while tr > 0 and tf < 7:
            bishop_mask |= (1 << (tr * 8 + tf))
            tr -= 1
            tf += 1
        tr, tf = r - 1, f - 1
        while tr > 0 and tf > 0:
            bishop_mask |= (1 << (tr * 8 + tf))
            tr -= 1
            tf -= 1
        return bishop_mask & 0xFFFFFFFFFFFFFFFF

    def set_occupancy(self, index, nmask):
        occupancy = 0
        temp_mask = nmask
        bit_count = bin(nmask).count('1')
        for i in range(bit_count):
            square = (temp_mask & -temp_mask).bit_length() - 1
            temp_mask &= ~(1 << square)
            if index & (1 << i):
                occupancy |= (1 << square)
        return occupancy & self.mask

    def generate_rook_attacks_on_the_fly(self, square, occupancy):
        attacks = 0
        r = square // 8
        f = square % 8
        for i in range(r + 1, 8):
            target = i * 8 + f
            attacks |= (1 << target)
            if (1 << target) & occupancy:
                break
        for i in range(r - 1, -1, -1):
            target = i * 8 + f
            attacks |= (1 << target)
            if (1 << target) & occupancy:
                break
        for i in range(f - 1, -1, -1):
            target = r * 8 + i
            attacks |= (1 << target)
            if (1 << target) & occupancy:
                break
        for i in range(f + 1, 8):
            target = r * 8 + i
            attacks |= (1 << target)
            if (1 << target) & occupancy:
                break
        return attacks & self.mask

    def generate_bishop_attacks_on_the_fly(self, square, occupancy):
        attacks = 0
        r = square // 8
        f = square % 8
        tr, tf = r + 1, f + 1
        while tr < 8 and tf < 8:
            target = tr * 8 + tf
            attacks |= (1 << target)
            if (1 << target) & occupancy:
                break
            tr += 1
            tf += 1
        tr, tf = r + 1, f - 1
        while tr < 8 and tf > -1:
            target = tr * 8 + tf
            attacks |= (1 << target)
            if (1 << target) & occupancy:
                break
            tr += 1
            tf -= 1
        tr, tf = r - 1, f + 1
        while tr > -1 and tf < 8:
            target = tr * 8 + tf
            attacks |= (1 << target)
            if (1 << target) & occupancy:
                break
            tr -= 1
            tf += 1
        tr, tf = r - 1, f - 1
        while tr > -1 and tf > -1:
            target = tr * 8 + tf
            attacks |= (1 << target)
            if (1 << target) & occupancy:
                break
            tr -= 1
            tf -= 1
        return attacks & self.mask

    def init_sliders_tables(self):
        for sq in range(64):
            r_mask = self.ROOK_MASKS[sq]
            r_bits = self.ROOK_SHIFTS[sq]
            r_variations = 1 << r_bits
            self.ROOK_ATTACKS[sq] = [0] * r_variations
            for i in range(r_variations):
                occ = self.set_occupancy(i, r_mask)
                index = ((occ * magics.ROOK_MAGICS[sq]) & self.mask) >> (64 - r_bits)
                self.ROOK_ATTACKS[sq][index] = self.generate_rook_attacks_on_the_fly(sq, occ)

            b_mask = self.BISHOP_MASKS[sq]
            b_bits = self.BISHOP_SHIFTS[sq]
            b_variations = 1 << b_bits
            self.BISHOP_ATTACKS[sq] = [0] * b_variations
            for i in range(b_variations):
                occ = self.set_occupancy(i, b_mask)
                index = ((occ * magics.BISHOP_MAGICS[sq]) & self.mask) >> (64 - b_bits)
                self.BISHOP_ATTACKS[sq][index] = self.generate_bishop_attacks_on_the_fly(sq, occ)

    def get_rook_attacks(self, square, occupancy):
        occ = occupancy & self.ROOK_MASKS[square]
        index = ((occ * magics.ROOK_MAGICS[square]) & self.mask) >> (64 - self.ROOK_SHIFTS[square])
        return self.ROOK_ATTACKS[square][index]

    def get_bishop_attacks(self, square, occupancy):
        occ = occupancy & self.BISHOP_MASKS[square]
        index = ((occ * magics.BISHOP_MAGICS[square]) & self.mask) >> (64 - self.BISHOP_SHIFTS[square])
        return self.BISHOP_ATTACKS[square][index]

    def get_queen_attacks(self, square, occupancy):
        return self.get_rook_attacks(square, occupancy) | self.get_bishop_attacks(square, occupancy)

# Generator of magic numbers
"""
def find_magic_number(square, relevant_bits, is_bishop):
    mask = mask_bishop_occupancy(square) if is_bishop else mask_rook_occupancy(square)
    num_variations = 1 << relevant_bits 
    occupancies = [set_occupancy(i, mask) for i in range(num_variations)]
    attacks = []
    for occ in occupancies:
        if is_bishop:
            attacks.append(generate_bishop_attacks_on_the_fly(square, occ))
        else:
            attacks.append(generate_rook_attacks_on_the_fly(square, occ))

    while True:
        magic = get_magic_candidate()
        
        if bin((mask * magic) & 0xFF00000000000000).count('1') < 6:
            continue
            
        used_attacks = [0] * num_variations
        fail = False
        
        for i in range(num_variations):
            index = ((occupancies[i] * magic) & 0xFFFFFFFFFFFFFFFF) >> (64 - relevant_bits)
            
            if used_attacks[index] == 0:
                used_attacks[index] = attacks[i]
            elif used_attacks[index] != attacks[i]:
                fail = True
                break
        
        if not fail:
            return magic
"""

if __name__ == "__main__":
    attacks = AttackTables()

# Calculation magic number and saving it in magics.py
"""
with open("src/logic/magics.py", "w") as f:
    found_rooks = []
    found_bishops = []

    for sq in range(64):
        b_mask = mask_bishop_occupancy(sq)
        b_bits = bin(b_mask).count('1')
        magic_b = find_magic_number(sq, b_bits, True)
        found_bishops.append(hex(magic_b))
        
        r_mask = mask_rook_occupancy(sq)
        r_bits = bin(r_mask).count('1')
        magic_r = find_magic_number(sq, r_bits, False)
        found_rooks.append(hex(magic_r))

    f.write("ROOK_MAGICS = [\n")
    for m in found_rooks:
        f.write(f"    {m},\n")
    f.write("]\n\n")

    f.write("BISHOP_MAGICS = [\n")
    for m in found_bishops:
        f.write(f"    {m},\n")
    f.write("]\n")
"""