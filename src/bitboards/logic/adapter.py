from src.bitboards.logic.board import Board
from src.bitboards.logic.bitboard_utils import BitboardConstants
from src import config

def to_matrix(bitboard):
    # Initialize an empty matrix with "--" for empty squares
    matrix = [["--" for _ in range(config.COLS)] for _ in range(config.ROWS)]

    #Prepare the piece_map with keys matching the original_keys in matrix engine
    original_keys = ["w_pawn", "w_rook", "w_knight", "w_bishop", "w_queen", "w_king", "b_pawn", "b_rook", "b_knight", "b_bishop", "b_queen", "b_king"]
    piece_map = {char: getattr(bitboard, attr) for char, attr in bitboard.piece_map.items()}
    bitboard_keys = list(piece_map.keys())

    #Change the keys in piece_map to match the original_keys in matrix engine
    for original_key, old_key in zip(original_keys, bitboard_keys):
        piece_map[original_key] = piece_map.pop(old_key)

    #Convert the bitboard to a matrix representation
    for rank in range(config.ROWS - 1, -1, -1):
            for file in range(config.COLS):
                square = rank * config.COLS + file
                #Check each piece type and set the corresponding character in the matrix
                for char, bitboard in piece_map.items():
                    if BitboardConstants.get_bit(bitboard, square):
                        piece_char = char
                        break
                    else:
                        piece_char = "--"
                matrix[config.ROWS - 1 - rank][file] = piece_char

    return matrix

def to_bitboard(matrix):
    # Initialize an empty Board object
    bitboard = Board()
    bitboard.clear_board()  # Clear the board before setting pieces

    for rank in range(config.ROWS - 1, -1, -1):
        for file in range(config.COLS):
            square = rank * config.COLS + file
            piece_char = matrix[config.ROWS - 1 - rank][file]
            if piece_char != "--":
                if piece_char == "w_pawn":
                    bitboard.white_pawns = BitboardConstants.set_bit(bitboard.white_pawns, square)
                elif piece_char == "w_rook":
                    bitboard.white_rooks = BitboardConstants.set_bit(bitboard.white_rooks, square)
                elif piece_char == "w_knight":
                    bitboard.white_knights = BitboardConstants.set_bit(bitboard.white_knights, square)
                elif piece_char == "w_bishop":
                    bitboard.white_bishops = BitboardConstants.set_bit(bitboard.white_bishops, square)
                elif piece_char == "w_queen":
                    bitboard.white_queen = BitboardConstants.set_bit(bitboard.white_queen, square)
                elif piece_char == "w_king":
                    bitboard.white_king = BitboardConstants.set_bit(bitboard.white_king, square)
                elif piece_char == "b_pawn":
                    bitboard.black_pawns = BitboardConstants.set_bit(bitboard.black_pawns, square)
                elif piece_char == "b_rook":
                    bitboard.black_rooks = BitboardConstants.set_bit(bitboard.black_rooks, square)
                elif piece_char == "b_knight":
                    bitboard.black_knights = BitboardConstants.set_bit(bitboard.black_knights, square)
                elif piece_char == "b_bishop":
                    bitboard.black_bishops = BitboardConstants.set_bit(bitboard.black_bishops, square)
                elif piece_char == "b_queen":
                    bitboard.black_queen = BitboardConstants.set_bit(bitboard.black_queen, square)
                elif piece_char == "b_king":
                    bitboard.black_king = BitboardConstants.set_bit(bitboard.black_king, square)

    # Update occupancy after setting pieces
    bitboard._update_occupancy()
    return bitboard

if __name__ == "__main__":
    board = Board()
    matrix = to_matrix(board)
    for row in matrix:
        print(" ".join(row))
    print()

    test_matrix = [
    ["--", "--", "--", "--", "--", "--", "--", "b_king"],
    ["--", "w_pawn", "--", "--", "--", "--", "w_pawn", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["w_king", "--", "--", "--", "--", "--", "--", "--"]
    ]

    bitboard = to_bitboard(test_matrix)
    bitboard.display_board()