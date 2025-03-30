import io
import random

import chess.pgn
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from tqdm import tqdm
import numpy as np


class ChessDataset(Dataset):
    def __init__(self, num_games=100, num_random_moves=0, use_FEN=False, pgn_path=None, saved_data_path=None, save_data_to_path=None, used=True):
        self.num_games = num_games
        self.num_random_moves = num_random_moves
        self.use_FEN = use_FEN

        if save_data_to_path is not None and pgn_path is None:
            print('*** Can only save data read from pgn_path ***')
            exit(1)
        if save_data_to_path is not None and use_FEN:
            print('*** Cannot save data in FEN form, set use_FEN=False to save data and set use_FEN_True when loading data ***')
            exit(1)
        if save_data_to_path is None and not used:
            print('*** Either use the dataset or save it, cannot be neither ***')
            exit(1)

        if pgn_path is not None and saved_data_path is None:
            self.dataset = open(pgn_path)
            
            if used:
                print('Loading games from .pgn for use')
                self.games = [self.process_game(str(chess.pgn.read_game(self.dataset).mainline_moves())) for _ in tqdm(range(self.num_games))]
                self.games = [g for g in self.games if g is not None]

            if save_data_to_path is not None:
                print('Loading games from .pgn for saving')
                to_save = np.array([str(chess.pgn.read_game(self.dataset).mainline_moves()) for _ in tqdm(range(self.num_games))])
                to_save = [g for g in to_save if g != '']
                np.save(save_data_to_path, to_save)

        elif pgn_path is None and saved_data_path is not None:
            unprocessed_games = np.load(saved_data_path)
            print('Processing loaded game')
            self.games = [self.process_game(g) for g in tqdm(unprocessed_games)]
        else:
            print('*** Exactly one of pgn_path and saved_data_path must be passed in ***')
            exit(1)

    def process_game(self, moves):
        if moves == '':
            return None

        pgn = io.StringIO(moves)
        game = chess.pgn.read_game(pgn)

        num_total_moves = game.end().board().ply()
        num_keep_moves = random.randint(0, num_total_moves - 1)

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
        return str(chess.pgn.Game.from_board(board).mainline_moves()), next_move

    def __len__(self):
        return len(self.games)

    def __getitem__(self, idx):
        return self.games[idx]


"""
Arguments of ChessDataset and default values:
    num_games=100           number of games to read from .pgn file (only matters if reading .pgn file)
    num_random_moves=0      number of random moves to make after position if such move exists (no label returned)
    use_FEN=False           output the data in FEN if True, move notation if False
    pgn_path=None           Path of the .pgn file (downloaded from https://database.lichess.org/)
    saved_data_path=None    Path of the saved .npy file (from setting save_data_to_path to anything besides None)
    save_data_to_path=None  Path to save .npy file containing subset of games (for significantly lower storage + slightly faster loading in future)
    used=True               Whether this ChessDataset obejct will be used (as opposed to for only saving)
"""

if __name__ == '__main__':
    # Load the dataset
    dataset = ChessDataset(pgn_path='data/lichess_db_standard_rated_2017-02.pgn', num_games=10_000)
    dataloader = DataLoader(dataset)

    print('Enumerating dataset')
    for i, (game, move) in tqdm(enumerate(dataloader)):
        # Do stuff
        pass

    # Some games are empty (ie. 0 moves), so total games is less than num_games
    print(f'total games enumerated: {i+1}')

    """
    
    Alternatively, if storage becomes a concern:

    """

    # Can save a subset of entire dataset
    _ = ChessDataset(pgn_path='data/lichess_db_standard_rated_2017-02.pgn', num_games=10_000, save_data_to_path='data/subset_data.npy', used=False)

    # Can then load the presaved subset of dataset
    dataset = ChessDataset(saved_data_path='data/subset_data.npy')
    dataloader = DataLoader(dataset)

    print('Enumerating dataset')
    for i, (game, move) in tqdm(enumerate(dataloader)):
        # Do stuff
        pass

    # Some games are empty (ie. 0 moves), so total games is less than num_games
    print(f'total games enumerated: {i+1}')

    """
    
    Note that there is no time/space benefit of saving subset of data for training, only for loading dataset
    
    """
