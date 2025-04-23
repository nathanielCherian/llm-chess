from transformers import AutoModelForCausalLM, AutoTokenizer
import chess
from evaluation import evaluate_position


class GRPOBot():
    def __init__(self):
        self.board = chess.Board()
        self.model = AutoModelForCausalLM.from_pretrained('saved/models/GRPO_20250413-174516')
        self.tokenizer = AutoTokenizer.from_pretrained('saved/tokenizers/GRPO_20250413-174516')
        self.num_times_regen = 0
        self.num_moves_regen = 0
        self.num_fails = 0

    def end(self):
        print(f'num moves regened: {self.num_moves_regen}, num times regened: {self.num_times_regen}, num failures: {self.num_fails}')

    def generate_text(self, prompt, p=0.7):
        inputs = self.tokenizer(prompt, return_tensors='pt').to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_length=100,
            do_sample=True,
            top_p=p
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def get_move(self, fen):
        res = self.generate_text(fen)[len(fen):]
        p = 0.7

        if evaluate_position(fen, res)[1] != 'Valid move':
            self.num_moves_regen += 1

        while evaluate_position(fen, res)[1] != 'Valid move':
            print(res, p)
            self.num_times_regen += 1

            if p > 5:
                self.num_fails += 1
                board = chess.Board(fen)
                for move in board.legal_moves:
                    return board.san(move)

            print('Illegal, regenerating ...')
            p += 0.05
            res = self.generate_text(fen, p)[len(fen):]
        return res
