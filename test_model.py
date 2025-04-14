from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from dataset.chessDataset import ChessDataset
from torch.utils.data import DataLoader
from tqdm import tqdm
import matplotlib.pyplot as plt
from batch_eval import batch_eval
import numpy as np


# model = AutoModelForCausalLM.from_pretrained('saved/models/fb-chess-model-final')
# tokenizer = AutoTokenizer.from_pretrained('saved/tokenizers/fb-chess-tokenizer-final')

# model = AutoModelForCausalLM.from_pretrained('saved/models/20250406-130417')
# tokenizer = AutoTokenizer.from_pretrained('saved/tokenizers/20250406-130417')

# model = AutoModelForCausalLM.from_pretrained('saved/models/GRPO_20250413-165913')
# tokenizer = AutoTokenizer.from_pretrained('saved/tokenizers/GRPO_20250413-165913')

model = AutoModelForCausalLM.from_pretrained('saved/models/GRPO_20250413-174516')
tokenizer = AutoTokenizer.from_pretrained('saved/tokenizers/GRPO_20250413-174516')

model = model.to("cuda" if torch.cuda.is_available() else "cpu")


def generate_text(prompt, max_length=200):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_length=max_length,
        do_sample=True,
        temperature=0.7,
        top_p=0.9
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


dataset = ChessDataset(pgn_path='data/lichess_db_standard_rated_2017-03.pgn', end_in='white', num_games=1000, use_FEN=True, offset=50_000)
dataloader = DataLoader(dataset, shuffle=False)

prompts = []
responses = []

for i, (fen, _) in enumerate(tqdm(dataloader)):
    prompt = fen[0]
    response = generate_text(prompt)[len(prompt):]
    prompts.append(prompt)
    responses.append(response)

evals = batch_eval(prompts, responses, 60)
evals = np.array(evals)

plt.hist(evals, bins=50)
plt.show()
