# Import necessary libraries
import lib.stddraw as stddraw  # # For drawing and handling the game window
from lib.picture import Picture  # # For displaying images (menu background)
from lib.color import Color  # # For managing colors
import os  # # For file path operations
from game_grid import GameGrid  # # For handling the game grid and tile logic
from tetromino import Tetromino  # # For representing tetromino shapes
import random  # # For random selection (random tetrominoes)
import time  # # For timing events like keypresses
import sys  # # For exiting the program

def start():
    # # Initializes the game and starts the main game loop

    # # Set basic grid and canvas settings
    grid_h, grid_w = 20, 12
    canvas_w = 32 * (grid_w + 8)
    canvas_h = 32 * grid_h
    stddraw.setCanvasSize(canvas_w, canvas_h)
    stddraw.setXscale(-0.5, grid_w + 7.5)
    stddraw.setYscale(-0.5, grid_h - 0.5)

    # # Set static grid size for Tetromino class
    Tetromino.grid_height = grid_h
    Tetromino.grid_width = grid_w

    # # Create the game grid and first two tetromino pieces
    grid = GameGrid(grid_h, grid_w)
    current_tetromino = create_tetromino()
    next_tetromino = create_tetromino()

    grid.current_tetromino = current_tetromino
    grid.next_tetromino = next_tetromino

    game_paused = False  # # Game pause flag

    last_down_time = 0  # # Track last down key press time
    down_press_interval = 0.3  # # Minimum interval to count fast double-press
    down_press_count = 0  # # Counter for double-down-press to trigger hard drop

    score = 0  # # Initial score
    game_over = False  # # Game over flag

    # # Display initial menu screen
    display_game_menu(grid_h, grid_w)

    # # Main game loop
    while True:
        if stddraw.hasNextKeyTyped():
            key_typed = stddraw.nextKeyTyped()

            if key_typed == "p":
                game_paused = not game_paused
                time.sleep(0.2)  # # Avoid accidental multiple toggles

            if not game_paused:
                if key_typed == "left":
                    current_tetromino.move(key_typed, grid)
                elif key_typed == "right":
                    current_tetromino.move(key_typed, grid)
                elif key_typed == "down":
                    current_time = time.time()
                    if current_time - last_down_time < down_press_interval:
                        down_press_count += 1
                    else:
                        down_press_count = 1
                    last_down_time = current_time

                    if down_press_count == 2:
                        # # Perform hard drop if down pressed twice quickly
                        while current_tetromino.move("down", grid):
                            pass
                        down_press_count = 0
                    else:
                        current_tetromino.move("down", grid)

                elif key_typed == "space":
                    # # Hard drop on space press
                    while current_tetromino.move("down", grid):
                        pass
                elif key_typed == "up":
                    current_tetromino.rotate(grid)

            stddraw.clearKeysTyped()

        if game_paused:
            # # Show pause menu if paused
            action = draw_pause_menu(grid.grid_width, grid.grid_height)
            if action == "resume":
                game_paused = False
            elif action == "quit":
                sys.exit()

        else:
            # # Move current tetromino down automatically
            success = current_tetromino.move("down", grid)
            if not success:
                score += 10  # # Increase score when tetromino lands
                tiles, pos = current_tetromino.get_min_bounded_tile_matrix(True)
                grid.update_grid(tiles, pos)

                if grid.game_over:
                    grid.display_game_over()
                    time.sleep(2)
                    sys.exit()

                # # Switch to the next tetromino
                current_tetromino = next_tetromino
                grid.current_tetromino = current_tetromino
                next_tetromino = create_tetromino()
                grid.next_tetromino = next_tetromino

            # # Draw game elements
            grid.display()
            draw_score(score, grid.grid_width, grid.grid_height)
            stddraw.show(50)

def initialize_game():
    # # Sets up a fresh game state
    grid_h, grid_w = 20, 12
    canvas_w = 32 * (grid_w + 8)
    canvas_h = 32 * grid_h
    stddraw.setCanvasSize(canvas_w, canvas_h)
    stddraw.setXscale(-0.5, grid_w + 7.5)
    stddraw.setYscale(-0.5, grid_h - 0.5)

    Tetromino.grid_height = grid_h
    Tetromino.grid_width = grid_w

    grid = GameGrid(grid_h, grid_w)
    current_tetromino = create_tetromino()
    next_tetromino = create_tetromino()

    grid.current_tetromino = current_tetromino
    grid.next_tetromino = next_tetromino

    display_game_menu(grid_h, grid_w)

    return grid, current_tetromino, next_tetromino

def draw_pause_menu(grid_w, grid_h):
    # # Displays a pause menu with resume and quit options
    stddraw.clear()
    
    box_width = 8
    box_height = 8
    center_x = (grid_w + 7.5) / 2
    center_y = (grid_h - 0.5) / 2

    stddraw.setPenColor(Color(50, 50, 50))
    stddraw.filledRectangle(center_x - box_width/2, center_y - box_height/2, box_width, box_height)

    stddraw.setPenColor(Color(255, 255, 255))
    stddraw.setFontFamily("Arial")
    stddraw.setFontSize(20)

    stddraw.text(center_x, center_y + 2.5, "Press 'p' to Pause")
    stddraw.text(center_x, center_y, "Press 'r' to Resume")
    stddraw.text(center_x, center_y - 2.5, "Press 'q' to Quit")

    stddraw.show(10)

    while True:
        stddraw.show(10)
        if stddraw.hasNextKeyTyped():
            key = stddraw.nextKeyTyped()
            if key == 'r':
                return "resume"
            elif key == 'q':
                return "quit"

def create_tetromino():
    # # Randomly creates and returns a new Tetromino
    tetromino_types = ['I', 'O', 'Z', 'T', 'J', 'L', 'S']
    random_index = random.randint(0, len(tetromino_types) - 1)
    random_type = tetromino_types[random_index]
    return Tetromino(random_type)

def display_game_menu(grid_height, grid_width):
    # # Displays the start menu screen with a button to start
    background_color = Color(42, 69, 99)
    button_color = Color(25, 255, 228)
    text_color = Color(31, 160, 239)
    stddraw.clear(background_color)

    current_dir = os.path.dirname(os.path.realpath(__file__))
    img_file = current_dir + "/images/menu_image.png"
    img_center_x, img_center_y = (grid_width + 6.5) / 2, grid_height - 8
    image_to_display = Picture(img_file)
    stddraw.picture(image_to_display, img_center_x, img_center_y)

    button_w, button_h = grid_width - 1.5, 2
    button_blc_x, button_blc_y = img_center_x - button_w / 2, 4
    stddraw.setPenColor(button_color)
    stddraw.filledRectangle(button_blc_x, button_blc_y, button_w, button_h)

    stddraw.setFontFamily("Arial")
    stddraw.setFontSize(25)
    stddraw.setPenColor(text_color)
    stddraw.text(img_center_x, 5, "Click Here to Start the Game")
    stddraw.setFontSize(18)

    while True:
        stddraw.show(10)
        if stddraw.mousePressed():
            mouse_x = stddraw.mouseX()
            mouse_y = stddraw.mouseY()
            if button_blc_x <= mouse_x <= button_blc_x + button_w and button_blc_y <= mouse_y <= button_blc_y + button_h:
                break

def draw_score(score, grid_w, grid_h):
    # # Draws the current score on the side panel
    stddraw.setPenColor(Color(255, 255, 255))
    stddraw.setFontFamily("Arial")
    stddraw.setFontSize(16)
    stddraw.text(grid_w + 2, grid_h - 1, f"Score: {score}")

def draw_game_over_menu(score):
    # # Displays the Game Over screen with restart and quit options
    stddraw.clear()
    center_x = 12 / 2 + 3
    center_y = 20 / 2

    stddraw.setPenColor(Color(255, 0, 0))
    stddraw.setFontFamily("Arial")
    stddraw.setFontSize(40)
    stddraw.text(center_x, center_y + 4, "GAME OVER")

    stddraw.setPenColor(Color(255, 255, 255))
    stddraw.setFontSize(25)
    stddraw.text(center_x, center_y, f"Score: {score}")

    stddraw.setFontSize(20)
    stddraw.text(center_x, center_y - 3, "Press 'R' to Restart")
    stddraw.text(center_x, center_y - 5, "Press 'Q' to Quit")

    stddraw.show(10)

    while True:
        stddraw.show(10)
        if stddraw.hasNextKeyTyped():
            key = stddraw.nextKeyTyped()
            if key == 'r':
                start()
                return
            elif key == 'q':
                sys.exit()

# # Program entry point
if __name__ == '__main__':
    start()
