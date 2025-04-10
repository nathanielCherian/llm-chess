import json

from flask import Flask, request, jsonify
from batch_eval import batch_eval

app = Flask(__name__)



@app.route('/eval', methods=['POST'])
def hello():
    data = request.get_json(force=True)

    games = [d['prompt'] for d in data]
    moves = [d['completion'] for d in data]
    n_jobs = 10

    #print(games)
    #print(moves)

    return jsonify(batch_eval(games, moves, n_jobs))



if __name__ == "__main__":
    app.run(debug=True)