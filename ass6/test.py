import numpy as np
import random

class TicTacToe:
    def __init__(self, size=3):
        self.board = np.zeros((size, size), dtype=int)
        self.current_turn = 1  # 1 for 'X', -1 for 'O'

    def make_move(self, row, col):
        if self.board[row, col] == 0:
            self.board[row, col] = self.current_turn
            self.current_turn = -self.current_turn  # Switch turns
            return True
        return False

    def check_winner(self):
        for i in range(3):
            if abs(self.board[i, :].sum()) == 3: return self.board[i, 0]
            if abs(self.board[:, i].sum()) == 3: return self.board[0, i]
        if abs(np.diag(self.board).sum()) == 3: return self.board[0, 0]
        if abs(np.diag(np.fliplr(self.board)).sum()) == 3: return self.board[0, -1]
        if np.all(self.board != 0):
            return 0  # Draw
        return None

    def get_available_moves(self):
        return [(i, j) for i in range(3) for j in range(3) if self.board[i, j] == 0]

    def copy(self):
        new_game = TicTacToe(size=self.board.shape[0])
        new_game.board = np.copy(self.board)
        new_game.current_turn = self.current_turn
        return new_game

    def is_terminal(self):
        return self.check_winner() is not None

class MCTSNode:
    def __init__(self, game, move=None, parent=None):
        self.game = game
        self.move = move
        self.parent = parent
        self.children = []
        self.wins = 0
        self.visits = 0
        self.unvisited_moves = game.get_available_moves()

    def add_child(self, move):
        new_game = self.game.copy()
        new_game.make_move(*move)
        child_node = MCTSNode(new_game, move, self)
        self.children.append(child_node)
        self.unvisited_moves.remove(move)
        return child_node

    def update_stats(self, result):
        self.visits += 1
        if result == -1:
            self.wins += 1
        #elif result == 0:  # Draw
        #    self.wins += 0.5  # Adjust based on your scoring

    def is_fully_expanded(self):
        return len(self.unvisited_moves) == 0

    def is_terminal(self):
        return self.game.is_terminal()

# MCTS Methods Adaptation

def monte_carlo_tree_search(root, iterations=1000):
    for _ in range(iterations):
        leaf = traverse(root)
        simulation_result = rollout(leaf)
        backpropagate(leaf, simulation_result)
    return best_child(root)

def traverse(node):
    while node.is_fully_expanded() and not node.is_terminal():
        node = best_uct(node)
    return random.choice(node.children) if node.children else node

def rollout(node):
    current_simulation_game = node.game.copy()
    while not current_simulation_game.is_terminal():
        possible_moves = current_simulation_game.get_available_moves()
        move = random.choice(possible_moves)
        current_simulation_game.make_move(*move)
    return current_simulation_game.check_winner()

def rollout_policy(node):
    return random.choice(node.children)

def backpropagate(node, result):
    while node is not None:
        node.update_stats(result)
        node = node.parent

def best_uct(node):
    # UCT formula: wins / visits + sqrt(2 * log(parent.visits) / visits)
    log_parent_visits = np.log(node.parent.visits)
    return max(node.children, key=lambda x: x.wins / x.visits + np.sqrt(2 * log_parent_visits / x.visits))

def best_child(node):
    if not node.children:  # Check if the list of children is empty
        return None
    return max(node.children, key=lambda x: x.visits)

def pick_unvisited(node_children):
    for child in node_children:
        if child.visits == 0:
            return child
    return None

import tkinter as tk
from tkinter import messagebox

# Assuming the TicTacToe, MCTSNode, and MCTS functions are already defined as per the previous code

class TicTacToeGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Tic Tac Toe")
        self.game = TicTacToe()
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.initialize_board()
        self.player = 1  # Human is 1, AI is -1
        self.ai = -1

    def initialize_board(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j] = tk.Button(self.master, text='', font=('Arial', 24), height=2, width=5,
                                               command=lambda row=i, col=j: self.on_click(row, col))
                self.buttons[i][j].grid(row=i, column=j)

    def on_click(self, row, col):
        if self.game.make_move(row, col) and self.game.current_turn == self.ai:
            self.update_button_text()
            winner = self.game.check_winner()
            if winner is not None:
                self.end_game(winner)
            else:
                self.ai_move()

    def ai_move(self):
        root = MCTSNode(self.game)
        best_move = monte_carlo_tree_search(root, iterations=5000)
        if best_move is not None:
            self.game.make_move(*best_move.move)
        else:
            # Fallback strategy: make a random move or handle the situation appropriately
            self.make_random_move()
        self.update_button_text()
        winner = self.game.check_winner()
        if winner is not None:
            self.end_game(winner)

    def make_random_move(self):
        available_moves = self.game.get_available_moves()
        if available_moves:
            move = random.choice(available_moves)
            self.game.make_move(*move)


    def update_button_text(self):
        for i in range(3):
            for j in range(3):
                if self.game.board[i, j] == 1:
                    self.buttons[i][j]['text'] = 'X'
                elif self.game.board[i, j] == -1:
                    self.buttons[i][j]['text'] = 'O'

    def end_game(self, winner):
        if winner == 1:
            messagebox.showinfo("Game Over", "X wins!")
        elif winner == -1:
            messagebox.showinfo("Game Over", "O wins!")
        else:
            messagebox.showinfo("Game Over", "It's a draw!")
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    gui = TicTacToeGUI(root)
    root.mainloop()
