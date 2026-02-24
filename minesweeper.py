#!/usr/bin/env python3
"""
Terminal Minesweeper - Classic Minesweeper for terminal
Author: Sagar Jadhav
"""

import os
import random
import sys

HIDDEN = '■'
MINE = '💣'
FLAG = '🚩'
NUMBERS = [' ', '①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧']

class Minesweeper:
    def __init__(self, width=9, height=9, mines=10):
        self.width = width
        self.height = height
        self.mines = mines
        self.game_over = False
        self.won = False
        self.board = [[HIDDEN for _ in range(width)] for _ in range(height)]
        self.real_board = [[' ' for _ in range(width)] for _ in range(height)]
        self.flags = set()
        self.first_click = True
        self.place_mines()
    
    def place_mines(self):
        positions = random.sample(range(self.width * self.height), self.mines)
        for pos in positions:
            y, x = divmod(pos, self.width)
            self.real_board[y][x] = MINE
        
        for y in range(self.height):
            for x in range(self.width):
                if self.real_board[y][x] != MINE:
                    count = self.count_mines(x, y)
                    self.real_board[y][x] = NUMBERS[count] if count > 0 else ' '
    
    def count_mines(self, x, y):
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.real_board[ny][nx] == MINE:
                        count += 1
        return count
    
    def draw(self):
        os.system('clear')
        print("  " + " ".join(str(i % 10) for i in range(self.width)))
        print(" +" + "-" * self.width * 2 + "+")
        
        for y in range(self.height):
            row = f"{y % 10}│"
            for x in range(self.width):
                if (y, x) in self.flags:
                    row += FLAG + ' '
                else:
                    row += self.board[y][x] + ' '
            row += "│"
            print(row)
        
        print(" +" + "-" * self.width * 2 + "+")
        print(f"Mines: {self.mines - len(self.flags)} | Flags: {len(self.flags)}")
        
        if self.game_over:
            print("\n💥 GAME OVER! 💥")
        elif self.won:
            print("\n🎉 YOU WIN! 🎉")
    
    def reveal(self, x, y):
        if (y, x) in self.flags:
            return
        
        if self.first_click:
            self.first_click = False
            if self.real_board[y][x] == MINE:
                self.place_mines()
                self.reveal(x, y)
                return
        
        if self.real_board[y][x] == MINE:
            self.game_over = True
            self.reveal_all()
            return
        
        if self.board[y][x] != HIDDEN:
            return
        
        self.board[y][x] = self.real_board[y][x]
        
        if self.real_board[y][x] == ' ':
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        self.reveal(nx, ny)
        
        self.check_win()
    
    def flag(self, x, y):
        if self.board[y][x] == HIDDEN:
            if (y, x) in self.flags:
                self.flags.remove((y, x))
            else:
                self.flags.add((y, x))
    
    def reveal_all(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.real_board[y][x] == MINE and (y, x) not in self.flags:
                    self.board[y][x] = MINE
    
    def check_win(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.real_board[y][x] != MINE and self.board[y][x] == HIDDEN:
                    return
        self.won = True
        self.game_over = True

def main():
    diff = input("Difficulty (1: Easy, 2: Medium, 3: Hard): ").strip()
    
    sizes = {
        '1': (9, 9, 10),
        '2': (16, 16, 40),
        '3': (30, 16, 99),
    }
    
    w, h, m = sizes.get(diff, (9, 9, 10))
    game = Minesweeper(w, h, m)
    
    import keyboard
    cursor = [0, 0]
    
    while not game.game_over:
        game.draw()
        print(f"\nCursor: {cursor[0]},{cursor[1]} | Arrow keys: move | Enter: reveal | F: flag | Q: quit")
        
        key = keyboard.read_key()
        
        if key == 'up' and cursor[0] > 0:
            cursor[0] -= 1
        elif key == 'down' and cursor[0] < game.height - 1:
            cursor[0] += 1
        elif key == 'left' and cursor[1] > 0:
            cursor[1] -= 1
        elif key == 'right' and cursor[1] < game.width - 1:
            cursor[1] += 1
        elif key == 'enter':
            game.reveal(cursor[1], cursor[0])
        elif key == 'f':
            game.flag(cursor[1], cursor[0])
        elif key == 'q':
            break
        
        if game.won:
            break
    
    game.draw()

if __name__ == '__main__':
    main()
