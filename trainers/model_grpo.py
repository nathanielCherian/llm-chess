import time
import os

from datasets import load_dataset
from trl import GRPOConfig, GRPOTrainer
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import AutoModelForCausalLM, TrainingArguments
import torch
from joblib import Parallel, delayed

from dataset.chessDataset import ChessDataset
from evaluation import evaluate_position
from batch_eval import batch_eval


dataset_path = "data/small_data.json"
pgn_path = 'data/lichess_db_standard_rated_2017-03.pgn'
if not os.path.exists(dataset_path):
    _ = ChessDataset(pgn_path=pgn_path, use_FEN=True, num_games=1000, end_in='white', save_processed_to_json=dataset_path)
dataset = load_dataset('json', data_files=dataset_path, split='train')

save_name = time.strftime("%Y%m%d-%H%M%S")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def reward_move(completions, **kwargs):
    prompts = kwargs["prompts"]
    rewards = batch_eval(prompts, completions, 24, enable_tqdm=False)
    return rewards


model = AutoModelForCausalLM.from_pretrained("saved/models/fb-chess-model-final").to(device)

training_args = GRPOConfig(
  output_dir="fb_grpo_model", 
  per_device_train_batch_size=24,
  num_train_epochs=3,
  save_strategy='no',
  report_to='none'
)

trainer = GRPOTrainer(
  model=model,
  reward_funcs=reward_move,
  args=training_args,
  train_dataset=dataset,
)
trainer.train()

trainer.save_model(f'saved/models/GRPO_{save_name}')
trainer.tokenizer.save_pretrained(f'saved/tokenizers/GRPO_{save_name}')
