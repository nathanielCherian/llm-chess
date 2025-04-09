import json
import time

from joblib import Parallel, delayed

from evaluation import evaluate_position


def batch_eval(games, moves, n_jobs):
    ret = Parallel(n_jobs=n_jobs)(delayed(evaluate_position)(g, m) for g, m in zip(games, moves))
    return ret


if __name__ == '__main__':
    with open('data/subset_data.json', 'r') as file:
        data = json.load(file)[:10]
        games = [d['prompt'] for d in data]
        moves = [d['completion'] for d in data]

        start = time.time()
        evals = [evaluate_position(g, m) for g, m in zip(games, moves)]
        end = time.time()
        print(end - start)

        start = time.time()
        evals = batch_eval(games, moves, 10)
        end = time.time()
        print(end - start)
