
# NOTE: you must call the globals to set up the engine, then it will run until you call engine.quit()


# -----------------
#      Imports
# -----------------



import numpy as np
import re

import chess
import chess.engine
import chess.pgn

import traceback



# -----------------
#      Globals
# -----------------




# ------------------------------
#      FEN Helper functions
# ------------------------------



def fen_to_matrix(fen):
    fen_board = fen.split(' ')[0]  # Get only the board part
    rows = fen_board.split('/')  # Split into ranks
    
    board_matrix = []
    
    for row in rows:
        expanded_row = []
        for char in row:
            if char.isdigit():  # Convert empty squares
                expanded_row.extend(['.'] * int(char))
            else:
                expanded_row.append(char)
        board_matrix.append(expanded_row)
    
    return np.array(board_matrix)



# ------------------------------
#      SAN Helper functions
# ------------------------------



def rooksReachingDst(positions, piece, white_to_move, matrix):
    srcs = []
    valid = []

    char = piece if white_to_move else piece.lower()

    guard = True
    for i in range(7):
        pos2 = positions[2] - 1 - i
        pos3 = positions[3]
        if (positions[0] == -1 and positions[1] == -1) or (positions[0] == pos2) or (positions[1] == pos3):
            if pos2 >= 0:
                if matrix[pos2][pos3] == char:
                    srcs.append([pos2, pos3])
                    if guard:
                        valid.append([pos2, pos3])
                    guard = False
                elif matrix[pos2][pos3] != '.':
                    guard = False
            else:
                break
        elif (pos2 >= 0) and (matrix[pos2][pos3] != '.'):
            guard = False

    guard = True
    for i in range(7):
        pos2 = positions[2] + 1 + i
        pos3 = positions[3]
        if (positions[0] == -1 and positions[1] == -1) or (positions[0] == pos2) or (positions[1] == pos3):
            if pos2 < 8:
                if matrix[pos2][pos3] == char:
                    srcs.append([pos2, pos3])
                    if guard:
                        valid.append([pos2, pos3])
                    guard = False
                elif matrix[pos2][pos3] != '.':
                    guard = False
            else:
                break
        elif (pos2 < 8) and (matrix[pos2][pos3] != '.'):
            guard = False

    guard = True
    for i in range(7):
        pos2 = positions[2]
        pos3 = positions[3] - 1 - i
        if (positions[0] == -1 and positions[1] == -1) or (positions[0] == pos2) or (positions[1] == pos3):
            if pos3 >= 0:
                if matrix[pos2][pos3] == char:
                    srcs.append([pos2, pos3])
                    if guard:
                        valid.append([pos2, pos3])
                    guard = False
                elif matrix[pos2][pos3] != '.':
                    guard = False
            else:
                break
        elif (pos3 >= 0) and (matrix[pos2][pos3] != '.'):
            guard = False

    guard = True
    for i in range(7):
        pos2 = positions[2]
        pos3 = positions[3] + 1 + i
        if (positions[0] == -1 and positions[1] == -1) or (positions[0] == pos2) or (positions[1] == pos3):
            if pos3 < 8:
                if matrix[pos2][pos3] == char:
                    srcs.append([pos2, pos3])
                    if guard:
                        valid.append([pos2, pos3])
                    guard = False
                elif matrix[pos2][pos3] != '.':
                    guard = False
            else:
                break
        elif (pos3 < 8) and (matrix[pos2][pos3] != '.'):
            guard = False

    return valid, srcs


def bishopsReachingDst(positions, piece, white_to_move, matrix):
    srcs = []
    valid = []

    char = piece if white_to_move else piece.lower()

    guard = True
    for i in range(7):
        pos2 = positions[2] - 1 - i
        pos3 = positions[3] - 1 - i
        if (positions[0] == -1 and positions[1] == -1) or (positions[0] == pos2) or (positions[1] == pos3):
            if (pos2 >= 0) and (pos3 >= 0):
                if matrix[pos2][pos3] == char:
                    srcs.append([pos2, pos3])
                    if guard:
                        srcs.append([pos2, pos3])
                    guard = False
                elif matrix[pos2][pos3] != '.':
                    guard = False
            else:
                break
        elif (pos2 >= 0) and (pos3 >= 0) and (matrix[pos2][pos3] != '.'):
            guard = False

    guard = True
    for i in range(7):
        pos2 = positions[2] - 1 - i
        pos3 = positions[3] + 1 + i
        if (positions[0] == -1 and positions[1] == -1) or (positions[0] == pos2) or (positions[1] == pos3):
            if (pos2 >= 0) and (pos3 < 8):
                if matrix[pos2][pos3] == char:
                    srcs.append([pos2, pos3])
                    if guard:
                        srcs.append([pos2, pos3])
                    guard = False
                elif matrix[pos2][pos3] != '.':
                    guard = False
            else:
                break
        elif (pos2 >= 0) and (pos3 < 8) and (matrix[pos2][pos3] != '.'):
            guard = False

    guard = True
    for i in range(7):
        pos2 = positions[2] + 1 + i
        pos3 = positions[3] - 1 - i
        if (positions[0] == -1 and positions[1] == -1) or (positions[0] == pos2) or (positions[1] == pos3):
            if (pos2 < 8) and (pos3 >= 0):
                if matrix[pos2][pos3] == char:
                    srcs.append([pos2, pos3])
                    if guard:
                        srcs.append([pos2, pos3])
                    guard = False
                elif matrix[pos2][pos3] != '.':
                    guard = False
            else:
                break
        elif (pos2 < 8) and (pos3 >= 0) and (matrix[pos2][pos3] != '.'):
            guard = False

    guard = True
    for i in range(7):
        pos2 = positions[2] + 1 + i
        pos3 = positions[3] + 1 + i
        if (positions[0] == -1 and positions[1] == -1) or (positions[0] == pos2) or (positions[1] == pos3):
            if (pos2 < 8) and (pos3 < 8):
                if matrix[pos2][pos3] == char:
                    srcs.append([pos2, pos3])
                    if guard:
                        srcs.append([pos2, pos3])
                    guard = False
                elif matrix[pos2][pos3] != '.':
                    guard = False
            else:
                break
        elif (pos2 < 8) and (pos3 < 8) and (matrix[pos2][pos3] != '.'):
            guard = False

    return valid, srcs


def knightsReachingDst(positions, piece, white_to_move, matrix):
    srcs = []
    char = piece if white_to_move else piece.lower()
    knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]

    for move in knight_moves:
        pos2 = positions[2] + move[0]
        pos3 = positions[3] + move[1]
        if (positions[0] == -1 and positions[1] == -1) or (positions[0] == pos2) or (positions[1] == pos3):
            if 0 <= pos2 < 8 and 0 <= pos3 < 8:
                if matrix[pos2][pos3] == char:
                    srcs.append([pos2, pos3])

    return srcs, srcs


def kingsReachingDst(positions, piece, white_to_move, matrix):
    srcs = []
    char = piece if white_to_move else piece.lower()
    king_moves = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]

    for move in king_moves:
        pos2 = positions[2] + move[0]
        pos3 = positions[3] + move[1]
        if (positions[0] == -1 and positions[1] == -1) or (positions[0] == pos2) or (positions[1] == pos3):
            if 0 <= pos2 < 8 and 0 <= pos3 < 8:
                if matrix[pos2][pos3] == char:
                    srcs.append([pos2, pos3])

    return srcs, srcs


def pawnsReachingDst(positions, piece, white_to_move, matrix, move_type, en_passant_pos):
    srcs = []
    valid = []

    char = piece if white_to_move else piece.lower()

    if move_type == 'Pawn double move':
        if matrix[positions[2]][positions[3]] == char:
            srcs.append([positions[0], positions[1]])
            if white_to_move:
                if matrix[8 - 3][ord(san[0]) - ord('a')] == '.':
                    valid.append([positions[0], positions[1]])
            else:
                if matrix[8 - 6][ord(san[0]) - ord('a')] == '.':
                    valid.append([positions[0], positions[1]])

    else:
        if matrix[positions[2]][positions[3]] == char:
            srcs.append([positions[0], positions[1]])
            valid.append([positions[0], positions[1]])

    return valid, srcs


def getMoveInfo(san, white_to_move, matrix):
    # move src row, col, dst row, col

    # Check for castling
    if san == 'O-O-O':
        if white_to_move:
            return 'Long castling', [0, 'a', 0, 'd']
        else:
            return 'Long castling', [7, 'a', 7, 'd']
    elif san == 'O-O':
        if white_to_move:
            return 'Short castling', [0, 'h', 0, 'f']
        else:
            return 'Short castling', [7, 'h', 7, 'f']
    
    # pawn actions
    elif 'a' <= san[0] <= 'h':
        # pawn capture
        if 'x' in san:
            if white_to_move:
                if re.fullmatch(r"[a-h]x[a-h][1-8]", san):
                    return 'Pawn capture', [8 - int(san[3]) - 1, ord(san[0]) - ord('a'), 8 - int(san[3]), ord(san[2]) - ord('a')]
                
                if re.fullmatch(r"[a-h]x[a-h][1-8] e\.p\.", san):
                    return 'En passant capture', [8 - int(san[3]) - 1, ord(san[0]) - ord('a'), 8 - int(san[3]), ord(san[2]) - ord('a')]
                
                if re.fullmatch(r"[a-h]x[a-h]8=[RNBQ]", san):
                    return 'Pawn capture and promotion', [8 - 7, ord(san[0]) - ord('a'), 8 - 8, ord(san[2]) - ord('a')]
                
            else:
                if re.fullmatch(r"[a-h]x[a-h][1-8]", san):
                    return 'Pawn capture', [8 - int(san[3]) + 1, ord(san[0]) - ord('a'), 8 - int(san[3]), ord(san[2]) - ord('a')]
                
                if re.fullmatch(r"[a-h]x[a-h][1-8] e\.p\.", san):
                    return 'En passant capture', [8 - int(san[3]) + 1, ord(san[0]) - ord('a'), 8 - int(san[3]), ord(san[2]) - ord('a')]
                
                if re.fullmatch(r"[a-h]x[a-h]1=[RNBQ]", san):
                    return 'Pawn capture and promotion', [8 - 2, ord(san[0]) - ord('a'), 8 - 1, ord(san[2]) - ord('a')]

        # pawn move
        else:
            if white_to_move:
                if re.fullmatch(r"[a-h]4", san):
                    if matrix[8 - 3][ord(san[0]) - ord('a')] == 'P':
                        return 'Pawn move', [8 - 3, ord(san[0]) - ord('a'), 8 - int(san[1]), ord(san[0]) - ord('a')]
                    else:
                        return 'Pawn double move', [8 - 2, ord(san[0]) - ord('a'), 8 - int(san[1]), ord(san[0]) - ord('a')]
                
                if re.fullmatch(r"[a-h][1-8]", san):
                    return 'Pawn move', [8 - int(san[1]) - 1, ord(san[0]) - ord('a'), 8 - int(san[1]), ord(san[0]) - ord('a')]
                
                
                if re.fullmatch(r"[a-h][1|8]=[RNBQ]", san):
                    return 'Pawn promotion', [8 - 7, ord(san[0]) - ord('a'), 8 - 8, ord(san[0]) - ord('a')]
            
            else:
                if re.fullmatch(r"[a-h]5", san):
                    if matrix[8 - 6][ord(san[0]) - ord('a')] == 'p':
                        return 'Pawn move', [8 - 6, ord(san[0]) - ord('a'), 8 - int(san[1]), ord(san[0]) - ord('a')]
                    else:
                        return 'Pawn double move', [8 - 7, ord(san[0]) - ord('a'), 8 - int(san[1]), ord(san[0]) - ord('a')]
                
                if re.fullmatch(r"[a-h][1-8]", san):
                    return 'Pawn move', [8 - int(san[1]) + 1, ord(san[0]) - ord('a'), 8 - int(san[1]), ord(san[0]) - ord('a')]
                
                if re.fullmatch(r"[a-h][1|8]=[RNBQ]", san):
                    return 'Pawn promotion', [8 - 2, ord(san[0]) - ord('a'), 8 - 1, ord(san[0]) - ord('a')]

    
    # piece actions
    elif san[0] in 'RNBQK':
        # piece capture
        if 'x' in san:
            if re.fullmatch(r"[RNBQK][x][a-h][1-8]", san):
                return 'Piece capture', [-1, -1, 8 - int(san[3]), ord(san[2]) - ord('a')]
            elif re.fullmatch(r"[RNBQK][a-h][x][a-h][1-8]", san):
                return 'Ambiguous column piece capture', [-1, ord(san[2]) - ord('a'), 8 - int(san[4]), ord(san[3]) - ord('a')]
            elif re.fullmatch(r"[RNBQK][1-8][x][a-h][1-8]", san):
                return 'Ambiguous row piece capture', [8 - int(san[1]), -1, 8 - int(san[4]), ord(san[3]) - ord('a')]
        
        # piece move
        else:
            if re.fullmatch(r"[RNBQK][a-h][1-8]", san):
                return 'Piece move', [-1, -1, 8 - int(san[2]), ord(san[1]) - ord('a')]
            elif re.fullmatch(r"[RNBQK][a-h][a-h][1-8]", san):
                return 'Ambiguous column piece move', [-1, ord(san[1]) - ord('a'), 8 - int(san[3]), ord(san[2]) - ord('a')]
            elif re.fullmatch(r"[RNBQK][1-8][a-h][1-8]", san):
                return 'Ambiguous row piece move', [8 - int(san[1]), -1, 8 - int(san[3]), ord(san[2]) - ord('a')]
            
    
    return 'Unknown move type', [-1, -1, -1, -1]



# -------------------------
#      Check functions
# -------------------------



def failToRemoveCheck(board, trial_board):
    if board.is_check():
        if trial_board.is_check():
            return True

    return False

def castlingRights(fen, move_type, white_to_move):
    castling_rights = fen.split(' ')[2]

    if move_type == 'Long castling':
        if white_to_move:
            return 'K' in castling_rights
        else:
            return 'k' in castling_rights
    elif move_type == 'Short castling':
        if white_to_move:
            return 'Q' in castling_rights
        else:
            return 'q' in castling_rights
        
    return True


def getIllegalMoveType(fen, board, san):
    matrix = fen_to_matrix(fen)
    #print(matrix)

    white_to_move = 'white' if board.turn else 'black'


    # Check for checkmate or check
    if san[-1] == '#':
        san = san[:-1]
        if board.is_legal(board.parse_san(san)):
            return 'Incorrect checkmate indication'
    elif san[-1] == '+':
        san = san[:-1]
        if board.is_legal(board.parse_san(san)):
            return 'Incorrect check indication'
        

    # Get the piece type
    piece_type = None
    if san[0] in ['R', 'N', 'B', 'Q', 'K']:
        piece_type = san[0]
    elif san[0] in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
        piece_type = 'P'
    elif san[0] == 'O':
        piece_type = 'C'
    else:
        return 'Unknown piece type'

    # Get the move type and positions
    move_type, positions = getMoveInfo(san, white_to_move, matrix)

    #print(move_type, positions)


    # Check if the move is unknown
    if move_type == 'Unknown move type':
        return 'Unknown move type'


    # Check if castling is allowed
    if not castlingRights(fen, move_type, white_to_move):
        return 'No castling rights'


    # Check if the move is a self capture
    if 'castling' not in move_type:
        if white_to_move and matrix[positions[2]][positions[3]] in ['P', 'R', 'N', 'B', 'Q', 'K']:
            return 'Self capture'
        elif not white_to_move and matrix[positions[2]][positions[3]] in ['p', 'r', 'n', 'b', 'q', 'k']:
            return 'Self capture'
    
    
    en_passant_pos = fen.split(' ')[3]
    if move_type == 'En passant capture':
        if en_passant_pos != chr(positions[3] + ord('a')) + str(8 - positions[2]):
            return 'Illegal en passant capture'
        
        if white_to_move:
            if matrix[8 - 5][positions[3]] != 'p':
                return 'Illegal en passant capture'
        else:
            if matrix[8 - 4][positions[3]] != 'P':
                return 'Illegal en passant capture'
        

    # Check if the capture notation is correct
    if ('capture' in move_type) and (move_type != 'En passant capture'):
        if white_to_move:
            if matrix[positions[2]][positions[3]] not in ['p', 'r', 'n', 'b', 'q', 'k']:
                return 'No piece to be captured'
        else:
            if matrix[positions[2]][positions[3]] not in ['P', 'R', 'N', 'B', 'Q', 'K']:
                return 'No piece to be captured'
    elif 'castling' not in move_type:
        if matrix[positions[2]][positions[3]] != '.':
            return 'Empty square is not empty'


    # Check if the castling is legal
    row = 7 if white_to_move else 0

    if move_type == 'Long castling':
        if matrix[row][4] != 'K':
            return 'Illegal castling'
        if matrix[row][0] != 'R':
            return 'Illegal castling'
        if matrix[row][1] != '.' or matrix[row][2] != '.' or matrix[row][3] != '.':
            return 'Castling through blocked squares'
        
    elif move_type == 'Short castling':
        if matrix[row][4] != 'K':
            return 'Illegal castling'
        if matrix[row][7] != 'R':
            return 'Illegal castling'
        if matrix[row][5] != '.' or matrix[row][6] != '.':
            return 'Castling through blocked squares'


    if move_type == 'Long castling' or move_type == 'Short castling':
        castle_board = chess.Board(board.fen())

        row = '1' if white_to_move else '8'

        for i in range(3):
            col = -1

            if move_type == 'Long castling':
                castle_board.set_piece_at(chess.parse_square('a' + row), None)
                castle_board.set_piece_at(chess.parse_square('b' + row), None)
                castle_board.set_piece_at(chess.parse_square('c' + row), None)
                castle_board.set_piece_at(chess.parse_square('d' + row), None)
                castle_board.set_piece_at(chess.parse_square('e' + row), None)

                col = chr(ord('c') + i)
            else:
                castle_board.set_piece_at(chess.parse_square('e' + row), None)
                castle_board.set_piece_at(chess.parse_square('f' + row), None)
                castle_board.set_piece_at(chess.parse_square('g' + row), None)
                castle_board.set_piece_at(chess.parse_square('h' + row), None)

                col = chr(ord('e') + i)

            castle_board.set_piece_at(chess.parse_square(col + row), chess.Piece.from_symbol('K' if white_to_move else 'k'))

            if castle_board.is_check():
                return 'Castling through check'

    else:
        # Check which pieces can reach the destination
        reaching = []
        aligned = []

        if piece_type == 'R':
            reaching, aligned = rooksReachingDst(positions, 'R', white_to_move, matrix)
        elif piece_type == 'B':
            reaching, aligned = bishopsReachingDst(positions, 'B', white_to_move, matrix)
        elif piece_type == 'Q':
            reaching, aligned = rooksReachingDst(positions, 'Q', white_to_move, matrix)
            reaching1, aligned1 = bishopsReachingDst(positions, 'Q', white_to_move, matrix)
            reaching += reaching1
            aligned += aligned1
        elif piece_type == 'N':
            reaching, aligned = knightsReachingDst(positions, 'N', white_to_move, matrix)
        elif piece_type == 'K':
            reaching, aligned = kingsReachingDst(positions, 'K', white_to_move, matrix)
        elif piece_type == 'P':
            reaching, aligned = pawnsReachingDst(positions, 'P', white_to_move, matrix, move_type, en_passant_pos)
            
        #print(reaching)
        #print(aligned)

        # Check if no piece can reach the destination
        if len(reaching) == 0:
            if len(aligned) > 0:
                return 'Attempting to move blocked piece'
            else:
                return 'No piece reaches destination'

        src = chr(reaching[0][1] + ord('a')) + str(8 - reaching[0][0])
        dst = chr(positions[3] + ord('a')) + str(8 - positions[2])

        #print(src, dst)

        trial_board = chess.Board(board.fen())
        trial_board.set_piece_at(chess.parse_square(src), None)

        piece = chess.Piece.from_symbol(piece_type if white_to_move else piece_type.lower())
        trial_board.set_piece_at(chess.parse_square(dst), piece)

        new_matrix = fen_to_matrix(trial_board.fen())
        #print(new_matrix)

        if failToRemoveCheck(board, trial_board):
            return 'Move keeps king in check'
        elif trial_board.is_check():
            return 'Attempting to move pinned piece'
        
        if len(reaching) > 1:
            return 'Ambiguous move'

    return "Unknown issue"



# ------------------------
#       Main function
# ------------------------



def evaluate_position(fen, san, time=0.1):
    board = chess.Board(fen)
    engine = chess.engine.SimpleEngine.popen_uci("/usr/local/bin/stockfish")
    limit = chess.engine.Limit(time=time)

    try:
        board.parse_san(san)
        board.push_san(san)

        #print("FEN:", board.fen())

        info = engine.analyse(board, limit)
        
        if "score" in info:
            bound = 1000


            # TODO: currently not using negative scores for black
            score = info["score"].white() if not board.turn else info["score"].black()


            print("Score:", score)

            if score.is_mate():
                mate = score.mate()
                if mate >= 0:
                    return 1.0, "Valid move"
                else:
                    return 0.0, "Valid move"
            else:
                cp = max(min(score.score(), bound), - bound)
                return (cp + bound) / (2 * bound), "Valid move"

        return (0.5, "Valid move")
    
    except chess.InvalidMoveError:
        return (0, 'Bad format')
    except chess.AmbiguousMoveError:
        return (0, 'Ambiguous format')
    except chess.IllegalMoveError:
        try:
            return (0, getIllegalMoveType(fen, board, san))
        except Exception as e:
            print(e)
            traceback.print_exc()
            return (0, 'getIllegalMoveType error')
    except:
            return (0, 'Unknown error')
    finally:
        engine.quit()

if __name__ == "__main__":
    # Example usage

    fen = "7K/8/8/6r1/5q2/8/P7/6k1 w - - 0 1"
    san = "a3"

    #fen = "rnbqkbnr/pppppppp/8/8/7q/8/PPPPPPP1/RNBQK3 b KQkq - 0 0"
    #san = "Qh1"

    #fen = "rnbqk3/ppppppp1/8/8/7Q/8/PPPPPPP1/RNBQK3 w KQkq - 0 0"
    #san = "Qh8"
    
    score, message = evaluate_position(fen, san)
    print(f"Score: {score}, Message: {message}")

