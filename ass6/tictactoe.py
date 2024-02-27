import numpy as np
import random
import math
import tkinter as tk
#import sort?

# Zip would make the code look much cleaner instead of bombing this .py

class TicTacToe:
    def __init__(self, size=3, win_condition=3, mtsc_iterations=5000):
        self.size = size
        self.board = np.zeros((self.size, self.size), dtype=int)
        self.current_turn = 1  # 1 for X, -1 for O
        self.win_condition = win_condition

    def make_move(self, row, col):
        if self.board[row, col] == 0:
            self.board[row, col] = self.current_turn
            self.current_turn = -self.current_turn  #Switch turns
            return True
        return False

    def check_winner(self):
        for i in range(self.size):
            if abs(self.board[i, :].sum()) == self.size: return self.board[i, 0]
            if abs(self.board[:, i].sum()) == self.size: return self.board[0, i]
        if abs(np.diag(self.board).sum()) == self.size: return self.board[0, 0]
        if abs(np.diag(np.fliplr(self.board)).sum()) == self.size: return self.board[0, -1]
        if np.all(self.board != 0):
            return 0  # Draw
        return None

    def get_available_moves(self):
        return [(i, j) for i in range(self.size) for j in range(self.size) if self.board[i, j] == 0]

    def copy(self):
        new_game = TicTacToe(size=self.board.shape[0])
        new_game.board = np.copy(self.board)
        new_game.current_turn = self.current_turn
        return new_game

class MCTSNode:
    def __init__(self, game, parent=None, move=None):
        self.game = game
        self.parent = parent
        self.move = move
        self.wins = 0
        self.visits = 0
        self.children = []
        self.untried_moves = game.get_available_moves()

    def UCT(self):
        return self.wins / self.visits + math.sqrt(2) * math.sqrt(math.log(self.parent.visits) / self.visits) if self.parent else float('inf')

    def select_child(self):
        sorted_children = sorted(self.children, key=lambda c: c.UCT())
        print([c.UCT() for c in sorted_children])
        selected_child = max(sorted_children, key=lambda c: c.UCT())
        print(f"Selected move: {selected_child.move} with UCT: {selected_child.UCT()}")
        return selected_child

    def add_child(self, move):
        new_game = self.game.copy()
        new_game.make_move(*move)
        child_node = MCTSNode(new_game, parent=self, move=move)
        self.untried_moves.remove(move)
        self.children.append(child_node)
        return child_node

    def update(self, result):
        self.visits += 1
        if result == -1:
            self.wins += 1
        elif result == 0:
            self.wins += 0.5
        elif result == 1:
            self.wins -= 500000
        

def MCTS(root, iterations=500):
    for _ in range(iterations):
        node = root
        game = root.game.copy()

        # if game is over, backpropagate
        if game.check_winner() is None:
            while node.untried_moves == [] and node.children != []:
                node = node.select_child()
                game.make_move(*node.move)

            if node.untried_moves != []:
                move = random.choice(node.untried_moves)
                game.make_move(*move)
                node = node.add_child(move)
            
            while game.get_available_moves() != []:
                move = random.choice(game.get_available_moves())
                game.make_move(*move)

            #backpropagate
            while node is not None:
                node.update(game.check_winner())
                node = node.parent


class TicTacToeGUI:
    def __init__(self, master, size=3, win_condition=3, mtsc_iterations=5):
        self.mtsc_iterations = mtsc_iterations
        self.win_condition = win_condition
        self.master = master
        self.size = size 
        self.game = TicTacToe(size=size, win_condition=win_condition, mtsc_iterations=mtsc_iterations)
        self.buttons = [[None for _ in range(size)] for _ in range(size)]
        self.initialize_board()

    def initialize_board(self):
        for i in range(self.size):
            for j in range(self.size):
                button = tk.Button(self.master, text='', font=('Arial', 24), height=2, width=5,
                                   command=lambda row=i, col=j: self.on_click(row, col))
                button.grid(row=i, column=j)
                self.buttons[i][j] = button

    def on_click(self, row, col):
        if self.game.make_move(row, col):
            self.update_buttons()
            winner = self.game.check_winner()
            if winner is not None:
                self.end_game(winner)
            else:
                self.ai_move()

    def update_buttons(self):
        for i in range(self.size):
            for j in range(self.size):
                text = {1: 'X', -1: 'O', 0: ''}[self.game.board[i, j]]
                self.buttons[i][j].config(text=text)

    def ai_move(self):
        root = MCTSNode(self.game)
        MCTS(root, iterations=self.mtsc_iterations)
        move = root.select_child().move
        self.game.make_move(*move)
        self.update_buttons()
        winner = self.game.check_winner()
        if winner is not None:
            self.end_game(winner)

    def end_game(self, winner):
        result = {1: "X wins!", -1: "O wins!", 0: "Draw!"}[winner]
        message = tk.Message(self.master, text=result, width=200)
        message.grid(row=3, column=0, columnspan=3)
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(state='disabled')


def main():
    root = tk.Tk()
    root.title("Tic-Tac-Toe")
    app = TicTacToeGUI(root, size=3, win_condition=3, mtsc_iterations=500)
    root.mainloop()

main()


'''
def simulate_ai_game():
    game = TicTacToe()
    root = MCTSNode(game)

    while game.check_winner() is None:
        print(f"Turn: {'X' if game.current_turn == 1 else 'O'}")
        MCTS(root, iterations=1000)
        move = root.select_child().move
        game.make_move(*move)
        root = [child for child in root.children if child.move == move][0]
        
        print(game.board)
        print("----------")

        won = game.check_winner()
        if won:
            #print("Winner:", 'X' if winner == 1 else 'O' if winner == -1 else 'Draw')
            break

simulate_ai_game()
'''