import lib.stddraw as stddraw  # used for drawing the tiles to display them
from lib.color import Color  # used for coloring the tiles

# A class for modeling numbered tiles as in 2048
class Tile:
   # Class variables shared among all Tile objects
   # ---------------------------------------------------------------------------
   # the value of the boundary thickness (for the boxes around the tiles)
   boundary_thickness = 0.004
   # font family and font size used for displaying the tile number
   font_family, font_size = "Arial", 14

   # A constructor that creates a tile with 2 as the number on it
   def __init__(self, number=2):
      # set the number on this tile
      self.number = number
      self.set_colors()
      
   def set_colors(self):
    color_map = {
        2: Color(173, 216, 230),    # soft blue
        4: Color(100, 149, 237),    # darker blue
        8: Color(144, 238, 144),    # soft green
        16: Color(60, 179, 113),    # green
        32: Color(255, 223, 0),     # yellow
        64: Color(255, 165, 0),     # orange
        128: Color(255, 99, 71),    # likely orange
        256: Color(255, 69, 0),     # bright red
        512: Color(255, 0, 0),      # red
        1024: Color(148, 0, 211),   # purple
        2048: Color(75, 0, 130)     # purple + dark blue
    }
    self.background_color = color_map.get(self.number, Color(60, 58, 50))
    self.foreground_color = Color(0, 0, 0)
    self.box_color = Color(50, 50, 50)


   # A method for drawing this tile at a given position with a given length
   def draw(self, position, length=1):
    #  everytime update colorss
    self.set_colors()

    # after draw
    stddraw.setPenColor(self.background_color)
    stddraw.filledSquare(position.x, position.y, length / 2)
    
    stddraw.setPenColor(self.box_color)
    stddraw.setPenRadius(Tile.boundary_thickness)
    stddraw.square(position.x, position.y, length / 2)
    stddraw.setPenRadius()

    stddraw.setPenColor(self.foreground_color)
    stddraw.setFontFamily(Tile.font_family)
    stddraw.setFontSize(Tile.font_size)
    stddraw.text(position.x, position.y, str(self.number))
