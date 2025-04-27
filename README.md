# Tetris 2048

A combination of two classic games: Tetris and 2048, implemented in Python using the stddraw module.

## Game Description

Tetris 2048 combines the mechanics of Tetris and 2048:
- Tetris-style falling blocks with all 7 standard tetromino shapes
- Each block has a number (2 or 4 initially)
- Merge same-valued blocks when they touch column-wise
- Clear rows when they are completely filled
- Win by reaching a 2048 tile

## Controls

- **Left/Right Arrow Keys**: Move the tetromino left/right
- **Up Arrow Key**: Rotate the tetromino clockwise
- **Down Arrow Key**: Soft drop (move down faster)
- **Space Bar**: Hard drop (immediately drop to the bottom)

## Scoring

- Points are awarded when merging tiles (the value of the new tile is added to the score)
- Points are also awarded when clearing rows (the sum of all numbers in the row)

## Features

- All 7 standard tetromino shapes (I, O, Z, S, T, L, J)
- Next tetromino preview
- Score display
- Win detection when a 2048 tile is created
- Game over screen with final score

## Implementation

The game is implemented using the following Python modules:
- stddraw.py: For rendering graphics
- numpy: For handling the game grid
- random: For generating random tetromino shapes and numbers

## Project Structure

- `Tetris_2048.py`: Main game file
- `game_grid.py`: Implementation of the game grid and tile merging logic
- `tetromino.py`: Implementation of the tetromino shapes and movements
- `tile.py`: Implementation of the numbered tiles
- `point.py`: Simple class for handling 2D points
- `lib/`: Contains the stddraw library and supporting modules

## Requirements

- Python 3
- Required modules: numpy

## How to Run

```
python Tetris_2048.py
``` 
