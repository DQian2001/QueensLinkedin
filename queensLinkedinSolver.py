import curses
import numpy as np
import sys

class Board:
   crossedOutSymbol = -1

   def __init__( self, board, currWorkingRow=0 ):
      self.board = board
      self.currWorkingRow = currWorkingRow

   def autoPlaceX( self, board, location ):
      i, j = location
      currLetter = board[ i, j ]

      # Remove all instances of the same letter/color.
      board[ board == currLetter ] = Board.crossedOutSymbol

      # Remove neighbors.
      maxI = max( i - 1, 0 )
      maxJ = max( j - 1, 0 )
      board[ maxI : i + 2, maxJ : j + 2 ] = Board.crossedOutSymbol

      # Remove current row.
      board[ i, : ] = Board.crossedOutSymbol

      # Remove current column.
      board[ :, j ] = Board.crossedOutSymbol

      # Replace the previously deleted currLetter.
      board[ i, j ] = currLetter

   def solve( self ):
      color_dim = np.max( self.board ) + 1
      stack = [ self ]
      while stack:
         bd = stack.pop()
         i = bd.currWorkingRow
         # print( "CURRENT BOARD IS:" )
         # print( str( bd.board ).replace( '-1', ' *' ) )
         # print( '-' * 34 )
         # print( "currently working on row", i )
         noGoodChildBoards = True
         for j in range( bd.board.shape[ 1 ] - 1, -1, -1 ):
            if bd.board[ i, j ] == Board.crossedOutSymbol:
               continue
            board = bd.board.copy()
            self.autoPlaceX( board, ( i, j ) )
            # print( str( board ).replace( '-1', ' *' ) )
            # Auto-place X's for each letter that only appears once.
            isSolved = True
            for letter in range( color_dim ):
               if np.count_nonzero( board == letter ) == 1:
                  x, y = np.where( board == letter )
                  self.autoPlaceX( board, next( zip( x, y ) ) )
               else:
                  isSolved = False
            if isSolved:
               print( "FOUND SOLUTION!!!" )
               return board
            isValidBoard = True
            for letter in range( color_dim ):
               if not np.count_nonzero( board == letter ):
                  isValidBoard = False
                  break
            if isValidBoard and i != board.shape[ 0 ] - 1:
               noGoodChildBoards = False
               stack.append( Board( board, currWorkingRow=i + 1 ) )
               # print( "good BOARD" )
            else:
               # print( "bad board" )
               pass

         if noGoodChildBoards and i != board.shape[ 0 ] - 1:
            # print( "NO GOOD CHILD BOARDS TODAY" )
            stack.append( Board( bd.board.copy(), currWorkingRow=i + 1 ) )
         else:
            # print( "FOUND SOME GOOD CHILDS" )
            pass

def main():
   grid_dim = input( "Enter array length/width" ).strip()
   if not grid_dim.isnumeric():
      return
   inputArr = curses.wrapper( getInputArr, int( grid_dim ) )
   currBoard = Board( inputArr )
   finalBoard = currBoard.solve()
   print( str( finalBoard ).replace( '-1', ' *' ) )

def getInputArr( stdscr, grid_dim ):
   curses.curs_set( 0 )
   stdscr.clear()

   # 1. Enable ALL mouse events and motion reporting
   curses.mousemask( curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION )
   curses.mouseinterval( 0 )

   # 2. FORCE terminal emulator into high-frequency event reporting mode
   sys.stdout.write( "\x1b[?1003h" )
   sys.stdout.flush()

   curses.start_color()

   # Setup color palettes
   MENU_COLORS = [
      "Black",
      "Red",
      "Orange",
      "Yellow",
      "Green",
      "Cyan",
      "Blue",
      "Purple",
      "Pink",
      "Brown",
      "Gray",
      "White",
   ]
   menu_dim = len( MENU_COLORS )
   text_color = menu_dim
   curses.init_pair( 1, curses.COLOR_RED, curses.COLOR_RED )
   # Orange
   curses.init_pair( 2, 208, 208 )
   curses.init_pair( 3, curses.COLOR_YELLOW, curses.COLOR_YELLOW )
   curses.init_pair( 4, curses.COLOR_GREEN, curses.COLOR_GREEN )
   curses.init_pair( 5, curses.COLOR_CYAN, curses.COLOR_CYAN )
   curses.init_pair( 6, curses.COLOR_BLUE, curses.COLOR_BLUE )
   # Purple
   curses.init_pair( 7, 129, 129 )
   # Pink
   curses.init_pair( 8, 13, 13 )
   # Brown
   curses.init_pair( 9, 94, 94 )
   # Gray
   curses.init_pair( 10, 244, 244 )
   curses.init_pair( 11, curses.COLOR_WHITE, curses.COLOR_WHITE )
   curses.init_pair( text_color, curses.COLOR_WHITE, curses.COLOR_BLACK )

   CELL_WIDTH = 5
   CELL_HEIGHT = 2

   # Initialize canvas grid to white color (last color in MENU).
   array_2d = np.ones( ( grid_dim, grid_dim ), dtype=int ) * ( menu_dim - 1 )

   active_color_pair = 0
   MENU_X_START = ( grid_dim * CELL_WIDTH ) + 4
   is_drawing = False

   # pylint: disable=too-many-nested-blocks
   while True:
      stdscr.clear()

      # Get the CURRENT live dimensions of the terminal window
      max_y, max_x = stdscr.getmaxyx()

      # Calculate minimum size requirements to fit the UI safely
      needed_width = MENU_X_START + 17
      needed_height = max( ( max( menu_dim, grid_dim ) * CELL_HEIGHT ) + 3, 20 )

      # SAFEGUARD: If screen is too cramped, show warning and wait for resize
      if max_x < needed_width or max_y < needed_height:
         try:
            stdscr.addstr(
               0, 0, "⚠️ SCREEN TOO SMALL!",
               curses.color_pair( text_color ) | curses.A_BOLD
            )
            stdscr.addstr(
               1, 0, "Please expand your window to at least " +
               f"{needed_width}x{needed_height}.", curses.color_pair( text_color )
            )
            stdscr.addstr(
               2, 0, f"Current size: {max_x}x{max_y}",
               curses.color_pair( text_color )
            )
         except curses.error:
            pass  # absolute fallback if the window is truly microscopic

         stdscr.refresh()
         key = stdscr.getch()
         if key == ord( 'q' ):
            return np.unique( array_2d, return_inverse=True )[ 1 ]
         continue  # Skip rendering the grid until they resize it larger

      # 1. DRAW GRID (Safe inside boundaries)
      for r in range( grid_dim ):
         for c in range( grid_dim ):
            color_attr = curses.color_pair( int( array_2d[ r, c ] ) )
            for h in range( CELL_HEIGHT ):
               stdscr.addstr(
                  r * CELL_HEIGHT + h, c * CELL_WIDTH, ' ' * CELL_WIDTH, color_attr
               )

      # 2. DRAW SIDEBAR
      stdscr.addstr( 0, MENU_X_START, "COLOR PICKER" )
      stdscr.addstr( 1, MENU_X_START, "------------" )

      slotYStart = lambda idx: 2 * idx + 3
      for idx, info in enumerate( MENU_COLORS ):
         y_pos = slotYStart( idx )
         swatch_attr = curses.color_pair( idx )
         stdscr.addstr( y_pos, MENU_X_START, "    ", swatch_attr )
         stdscr.addstr( y_pos + 1, MENU_X_START, "    ", swatch_attr )
         is_active = ( idx == active_color_pair )
         label = f" {info}" + ( " <--" if is_active else "" )
         text_style = curses.color_pair(
            text_color
         ) | curses.A_REVERSE if is_active else curses.color_pair( text_color )
         stdscr.addstr( y_pos, MENU_X_START + 6, label, text_style )

      stdscr.addstr( ( grid_dim * CELL_HEIGHT ) + 1, 0, "Press 'q' to quit.",
         curses.color_pair( text_color ) )
      stdscr.refresh()

      # 3. MOUSE & KEYBOARD INPUT
      key = stdscr.getch()

      if key == ord( 'q' ):
         # Clean up: Tell terminal to turn OFF
         # high-frequency mouse tracking before exiting
         sys.stdout.write( "\x1b[?1003l" )
         sys.stdout.flush()
         return np.unique( array_2d, return_inverse=True )[ 1 ]

      if key == ord( '\t' ):
         # Increment selection, then use modulo to
         # wrap back to 0 if it goes past the end.
         active_color_pair = ( active_color_pair + 1 ) % menu_dim
         continue
      if key == curses.KEY_BTAB:
         # Decrement selection, then use modulo to
         # wrap back to end if it goes past 0.
         active_color_pair = ( active_color_pair - 1 ) % menu_dim

      if key == curses.KEY_MOUSE:
         try:
            _, mx, my, _, bstate = curses.getmouse()
            clicked_col = mx // CELL_WIDTH
            clicked_row = my // CELL_HEIGHT
            insideGrid = 0 <= clicked_row < grid_dim and 0 <= clicked_col < grid_dim
            if bstate & curses.BUTTON1_PRESSED:
               is_drawing = insideGrid
               # Select a sidebar option to change the active color.
               if mx >= MENU_X_START:
                  for idx, info in enumerate( MENU_COLORS ):
                     slot_y_start = slotYStart( idx )
                     if slot_y_start <= my <= slot_y_start + 1:
                        active_color_pair = idx
                        break
            elif bstate & curses.BUTTON1_RELEASED:
               is_drawing = False
            if is_drawing and insideGrid:
               array_2d[ clicked_row, clicked_col ] = active_color_pair
               continue
         except curses.error:
            pass

if __name__ == "__main__":
   main()
