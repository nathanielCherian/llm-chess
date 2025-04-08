from datasets import load_dataset
from trl import GRPOConfig, GRPOTrainer
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import AutoModelForCausalLM, TrainingArguments
import torch
import time

from evaluation import evaluate_position
from joblib import Parallel, delayed

#dataset_path = "data/data_300k_01.json"
dataset_path = "data/subset_data.json"
dataset = load_dataset("json", data_files=dataset_path, split="train")
print("loaded dataset")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"using device {device}")

"""
def reward_move(completions, **kwargs):
    prompts = kwargs["prompts"]
    
    results = Parallel(n_jobs=8)(  # Adjust number of jobs to your CPU cores
        delayed(evaluate_position)(
            prompt.strip(),
            completion.strip(),
            stockfish_path="stockfish/stockfish-ubuntu-x86-64-avx2"
        )
        for prompt, completion in zip(prompts, completions)
    )
    
    # Extract first item from each result if evaluate_position returns a tuple
    return [score[0] for score in results]
"""

def reward_move(completions, **kwargs):
    start = time.time()
    prompts = kwargs["prompts"]
    rewards = []
    for prompt, completion in zip(prompts, completions):
      sf_eval = evaluate_position(prompt.strip(), completion.strip(), stockfish_path="stockfish/stockfish-ubuntu-x86-64-avx2")
      rewards.append(sf_eval[0])
    end = time.time()
    f = open("log.log", "a")
    f.write(f"{len(prompts)} {start} {end} {end-start}\n")
    f.close()
    return rewards
    #return [1.0 for _ in range(len(prompts))]

model = AutoModelForCausalLM.from_pretrained("finetuned_models/fb-chess-model-final")
print("on device: ", model.device)
model.to(device)
print("now on: ", model.device)

training_args = GRPOConfig(output_dir="fb_grpo_model", 
  logging_steps=10,
  per_device_train_batch_size=24,
  num_train_epochs=3,
)

trainer = GRPOTrainer(
  model=model,
  reward_funcs=reward_move,
  args=training_args,
  train_dataset=dataset,
)
trainer.train()
