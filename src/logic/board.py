from src.logic.bitboard_utils import BitboardConstants

class Board:
    def __init__(self):
        self.white_pawns = 0
        self.white_rooks = 0
        self.white_knights = 0
        self.white_bishops = 0
        self.white_queen = 0
        self.white_king = 0
        self.black_pawns = 0
        self.black_rooks = 0
        self.black_knights = 0
        self.black_bishops = 0
        self.black_queen = 0
        self.black_king = 0
        self._setup_initial_position()

    def _setup_initial_position(self):
        self.white_king = BitboardConstants.set_bit(self.white_king, 4)
        self.white_queen = BitboardConstants.set_bit(self.white_queen, 3)
        self.black_king = BitboardConstants.set_bit(self.black_king, 60)
        self.black_queen = BitboardConstants.set_bit(self.black_queen, 59)
        self.white_rooks = BitboardConstants.set_bit(self.white_rooks, 0)
        self.white_rooks = BitboardConstants.set_bit(self.white_rooks, 7)
        self.white_knights = BitboardConstants.set_bit(self.white_knights, 1)
        self.white_knights = BitboardConstants.set_bit(self.white_knights, 6)
        self.white_bishops = BitboardConstants.set_bit(self.white_bishops, 2)
        self.white_bishops = BitboardConstants.set_bit(self.white_bishops, 5)
        self.black_rooks = BitboardConstants.set_bit(self.black_rooks, 56)
        self.black_rooks = BitboardConstants.set_bit(self.black_rooks, 63)
        self.black_knights = BitboardConstants.set_bit(self.black_knights, 57)
        self.black_knights = BitboardConstants.set_bit(self.black_knights, 62)
        self.black_bishops = BitboardConstants.set_bit(self.black_bishops, 58)
        self.black_bishops = BitboardConstants.set_bit(self.black_bishops, 61)

        for i in range(8, 16):
            self.white_pawns = BitboardConstants.set_bit(self.white_pawns, i)
        for i in range(48, 56):
            self.black_pawns = BitboardConstants.set_bit(self.black_pawns, i)

        self.white_pieces = (self.white_pawns | self.white_rooks | self.white_knights | self.white_bishops | self.white_queen | self.white_king) & 0xFFFFFFFFFFFFFFFF
        self.black_pieces = (self.black_pawns | self.black_rooks | self.black_knights | self.black_bishops | self.black_queen | self.black_king) & 0xFFFFFFFFFFFFFFFF
        self.all_pieces = (self.white_pieces | self.black_pieces) & 0xFFFFFFFFFFFFFFFF

    def display_board(self):
        piece_map = {"P" : self.white_pawns, "R" : self.white_rooks, "B" : self.white_bishops, "N" : self.white_knights, "Q" : self.white_queen, "K" : self.white_king, "p" : self.black_pawns, "r" : self.black_rooks, "b" : self.black_bishops, "n" : self.black_knights, "q" : self.black_queen, "k" : self.black_king}

        for rank in range(7, -1, -1):
            row = f"{rank + 1} "
            for file in range(8):
                square = rank * 8 + file
                piece_char = ". "

                for char, bitboard in piece_map.items():
                    if BitboardConstants.get_bit(bitboard, square):
                        piece_char = char + " "
                        break
                row += piece_char
            print(row)
        print("  a b c d e f g h")

if __name__ == "__main__":
    my_board = Board()
    my_board.display_board() 