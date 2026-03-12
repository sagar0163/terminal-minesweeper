#!/usr/bin/env python3
"""
Terminal Minesweeper - Enhanced Edition v2.0
Author: Sagar Jadhav
Version: 2.0 - Optimized & Enhanced
"""

import os
import random
import sys
import time

HIDDEN = '■'
MINE = '💣'
FLAG = '🚩'
QUESTION = '?'
NUMBERS = [' ', '①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧']
NUMBER_COLORS = ['\033[0m', '\033[94m', '\033[92m', '\033[91m', '\033[93m', '\033[95m', '\033[96m', '\033[90m', '\033[97m']
RESET = '\033[0m'

class Minesweeper:
    """Enhanced Minesweeper Game"""
    
    def __init__(self, width=9, height=9, mines=10):
        self.width = width
        self.height = height
        self.mines = mines
        self.game_over = False
        self.won = False
        self.start_time = None
        self.elapsed_time = 0
        self.board = [[HIDDEN for _ in range(width)] for _ in range(height)]
        self.real_board = [[' ' for _ in range(width)] for _ in range(height)]
        self.flags = set()
        self.questions = set()
        self.first_click = True
        self.moves = 0
        self.cursor = [height // 2, width // 2]
        self.place_mines()
    
    def place_mines(self, exclude_pos=None):
        """Place mines randomly, excluding first click position"""
        available = list(range(self.width * self.height))
        
        if exclude_pos:
            exclude_idx = exclude_pos[0] * self.width + exclude_pos[1]
            if exclude_idx in available:
                available.remove(exclude_idx)
        
        positions = random.sample(available, self.mines)
        
        for pos in positions:
            y, x = divmod(pos, self.width)
            self.real_board[y][x] = MINE
        
        # Calculate numbers
        for y in range(self.height):
            for x in range(self.width):
                if self.real_board[y][x] != MINE:
                    count = self.count_mines(x, y)
                    self.real_board[y][x] = count if count > 0 else ' '
    
    def count_mines(self, x, y):
        """Count mines around a cell"""
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
        """Draw the game board"""
        os.system('clear')
        
        # Title
        print(f"\n  \033[1;36m╔{'═' * (self.width * 2 + 2)}╗")
        print(f"  ║  🎯 MINESWEEPER v2.0  ║")
        print(f"  ╚{'═' * (self.width * 2 + 2)}╝\033[0m\n")
        
        # Column headers
        print("   " + " ".join(str(i % 10) for i in range(self.width)))
        print("  +" + "─" * self.width * 2 + "+")
        
        # Board
        for y in range(self.height):
            row = f"{y % 10}│"
            for x in range(self.width):
                cell = self.board[y][x]
                
                # Highlight cursor
                if [y, x] == self.cursor:
                    if cell == HIDDEN:
                        row += f"\033[7m{HIDDEN}\033[0m "
                    else:
                        row += f"\033[7m{cell}\033[0m "
                    continue
                
                # Show flags
                if (y, x) in self.flags:
                    row += f"\033[31m{FLAG}\033[0m "
                # Show questions
                elif (y, x) in self.questions:
                    row += f"\033[33m{QUESTION}\033[0m "
                # Show revealed cells
                elif cell != HIDDEN:
                    if isinstance(cell, int) and cell > 0:
                        row += f"{NUMBER_COLORS[cell]}{NUMBERS[cell]}{RESET} "
                    else:
                        row += f"{cell} "
                # Hidden cells
                else:
                    row += f"{cell} "
            
            row += "│"
            print(row)
        
        print("  +" + "─" * self.width * 2 + "+")
        
        # Status bar
        mine_count = self.mines - len(self.flags)
        print(f"\n  💣 Mines: {mine_count} | 🚩 Flags: {len(self.flags)} | ⏱️ Time: {self.elapsed_time}s | Moves: {self.moves}")
        
        # Game over / Win message
        if self.game_over:
            if self.won:
                print(f"\n  \033[1;32m🎉 YOU WIN! 🎉\033[0m")
                print(f"  \033[1;36mTime: {self.elapsed_time}s | Moves: {self.moves}\033[0m")
            else:
                print(f"\n  \033[1;31m💥 GAME OVER! 💥\033[0m")
        
        print(f"\n  \033[90mArrow keys: move | Enter: reveal | F: flag | ?: question | Q: quit\033[0m")
    
    def reveal(self, x, y):
        """Reveal a cell"""
        if (y, x) in self.flags or (y, x) in self.questions:
            return
        
        if self.first_click:
            self.first_click = False
            self.start_time = time.time()
            
            # Regenerate mines to exclude first click
            if self.real_board[y][x] == MINE:
                self.real_board = [[' ' for _ in range(self.width)] for _ in range(self.height)]
                self.place_mines(exclude_pos=(y, x))
        
        if self.real_board[y][x] == MINE:
            self.game_over = True
            self.reveal_all(False)
            return
        
        if self.board[y][x] != HIDDEN:
            # Chord - click revealed number to open neighbors
            if isinstance(self.real_board[y][x], int) and self.real_board[y][x] > 0:
                self.chord(x, y)
            return
        
        self.moves += 1
        self.board[y][x] = self.real_board[y][x]
        
        # Flood fill empty cells
        if self.real_board[y][x] == ' ':
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if self.board[ny][nx] == HIDDEN and (ny, nx) not in self.flags:
                            self.reveal(nx, ny)
        
        self.check_win()
    
    def chord(self, x, y):
        """Chord on a number to open adjacent non-flagged cells"""
        count = self.real_board[y][x]
        flagged = sum(1 for dy in [-1, 0, 1] for dx in [-1, 0, 1] 
                     if 0 <= x+dx < self.width and 0 <= y+dy < self.height 
                     and (y+dy, x+dx) in self.flags)
        
        if flagged == count:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if self.board[ny][nx] == HIDDEN and (ny, nx) not in self.flags:
                            self.reveal(nx, ny)
    
    def flag(self, x, y):
        """Toggle flag on a cell"""
        if self.board[y][x] != HIDDEN:
            return
        
        if (y, x) in self.flags:
            self.flags.remove((y, x))
        else:
            self.flags.add((y, x))
            # Remove question if flagged
            if (y, x) in self.questions:
                self.questions.remove((y, x))
    
    def question(self, x, y):
        """Toggle question mark"""
        if self.board[y][x] != HIDDEN:
            return
        
        if (y, x) in self.questions:
            self.questions.remove((y, x))
        else:
            self.questions.add((y, x))
            # Remove flag if questioned
            if (y, x) in self.flags:
                self.flags.remove((y, x))
    
    def reveal_all(self, won=True):
        """Reveal all mines"""
        for y in range(self.height):
            for x in range(self.width):
                if self.real_board[y][x] == MINE:
                    if (y, x) not in self.flags:
                        self.board[y][x] = MINE
                elif (y, x) in self.flags and self.real_board[y][x] != MINE:
                    self.board[y][x] = '❌'  # Wrong flag
    
    def check_win(self):
        """Check if game is won"""
        for y in range(self.height):
            for x in range(self.width):
                if self.real_board[y][x] != MINE and self.board[y][x] == HIDDEN:
                    return
        
        self.won = True
        self.game_over = True
        self.elapsed_time = int(time.time() - self.start_time)
        
        # Flag remaining mines
        for y in range(self.height):
            for x in range(self.width):
                if self.real_board[y][x] == MINE and (y, x) not in self.flags:
                    self.flags.add((y, x))
        
        self.reveal_all(True)


def main():
    """Main entry point"""
    print("\n  🎯 Welcome to Minesweeper v2.0! 🎯\n")
    print("  Select Difficulty:")
    print("  ┌────────────────────────┐")
    print("  │ 1. Easy    (9x9, 10)  │")
    print("  │ 2. Medium  (16x16, 40) │")
    print("  │ 3. Hard    (30x16, 99)│")
    print("  └────────────────────────┘\n")
    
    diff = input("  Enter choice (1-3): ").strip()
    
    sizes = {
        '1': (9, 9, 10),
        '2': (16, 16, 40),
        '3': (30, 16, 99),
    }
    
    w, h, m = sizes.get(diff, (9, 9, 10))
    game = Minesweeper(w, h, m)
    
    import keyboard
    
    while not game.game_over:
        game.elapsed_time = int(time.time() - game.start_time) if game.start_time else 0
        game.draw()
        
        key = keyboard.read_key()
        
        if key == 'up' and game.cursor[0] > 0:
            game.cursor[0] -= 1
        elif key == 'down' and game.cursor[0] < game.height - 1:
            game.cursor[0] += 1
        elif key == 'left' and game.cursor[1] > 0:
            game.cursor[1] -= 1
        elif key == 'right' and game.cursor[1] < game.width - 1:
            game.cursor[1] += 1
        elif key == 'enter':
            game.reveal(game.cursor[1], game.cursor[0])
        elif key in ['f', 'F']:
            game.flag(game.cursor[1], game.cursor[0])
        elif key in ['?', 'shift+/']:
            game.question(game.cursor[1], game.cursor[0])
        elif key in ['q', 'Q']:
            break
        
        if game.won:
            break
    
    game.draw()
    print("\n  Thanks for playing!\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Game exited.\n")
    except Exception as e:
        print(f"\n  Error: {e}")
        print("  Make sure you're running in a terminal.")
