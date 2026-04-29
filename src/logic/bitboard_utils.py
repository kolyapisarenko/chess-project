class BitboardConstants:
    SQUARES = [1 << i for i in range(64)]
    FILE_A = 0x0101010101010101
    FILE_B = FILE_A << 1
    FILE_C = FILE_B << 1
    FILE_D = FILE_C << 1
    FILE_E = FILE_D << 1
    FILE_F = FILE_E << 1
    FILE_G = FILE_F << 1
    FILE_H = FILE_G << 1

    NOT_A_FILE = ~(FILE_A) & 0xFFFFFFFFFFFFFFFF
    NOT_AB_FILE = ~(FILE_A | FILE_B) & 0xFFFFFFFFFFFFFFFF
    NOT_H_FILE = ~(FILE_H) & 0xFFFFFFFFFFFFFFFF
    NOT_GH_FILE = ~(FILE_G | FILE_H) & 0xFFFFFFFFFFFFFFFF

    @staticmethod
    def set_bit(bitboard, square_index):
        return (bitboard | BitboardConstants.SQUARES[square_index]) & 0xFFFFFFFFFFFFFFFF
    
    @staticmethod
    def pop_bit(bitboard, square_index):
        return (bitboard & (~BitboardConstants.SQUARES[square_index])) & 0xFFFFFFFFFFFFFFFF
    
    @staticmethod
    def get_bit(bitboard, square_index):
        return bool(bitboard & (BitboardConstants.SQUARES[square_index]))
    
    @staticmethod
    def print_bitboard(bitboard):
        for rank in range(7, -1, -1):
            row = ""
            for file in range(8):
                square = rank * 8 + file
                if BitboardConstants.get_bit(bitboard, square):
                    row += "1 "
                else:
                    row += ". "
            print(row)
        print(f"\nNumeric value {bitboard}")

if __name__ == "__main__":
    empty_board = 0
    new_board = BitboardConstants.set_bit(empty_board, 28)
    BitboardConstants.print_bitboard(new_board)