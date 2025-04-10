import json
import time
import math

from joblib import Parallel, delayed
import chess
import chess.engine

from evaluation import evaluate_position


def get_eval(game, move):
    engine = chess.engine.SimpleEngine.popen_uci('stockfish/stockfish-windows-x86-64-avx2.exe')
    board = chess.Board(game)
    try:
        board.push_san(move)
        evaluation = engine.analyse(board, chess.engine.Limit(time=1))['score']
        score = evaluation.relative.score(mate_score=math.inf)
        score /= -100
        score = 1 / (1 + 10 ** (-score / 4))
        return score
    except Exception:
        return 0
    finally:
        engine.quit()


def batch_eval(games, moves, n_jobs):
    ret = Parallel(n_jobs=n_jobs)(delayed(get_eval)(g, m) for g, m in zip(games, moves))
    return ret


if __name__ == '__main__':
    with open('data/subset_data.json', 'r') as file:
        data = json.load(file)[:10]
        games = [d['prompt'] for d in data]
        moves = [d['completion'] for d in data]

        for g, m in zip(games, moves):
            print(g, m)

        start = time.time()
        evals = [evaluate_position(g, m)[0] for g, m in zip(games, moves)]
        end = time.time()
        print(f'\ntime elapsed: {end - start}')
        for e in evals:
            print(e)

        start = time.time()
        evals = batch_eval(games, moves, 10)
        end = time.time()
        print(f'\ntime elapsed: {end - start}')
        for e in evals:
            print(e)
