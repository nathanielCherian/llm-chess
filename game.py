import chess
from bot.GRPOBot import GRPOBot
from bot.humanBot import HumanBot
from bot.stockfishBot import StockfishBot


class Game():
    def __init__(self, white_model, black_model):
        self.board = chess.Board()
        self.cur_fen = self.board.fen()
        self.white = white_model
        self.black = black_model

    def print_board(self):
        print(self.board)

    def process_move(self, move):
        self.board.push_san(move)
        self.cur_fen = self.board.fen()
        print(move)
        self.print_board()
        if self.board.is_game_over():
            game = chess.pgn.Game()
            node = game
            for move in self.board.move_stack:
                node = node.add_variation(move)
            moves = str(game.mainline())
            print(moves)

            result = self.board.result()
            print(f'Result: {result}')
            self.white.end()
            self.black.end()
            return True

    def play(self):
        while True:
            white_move = self.white.get_move(self.cur_fen)
            if self.process_move(white_move):
                break

            black_move = self.black.get_move(self.cur_fen)
            if self.process_move(black_move):
                break


if __name__ == '__main__':
    white = GRPOBot()
    black = StockfishBot('stockfish/stockfish-windows-x86-64-avx2.exe', depth=1)

    game = Game(white, black)
    game.play()
