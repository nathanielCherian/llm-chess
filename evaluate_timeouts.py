import json

import matplotlib.pyplot as plt
from batch_eval import batch_eval


with open('data/subset_data.json', 'r') as file:
    data = json.load(file)
    games = [d['prompt'] for d in data]
    moves = [d['completion'] for d in data]

    evals = batch_eval(games, moves, 10, 1)
