import chess


class StockfishBot():
    def __init__(self, path, depth=20, time=0.1):
        self.stockfish = chess.engine.SimpleEngine.popen_uci(path)
        self.depth = depth
        self.time = time

    def end(self):
        self.stockfish.quit()

    def get_move(self, fen):
        board = chess.Board(fen)
        res = self.stockfish.play(board, chess.engine.Limit(depth=self.depth, time=self.time)).move
        res = board.san(chess.Move.from_uci(str(res)))
        return res
