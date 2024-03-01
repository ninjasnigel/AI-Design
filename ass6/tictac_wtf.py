import numpy as np
import random
import math
import tkinter as tk
from collections import defaultdict
from abc import ABC, abstractmethod

class TicTacToe:
    def __init__(self, size=3, win_condition=3, board=None, dtype=int, current_turn=1, winner=None, terminal=False):
        self.size = size
        self.board = board
        if board is None:
            self.board = np.zeros((size, size), dtype=dtype)
        self.current_turn = current_turn
        self.winner = winner
        self.terminal = terminal
        self.win_condition = win_condition

    def make_move(self, row, col):
        if self.board[row, col] != 0:
            raise ValueError(f"Invalid move ({row}, {col})")
        self.board[row, col] = self.current_turn
        self.current_turn *= -1
        winner = self.check_winner()
        terminal = winner is not None
        return TicTacToe(size=self.size, board=self.board, current_turn=self.current_turn, winner=winner, terminal=terminal)
        

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
    
    def is_terminal(self):
        return self.check_winner() is not None
    
    def find_children(self):
        return [self.make_move(*move) for move in self.get_available_moves()]
    
    def find_random_child(self):
        if self.is_terminal():
            return None
        return self.make_move(*random.choice(self.get_available_moves()))

    def reward(self):
        if self.current_turn is (not self.winner):
            return 0
        if self.winner == None or self.winner == 0:
            return 0.5
    
    def __hash__(self):
        return hash(str(self.board))
    
    def __eq__(self, other):
        return np.array_equal(self.board, other.board)
    
    def __str__(self):
        return str(self.board)

class MCTS:
    "Monte Carlo tree searcher. First rollout the tree then choose a move."

    def __init__(self, exploration_weight=2):
        self.Q = defaultdict(int)  # total reward of each node
        self.N = defaultdict(int)  # total visit count for each node
        self.children = dict()  # children of each node
        self.exploration_weight = exploration_weight

    def choose(self, node):
        if node.is_terminal():
            raise RuntimeError(f"choose called on terminal node {node}")

        for child in self.children:
            print(child, "child")

        print(node, "node")

        if node not in self.children:
            print("---")
            print(node, "<---")
            print('lol random choice')
            return node.find_random_child()

        def score(n):
            if self.N[n] == 0:
                return float("-inf")  # avoid unseen moves
            return self.Q[n] / self.N[n]  # average reward
        #print sorted after score
        print(sorted(self.children[node], key=score), "<---")
        return max(self.children[node], key=score)

    def do_rollout(self, node):
        "Make the tree one layer better. (Train for one iteration.)"
        path = self._select(node)
        leaf = path[-1]
        self._expand(leaf)
        reward = self._simulate(leaf)
        self._backpropagate(path, reward)

    def _select(self, node):
        "Find an unexplored descendent of `node`"
        path = []
        while True:
            path.append(node)
            if node not in self.children or not self.children[node]:
                # node is either unexplored or terminal
                return path
            unexplored = self.children[node] - self.children.keys()
            if unexplored:
                n = unexplored.pop()
                path.append(n)
                return path
            node = self._uct_select(node)  # descend a layer deeper
            if node in path:  # if we've already visited this node, break the loop
                break
        print('All nodes have been explored')
        return path

    def _expand(self, node):
        "Update the `children` dict with the children of `node`"
        if node in self.children:
            return  # already expanded
        self.children[node] = node.find_children()

    def _simulate(self, node):
        "Returns the reward for a random simulation (to completion) of `node`"
        invert_reward = True
        while True:
            if node.is_terminal():
                reward = node.reward()
                return 1 - reward if invert_reward else reward
            node = node.find_random_child()
            invert_reward = not invert_reward

    def _backpropagate(self, path, reward):
        "Send the reward back up to the ancestors of the leaf"
        for node in reversed(path):
            self.N[node] += 1
            self.Q[node] += reward
            reward = 1 - reward  # 1 for me is 0 for my enemy, and vice versa

    def _uct_select(self, node):
        "Select a child of node, balancing exploration & exploitation"

        # All children of node should already be expanded:
        assert all(n in self.children for n in self.children[node])

        log_N_vertex = math.log(self.N[node])

        def uct(n):
            "Upper confidence bound for trees"
            return self.Q[n] / self.N[n] + self.exploration_weight * math.sqrt(
                log_N_vertex / self.N[n]
            )

        return max(self.children[node], key=uct)

class TicTacToeGUI:
    def __init__(self, master, size=3, win_condition=3, mcts_iterations=5000):
        self.mcts_iterations = mcts_iterations
        self.win_condition = win_condition
        self.master = master
        self.size = size 
        self.game = TicTacToe(size=size, win_condition=win_condition)
        self.tree = MCTS()
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
        self.game.make_move(row, col)
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
        for i in range(self.mcts_iterations):
            game_copy = self.game.copy()  # Create a copy of the game
            self.tree.do_rollout(game_copy)  # Perform rollout on the game copy
        move = self.tree.choose(self.game)
        print("chosen move", move)
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
    app = TicTacToeGUI(root, size=3, win_condition=3, mcts_iterations=50)
    root.mainloop()

main()