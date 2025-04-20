import json

from dataset.chessDataset import ChessDataset

import time
import math

from torch.utils.data import DataLoader
from joblib import Parallel, delayed
import chess
import chess.engine
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt


def get_eval(game, move, time=0.1):
    engine = chess.engine.SimpleEngine.popen_uci('stockfish/stockfish-windows-x86-64-avx2.exe')
    new_board = chess.Board(game)
    old_board = chess.Board(game)
    try:
        new_board.push_san(move)

        old_info = engine.analyse(old_board, chess.engine.Limit(time=time))
        new_info = engine.analyse(new_board, chess.engine.Limit(time=time))

        old_score = old_info["score"].white()
        new_score = new_info["score"].white()

        old_mate, new_mate = None, None
        if old_score.is_mate():
            old_mate = old_score.mate()
        if new_score.is_mate():
            new_mate = new_score.mate()

        if old_mate is None and new_mate is None:
            ret = new_score.score() - old_score.score()
        
        elif old_mate is not None and new_mate is not None:
            if np.sign(old_mate) == np.sign(new_mate):
                ret = 0
            else:
                # Was white mate, made a move and is now black mate (very bad for white)
                if old_mate > new_mate:
                    ret = -math.inf
                # Was black mate, made a move and is now white mate (very good for white)
                else:
                    ret = math.inf
                
        elif old_mate is not None and new_mate is None:
            # Was white mating, made move, now is not mating (very bad for white)
            if old_mate >= 0:
                ret = -math.inf
            # Was black mating, made move, now is not mating (very good for white)
            else:
                ret = math.inf

        elif old_mate is None and new_mate is not None:
            # Was no one mating, made move, now white is mating (very good for white)
            if new_mate >= 0:
                ret = math.inf
            # Was no one mating, made move, now black is mating (very bad for white)
            else:
                ret = -math.inf

        # Adjust for turn
        # Evaluating white move (always for our model)
        if old_board.turn:
            return ret
        # Evaluating black move
        else:
            return -ret
    except Exception:
        return -123456
    finally:
        engine.quit()


def batch_diff_eval(games, moves, n_jobs, time=0.1, enable_tqdm=False):
    if enable_tqdm:
        print('Evaluating ...')
        ret = Parallel(n_jobs=n_jobs)(delayed(get_eval)(g, m, time=time) for g, m in tqdm(zip(games, moves), total=len(games)))
    else:
        ret = Parallel(n_jobs=n_jobs)(delayed(get_eval)(g, m, time=time) for g, m in zip(games, moves))
    return ret


if __name__ == '__main__':
    _ = ChessDataset(pgn_path='data/lichess_db_standard_rated_2017-02.pgn', num_games=100, use_FEN=True, save_processed_to_json='data/temp.json')

    with open('data/temp.json', 'r') as file:
        data = json.load(file)
        games = [d['prompt'] for d in data] + ['8/8/8/8/8/2r4k/8/3Q3K w - - 0 1'] + ['q2n4/1RRn4/2nn4/8/8/5r1k/8/6QK w - - 0 1']
        moves = [d['completion'] for d in data] + ['Qc1'] + ['Qf1']

        evals = batch_diff_eval(games, moves, 10, time=3, enable_tqdm=True)

        for i, e in enumerate(evals):
            print(e, games[i], moves[i])
