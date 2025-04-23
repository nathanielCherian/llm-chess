from evaluation import evaluate_position


class HumanBot():
    def __init__(self):
        pass

    def end(self):
        pass

    def get_move(self, fen):
        print('Enter move: ', end='')
        move = input()
        while evaluate_position(fen, move)[1] != 'Valid move':
            print('Illegal move, try again')
            print('Enter move: ', end='')
            move = input()
        return move
