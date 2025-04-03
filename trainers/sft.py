from datasets import load_dataset
from trl import SFTConfig, SFTTrainer
from dataset.chessDataset import ChessDataset

import time
import os


num_games = 50_000
max_length = 64
save_name = time.strftime("%Y%m%d-%H%M%S")
pgn_path = 'data/lichess_db_standard_rated_2017-02.pgn'

if not os.path.exists('data/subset_data.json'):
    _ = ChessDataset(pgn_path=pgn_path, use_FEN=True, num_games=num_games, end_in='white', save_processed_to_json='data/subset_data.json')
dataset = load_dataset('json', data_files='data/subset_data.json', split='train')

training_args = SFTConfig(
    max_length=max_length,
    learning_rate=3e-4,
)
trainer = SFTTrainer(
    'facebook/opt-125m',
    train_dataset=dataset,
    args=training_args
)
trainer.train()

trainer.save_model(f'saved/models/{save_name}')
trainer.tokenizer.save_pretrained(f'saved/tokenizers/{save_name}')
