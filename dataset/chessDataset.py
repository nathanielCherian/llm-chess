import io
import random
import json

import chess.pgn
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from tqdm import tqdm
import numpy as np


class ChessDataset(Dataset):
    def __init__(self, num_games=100, num_random_moves=0, use_FEN=False, pgn_path=None, saved_data_path=None, save_data_to_path=None,
                 save_processed_to_json=None, end_in='both', use_addendum=False, random_seed=None):
        if random_seed is not None:
            random.seed(random_seed)

        self.num_games = num_games
        self.num_random_moves = num_random_moves
        self.use_FEN = use_FEN
        self.end_in = end_in
        self.use_addendum = use_addendum

        if save_data_to_path is not None and pgn_path is None:
            print('*** Can only save data read from pgn_path ***')
            exit(1)
        if save_data_to_path is not None and use_FEN:
            print('*** Cannot save unprocessed data in FEN form, set use_FEN=False to save data and set use_FEN=True when loading data ***')
            exit(1)
        

        if pgn_path is not None and saved_data_path is None:
            self.dataset = open(pgn_path)

            print('Loading games from .pgn')
            self.games = [self.process_game(str(chess.pgn.read_game(self.dataset).mainline_moves())) for _ in tqdm(range(self.num_games))]
            self.games = [g for g in self.games if g is not None]

            if save_data_to_path is not None:
                np.save(save_data_to_path, self.games)

        elif pgn_path is None and saved_data_path is not None:
            self.games = np.load(saved_data_path)
            self.games = [(str(g[0]), str(g[1])) for g in self.games]
        else:
            print('*** Exactly one of pgn_path and saved_data_path must be passed in ***')
            exit(1)

        if save_processed_to_json is not None:
            to_json = [dict(zip(('prompt', 'completion'), g)) for g in self.games]
            with open(save_processed_to_json, 'w') as f:
                json.dump(to_json, f)

    def process_game(self, moves):
        if moves == '':
            return None

        pgn = io.StringIO(moves)
        game = chess.pgn.read_game(pgn)

        num_total_moves = game.end().board().ply()
        if num_total_moves <= 1:
            return None
        num_keep_moves = random.randint(0, num_total_moves - 1)

        if self.use_addendum:
            addendum = f' {1 + num_keep_moves // 2}. ' if (num_keep_moves % 2 == 0) else ' '
            addendum = addendum[1:] if num_keep_moves == 0 else addendum
        else:
            addendum = ''

        if self.end_in == 'white':
            num_keep_moves = num_keep_moves + (num_keep_moves % 2) if num_keep_moves < num_total_moves - 1 else num_keep_moves - (num_keep_moves % 2)
            addendum = f' {1 + num_keep_moves // 2}. '
            addendum = addendum[1:] if num_keep_moves == 0 else addendum
        elif self.end_in == 'black':
            num_keep_moves = num_keep_moves + (1 - num_keep_moves % 2) if num_keep_moves < num_total_moves - 1 else num_keep_moves - (1 - num_keep_moves % 2)
            addendum = ' '

        board = game.board()
        for i, uci_move in enumerate(game.mainline_moves()):
            if i == num_keep_moves:
                next_move = str(board.san(board.parse_uci(str(uci_move)))) if self.num_random_moves == 0 else 'N/A'
                break
            board.push(uci_move)

        for _ in range(self.num_random_moves):
            legal_moves = list(board.legal_moves)
            num_legal_moves = len(legal_moves)
            if len(legal_moves) == 0:
                break
            move_idx = 0 if num_legal_moves == 1 else random.randint(0, num_legal_moves-1)
            r_move = legal_moves[move_idx]
            board.push(r_move)

        if self.use_FEN:
            return board.fen(), next_move
        return str(chess.pgn.Game.from_board(board).mainline_moves()) + addendum, next_move

    def __len__(self):
        return len(self.games)

    def __getitem__(self, idx):
        return self.games[idx]


"""
Arguments of ChessDataset and default values:
    num_games=100                   Number of games to read from .pgn file (only matters if reading .pgn file)
    num_random_moves=0              Number of random moves to make after position if such move exists (no label returned)
    use_FEN=False                   Output the data in FEN if True, move notation if False
    pgn_path=None                   Path of the .pgn file (downloaded from https://database.lichess.org/)
    saved_data_path=None            Path of the saved .npy file (from setting save_data_to_path to anything besides None)
    save_data_to_path=None          Path to save .npy file containing processed subset of games
    save_processed_to_json=None     Path to save .json file containing processed subset of games
    end_in='both'                   Which player should make the next move, effectively always sets use_addendum=True
    use_addendum=False              Whether or not to add ' number. ' or ' ' to the end of moves, only applicable when end_in='both'
"""

if __name__ == '__main__':
    num_games = 10_000
    seed = 577

    # Save the processed dataset to a .json format (works with HuggingFace Trainers) with white to move next
    dataset = ChessDataset(pgn_path='data/lichess_db_standard_rated_2017-02.pgn', num_games=num_games, end_in='white', save_processed_to_json='data/subset_data.json', random_seed=seed)

    # Load the dataset
    dataset = ChessDataset(pgn_path='data/lichess_db_standard_rated_2017-02.pgn', num_games=num_games, random_seed=seed)
    dataloader = DataLoader(dataset)

    print('Enumerating dataset')
    for i, (game, move) in enumerate(tqdm(dataloader)):
        # Do stuff
        pass

    # Some games are empty (ie. 0 moves) or very short (ie. <= 2 moves), so total games is less than num_games
    print(f'total games enumerated: {i+1}')

    """
    
    Alternatively

    """

    # Can save a subset of entire dataset
    _ = ChessDataset(pgn_path='data/lichess_db_standard_rated_2017-02.pgn', num_games=num_games, save_data_to_path='data/subset_data.npy', random_seed=seed)

    # Can then load the presaved subset of dataset
    dataset = ChessDataset(saved_data_path='data/subset_data.npy', random_seed=seed)
    dataloader = DataLoader(dataset)

    print('Enumerating dataset')
    for i, (game, move) in enumerate(tqdm(dataloader)):
        # Do stuff
        pass

    # Some games are empty (ie. 0 moves) or very short (ie. <= 2 moves), so total games is less than num_games
    print(f'total games enumerated: {i+1}')

    """
    
    Note that there is no time/space benefit of saving subset of data for training, only for loading dataset
    
    """
