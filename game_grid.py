import lib.stddraw as stddraw
from lib.color import Color
from point import Point
import numpy as np
import time
import os
import pygame.mixer

class GameGrid:
    def __init__(self, grid_h, grid_w):
        self.grid_height = grid_h
        self.grid_width = grid_w
        self.tile_matrix = np.full((grid_h, grid_w), None)
        self.current_tetromino = None
        self.next_tetromino = None
        self.game_over = False
        self.empty_cell_color = Color(245, 245, 220)
        self.line_color = Color(0, 100, 200)
        self.boundary_color = Color(0, 100, 200)
        self.line_thickness = 0.001
        self.box_thickness = 10 * self.line_thickness
        self.score = 0
        
        # Animation properties
        self.merge_animation_duration = 0.15
        self.merge_flash_color = Color(255, 255, 255)  # White flash
        self.animation_active = False
        
        # Initialize sound mixer
        pygame.mixer.init()
        try:
            self.merge_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), "sounds", "merge.wav"))
        except:
            print("Warning: Could not load merge sound effect")
            self.merge_sound = None

    def display(self):
        stddraw.clear(Color(250, 248, 239))
        
        # Draw grid background
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                stddraw.setPenColor(self.empty_cell_color)
                stddraw.filledSquare(col, row, 0.5)

        self.draw_grid()

        if self.current_tetromino is not None:
            self.current_tetromino.draw()

        # Draw side panel
        
        panel_x = self.grid_width + 1
        stddraw.setPenColor(Color(0, 0, 0))
        stddraw.setFontSize(20)
        stddraw.text(panel_x + 1, self.grid_height -2, "Next Piece:")
        stddraw.text(panel_x + 1, self.grid_height - 9, "Score:")
        stddraw.setFontSize(16)

        # Draw next tetromino
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
        stddraw.setFontSize(20)

        self.draw_boundaries()
        stddraw.setFontSize(31)
        stddraw.text(panel_x + 2.5, self.grid_height - 10.5, str(self.score))
        stddraw.setFontSize(20)
        stddraw.setPenColor(Color(0, 0, 0))
        stddraw.text(panel_x + 1.5, self.grid_height - 13, "Controls:")

        stddraw.setPenColor(Color(0, 0, 0))
        stddraw.setFontSize(20)
        stddraw.text(panel_x + 1.5, self.grid_height - 14.5, "← → ↓ : Move")
        stddraw.text(panel_x + 1.5, self.grid_height - 15.5, "↑ : Rotate")
        stddraw.text(panel_x + 1.5, self.grid_height - 16.5, "Space : Drop")
        stddraw.text(panel_x + 1.5, self.grid_height - 17.5, "P : Pause")
        stddraw.text(panel_x + 1.5, self.grid_height - 18.5, " R : Resume")
        stddraw.text(panel_x + 1.5, self.grid_height - 19.5, "Q : Quit")

        # Faster refresh during animations
        refresh_time = 25 if self.animation_active else 250
        stddraw.show(refresh_time)

    def draw_grid(self):
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                if self.tile_matrix[row][col] is not None:
                    # Add scale effect during animation
                    scale = 1.1 if self.animation_active and hasattr(self, 'animating_tiles') and (row, col) in self.animating_tiles else 1.0
                    self.tile_matrix[row][col].draw(Point(col, row), scale)
        
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
        stddraw.setPenColor(self.boundary_color)
        stddraw.setPenRadius(self.box_thickness)
        stddraw.rectangle(-0.5, -0.5, self.grid_width, self.grid_height)
        stddraw.setPenRadius()

    def is_occupied(self, row, col):
        if not self.is_inside(row, col):
            return False
        return self.tile_matrix[row][col] is not None

    def is_inside(self, row, col):
        return 0 <= row < self.grid_height and 0 <= col < self.grid_width
    

    def clear_full_rows(self):
        rows_cleared = 0
        for row in range(self.grid_height):
            # Check if the row is full (no None values)
            if all(self.tile_matrix[row]):
                # Clear the row by setting all cells to None
                for col in range(self.grid_width):
                    self.tile_matrix[row][col] = None
                rows_cleared += 1
        
        # If any rows were cleared, apply gravity to tiles above
        if rows_cleared > 0:
            for _ in range(rows_cleared):
                # Move all tiles above down by one
                for row in range(self.grid_height - 1, 0, -1):
                    for col in range(self.grid_width):
                        if self.tile_matrix[row - 1][col] is not None:
                            self.tile_matrix[row][col] = self.tile_matrix[row - 1][col]
                            self.tile_matrix[row - 1][col] = None
                
                # Clear the top row
                for col in range(self.grid_width):
                    self.tile_matrix[0][col] = None
        
        return rows_cleared

    def update_grid(self, tiles_to_lock, blc_position):
        self.current_tetromino = None
        n_rows, n_cols = len(tiles_to_lock), len(tiles_to_lock[0])

        # Place all tiles first
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

        # Clear any full rows
        self.clear_full_rows()

        # Process merges and gravity until stable
        changed = True
        while changed:
            changed = False
            
            # Apply gravity
            if self.apply_gravity_all():
                changed = True
            
            # Apply merges
            if self.apply_merge_all():
                changed = True

         # 🌟 Buraya bu kontrolü ekliyoruz:
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
        changed = False
        
        # First, identify connected components (tiles that should move together)
        visited = set()
        components = []
        
        # Depth-first search to find connected components
        def find_connected(row, col, component):
            if (row, col) in visited or row < 0 or row >= self.grid_height or col < 0 or col >= self.grid_width:
                return
            if self.tile_matrix[row][col] is None:
                return
                
            visited.add((row, col))
            component.append((row, col))
            
            # Check horizontal neighbors only (don't include vertical connections)
            find_connected(row, col-1, component)  # left
            find_connected(row, col+1, component)  # right
        
        # Find all connected components
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                if self.tile_matrix[row][col] is not None and (row, col) not in visited:
                    component = []
                    find_connected(row, col, component)
                    components.append(component)
        
        # For each component, determine if it can fall
        for component in components:
            # Check if any tile in component is at bottom row or has a tile below it
            can_fall = True
            for row, col in component:
                if row == 0:
                    can_fall = False
                    break
                # Check if there's a tile below that's not part of this component
                if self.tile_matrix[row-1][col] is not None and (row-1, col) not in component:
                    can_fall = False
                    break
            
            # If component can fall, move it down by one row
            if can_fall:
                # Store the tiles
                tiles = {}
                for row, col in component:
                    tiles[(row, col)] = self.tile_matrix[row][col]
                    self.tile_matrix[row][col] = None
                
                # Place them one row down
                for (row, col), tile in tiles.items():
                    self.tile_matrix[row-1][col] = tile
                
                changed = True
        
        return changed

    def apply_merge_all(self):
        changed = False
        merge_positions = []  # Track positions of merges for animation
        
        for col in range(self.grid_width):
            row = 0
            while row < self.grid_height - 1:
                tile1 = self.tile_matrix[row][col]
                tile2 = self.tile_matrix[row + 1][col]
                
                if tile1 and tile2 and tile1.number == tile2.number:
                    # Store merge position for animation
                    merge_positions.append((row, col))
                    merge_positions.append((row + 1, col))
                    
                    # Merge tiles
                    tile1.number *= 2
                    self.score += tile1.number
                    tile1.set_colors()
                    self.tile_matrix[row + 1][col] = None
                    changed = True
                    row += 1  # Skip next row
                row += 1
        
        # Show merge animation if any merges occurred
        if merge_positions:
            self.show_merge_animation(merge_positions)
            # Play merge sound if available
            if self.merge_sound:
                self.merge_sound.play()
        
        return changed

    def show_merge_animation(self, positions):
        self.animation_active = True
        self.animating_tiles = positions
        
        # Flash effect - 3 stages
        for stage in range(3):
            # Alternate between flash color and original color
            for row, col in positions:
                if self.tile_matrix[row][col] is not None:
                    if stage % 2 == 0:
                        self.tile_matrix[row][col].background_color = self.merge_flash_color
                    else:
                        self.tile_matrix[row][col].set_colors()
            
            self.display()
            time.sleep(self.merge_animation_duration / 3)
        
        # Restore original state
        for row, col in positions:
            if self.tile_matrix[row][col] is not None:
                self.tile_matrix[row][col].set_colors()
        
        self.animation_active = False
        self.display()

    def display_game_over(self):
        center_x = self.grid_width / 2
        center_y = self.grid_height / 2
        
        stddraw.clear(Color(245, 245, 220))
        stddraw.setPenColor(Color(0, 0, 0))
        stddraw.setFontFamily("Arial")
        stddraw.setFontSize(30)
        stddraw.text(center_x, center_y + 0.8, "GAME OVER")
        
        stddraw.setFontSize(20)
        stddraw.text(center_x, center_y - 0.8, f"Score: {self.score}")
        
        # Add restart button
        button_w, button_h = 6, 2
        button_x, button_y = center_x - button_w/2, center_y - 3
        stddraw.setPenColor(Color(100, 200, 100))
        stddraw.filledRectangle(button_x, button_y, button_w, button_h)
        stddraw.setPenColor(Color(0, 0, 0))
        stddraw.text(center_x, button_y + button_h/2, "Restart")
        
        stddraw.show()
        
        # Wait for click to restart
        while True:
            if stddraw.mousePressed():
                mouse_x, mouse_y = stddraw.mouseX(), stddraw.mouseY()
                if (button_x <= mouse_x <= button_x + button_w and 
                    button_y <= mouse_y <= button_y + button_h):
                    return True  # Signal to restart
            time.sleep(0.05)