# Import necessary libraries
import lib.stddraw as stddraw  # # Used for drawing and displaying the game window
from lib.color import Color  # # Used for coloring tiles and background
from point import Point  # # Used for handling tile coordinate positions
import numpy as np  # # Used for handling tile matrices efficiently
import time  # # Used for controlling animation and timing
import os  # # Used for accessing file paths
import pygame.mixer  # # Used for playing sound effects (e.g., merge sound)

class GameGrid:
    def __init__(self, grid_h, grid_w):
        # # Initialize the game grid dimensions and essential variables
        self.grid_height = grid_h
        self.grid_width = grid_w
        self.tile_matrix = np.full((grid_h, grid_w), None)  # # Create a grid filled with None (empty)
        self.current_tetromino = None  # # Active tetromino currently falling
        self.next_tetromino = None  # # Next tetromino to be previewed
        self.game_over = False  # # Game over flag

        # # Visual appearance settings
        self.empty_cell_color = Color(245, 245, 220)  # # Background color for empty cells
        self.line_color = Color(0, 100, 200)  # # Grid line color
        self.boundary_color = Color(0, 100, 200)  # # Boundary box color
        self.line_thickness = 0.001  # # Thickness of grid lines
        self.box_thickness = 10 * self.line_thickness  # # Thickness of the boundary box
        self.score = 0  # # Initial score set to 0

        # # Animation settings
        self.merge_animation_duration = 0.15  # # Duration of merge animation (in seconds)
        self.merge_flash_color = Color(255, 255, 255)  # # Flash color for merging effect
        self.animation_active = False  # # Whether an animation is currently active

        # # Initialize sound effects
        pygame.mixer.init()
        try:
            self.merge_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), "sounds", "merge.wav"))
        except:
            print("Warning: Could not load merge sound effect")
            self.merge_sound = None

    def display(self):
        # # Draws the entire game screen including the grid, side panel, and active tetromino
        stddraw.clear(Color(250, 248, 239))  # # Clear the screen with background color

        # # Draw empty tiles (background)
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                stddraw.setPenColor(self.empty_cell_color)
                stddraw.filledSquare(col, row, 0.5)

        # # Draw locked tiles and current tetromino
        self.draw_grid()

        if self.current_tetromino is not None:
            self.current_tetromino.draw()

        # # Draw side panel for next piece preview and score
        panel_x = self.grid_width + 1
        stddraw.setPenColor(Color(0, 0, 0))
        stddraw.setFontSize(20)
        stddraw.text(panel_x + 1, self.grid_height - 2, "Next Piece:")
        stddraw.text(panel_x + 1, self.grid_height - 9, "Score:")
        stddraw.setFontSize(16)

        # # Draw next tetromino preview
        if self.next_tetromino is not None:
            n = len(self.next_tetromino.tile_matrix)
            offset_x = self.grid_width + 2.5
            offset_y = self.grid_height - 4
            for row in range(n):
                for col in range(n):
                    tile = self.next_tetromino.tile_matrix[row][col]
                    if tile is not None:
                        pos = Point(offset_x + col, offset_y - row)
                        tile.draw(pos)

        # # Draw the score
        stddraw.setFontSize(31)
        stddraw.text(panel_x + 2.5, self.grid_height - 10.5, str(self.score))

        # # Display control instructions
        stddraw.setFontSize(20)
        stddraw.text(panel_x + 1.5, self.grid_height - 13, "Controls:")
        stddraw.text(panel_x + 1.5, self.grid_height - 14.5, "← → ↓ : Move")
        stddraw.text(panel_x + 1.5, self.grid_height - 15.5, "↑ : Rotate")
        stddraw.text(panel_x + 1.5, self.grid_height - 16.5, "Space : Drop")
        stddraw.text(panel_x + 1.5, self.grid_height - 17.5, "P : Pause")
        stddraw.text(panel_x + 1.5, self.grid_height - 18.5, "R : Resume")
        stddraw.text(panel_x + 1.5, self.grid_height - 19.5, "Q : Quit")

        # # Update the screen (faster if animation is ongoing)
        refresh_time = 25 if self.animation_active else 250
        stddraw.show(refresh_time)

    def draw_grid(self):
        # # Draws all locked tiles and the grid lines
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                if self.tile_matrix[row][col] is not None:
                    scale = 1.1 if self.animation_active and hasattr(self, 'animating_tiles') and (row, col) in self.animating_tiles else 1.0
                    self.tile_matrix[row][col].draw(Point(col, row), scale)

        # # Draw grid lines
        stddraw.setPenColor(self.line_color)
        stddraw.setPenRadius(self.line_thickness)
        start_x, end_x = -0.5, self.grid_width - 0.5
        start_y, end_y = -0.5, self.grid_height - 0.5
        for x in np.arange(start_x + 1, end_x, 1):
            stddraw.line(x, start_y, x, end_y)
        for y in np.arange(start_y + 1, end_y, 1):
            stddraw.line(start_x, y, end_x, y)
        stddraw.setPenRadius()

    def draw_boundaries(self):
        # # Draws an outer boundary around the grid
        stddraw.setPenColor(self.boundary_color)
        stddraw.setPenRadius(self.box_thickness)
        stddraw.rectangle(-0.5, -0.5, self.grid_width, self.grid_height)
        stddraw.setPenRadius()

    def is_occupied(self, row, col):
        # # Returns True if the specified cell is occupied by a tile
        if not self.is_inside(row, col):
            return False
        return self.tile_matrix[row][col] is not None

    def is_inside(self, row, col):
        # # Returns True if the given (row, col) is within the grid
        return 0 <= row < self.grid_height and 0 <= col < self.grid_width

    def clear_full_rows(self):
        # # Clears any fully occupied rows and shifts above rows downward
        rows_cleared = 0
        for row in range(self.grid_height):
            if all(self.tile_matrix[row]):
                for col in range(self.grid_width):
                    self.tile_matrix[row][col] = None
                rows_cleared += 1

        if rows_cleared > 0:
            for _ in range(rows_cleared):
                for row in range(self.grid_height - 1, 0, -1):
                    for col in range(self.grid_width):
                        if self.tile_matrix[row - 1][col] is not None:
                            self.tile_matrix[row][col] = self.tile_matrix[row - 1][col]
                            self.tile_matrix[row - 1][col] = None
                for col in range(self.grid_width):
                    self.tile_matrix[0][col] = None

        return rows_cleared

    def update_grid(self, tiles_to_lock, blc_position):
        # # Locks a placed tetromino into the grid and handles gravity and merges
        self.current_tetromino = None
        n_rows, n_cols = len(tiles_to_lock), len(tiles_to_lock[0])

        for col in range(n_cols):
            for row in range(n_rows):
                if tiles_to_lock[row][col] is not None:
                    pos = Point()
                    pos.x = blc_position.x + col
                    pos.y = blc_position.y + (n_rows - 1) - row

                    if pos.y >= self.grid_height:
                        self.game_over = True
                        return True

                    if self.is_inside(pos.y, pos.x):
                        self.tile_matrix[pos.y][pos.x] = tiles_to_lock[row][col]
                    else:
                        self.game_over = True
                        return True

        self.clear_full_rows()

        changed = True
        while changed:
            changed = False
            if self.apply_gravity_all():
                changed = True
            if self.apply_merge_all():
                changed = True

        for col in range(self.grid_width):
            full = True
            for row in range(self.grid_height):
                if self.tile_matrix[row][col] is None:
                    full = False
                    break
            if full:
                self.game_over = True
                return True

        return self.game_over

    def apply_gravity_all(self):
        # # Applies gravity to all connected tiles that can fall downward
        changed = False
        visited = set()
        components = []

        def find_connected(row, col, component):
            if (row, col) in visited or row < 0 or row >= self.grid_height or col < 0 or col >= self.grid_width:
                return
            if self.tile_matrix[row][col] is None:
                return
            visited.add((row, col))
            component.append((row, col))
            find_connected(row, col-1, component)
            find_connected(row, col+1, component)

        for row in range(self.grid_height):
            for col in range(self.grid_width):
                if self.tile_matrix[row][col] is not None and (row, col) not in visited:
                    component = []
                    find_connected(row, col, component)
                    components.append(component)

        for component in components:
            can_fall = True
            for row, col in component:
                if row == 0 or (self.tile_matrix[row-1][col] is not None and (row-1, col) not in component):
                    can_fall = False
                    break
            if can_fall:
                tiles = {}
                for row, col in component:
                    tiles[(row, col)] = self.tile_matrix[row][col]
                    self.tile_matrix[row][col] = None
                for (row, col), tile in tiles.items():
                    self.tile_matrix[row-1][col] = tile
                changed = True

        return changed

    def apply_merge_all(self):
        # # Merges vertically adjacent tiles with the same number
        changed = False
        merge_positions = []

        for col in range(self.grid_width):
            row = 0
            while row < self.grid_height - 1:
                tile1 = self.tile_matrix[row][col]
                tile2 = self.tile_matrix[row + 1][col]

                if tile1 and tile2 and tile1.number == tile2.number:
                    merge_positions.append((row, col))
                    merge_positions.append((row + 1, col))
                    tile1.number *= 2
                    self.score += tile1.number
                    tile1.set_colors()
                    self.tile_matrix[row + 1][col] = None
                    changed = True
                    row += 1
                row += 1

        if merge_positions:
            self.show_merge_animation(merge_positions)
            if self.merge_sound:
                self.merge_sound.play()

        return changed

    def show_merge_animation(self, positions):
        # # Shows flashing animation when tiles merge
        self.animation_active = True
        self.animating_tiles = positions

        for stage in range(3):
            for row, col in positions:
                if self.tile_matrix[row][col] is not None:
                    if stage % 2 == 0:
                        self.tile_matrix[row][col].background_color = self.merge_flash_color
                    else:
                        self.tile_matrix[row][col].set_colors()
            self.display()
            time.sleep(self.merge_animation_duration / 3)

        for row, col in positions:
            if self.tile_matrix[row][col] is not None:
                self.tile_matrix[row][col].set_colors()

        self.animation_active = False
        self.display()

    def display_game_over(self):
        # # Displays the Game Over screen with the option to restart
        center_x = self.grid_width / 2
        center_y = self.grid_height / 2

        stddraw.clear(Color(245, 245, 220))
        stddraw.setPenColor(Color(0, 0, 0))
        stddraw.setFontFamily("Arial")
        stddraw.setFontSize(30)
        stddraw.text(center_x, center_y + 0.8, "GAME OVER")

        stddraw.setFontSize(20)
        stddraw.text(center_x, center_y - 0.8, f"Score: {self.score}")

        button_w, button_h = 6, 2
        button_x, button_y = center_x - button_w/2, center_y - 3
        stddraw.setPenColor(Color(100, 200, 100))
        stddraw.filledRectangle(button_x, button_y, button_w, button_h)
        stddraw.setPenColor(Color(0, 0, 0))
        stddraw.text(center_x, button_y + button_h/2, "Restart")

        stddraw.show()

        while True:
            if stddraw.mousePressed():
                mouse_x, mouse_y = stddraw.mouseX(), stddraw.mouseY()
                if (button_x <= mouse_x <= button_x + button_w and button_y <= mouse_y <= button_y + button_h):
                    return True
            time.sleep(0.05)
