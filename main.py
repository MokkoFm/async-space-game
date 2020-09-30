import time
import curses
import asyncio
import random
from itertools import cycle


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, symbol='*'):
  min_time_to_blink = 10
  max_time_to_blink = 50
  while True:
      for star in range(random.randint(min_time_to_blink, max_time_to_blink)):
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

      for star in range(random.randint(min_time_to_blink, max_time_to_blink)):
        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

      for star in range(random.randint(min_time_to_blink, max_time_to_blink)):
        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

      for star in range(random.randint(min_time_to_blink, max_time_to_blink)):
        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.refresh()
    rows = canvas.getmaxyx()[0] - 1
    columns = canvas.getmaxyx()[1] - 1
    symbols = ['+', '*', '.', ':']
    coroutines = [blink(canvas, random.randint(1, rows), random.randint(1, columns), random.choice(symbols)) for _ in range(100)]
    coroutines.append(fire(canvas, start_row=20, start_column=30, rows_speed=-0.3, columns_speed=0))
    coroutines.append(animate_spaceship(canvas, start_row = 20, start_column=30))

    while True:      
      for coroutine in coroutines:
        try:
          coroutine.send(None)
          canvas.refresh()
        except StopIteration:
          coroutines.remove(coroutine)
      
      if len(coroutines) == 0:
        break


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""
    
    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break
                
            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


async def animate_spaceship(canvas, start_row, start_column):
    files = [file_1, file_2]
    iterator = cycle(files)

    draw_frame(canvas, 20, 20, file_1)
    canvas.refresh()
    time.sleep(1)
    # стираем предыдущий кадр, прежде чем рисовать новый
    draw_frame(canvas, 20, 20, file_1, negative=True)
    canvas.refresh()
    draw_frame(canvas, 20, 20, file_2)
    canvas.refresh()
    draw_frame(canvas, 20, 20, file_2, negative=True)
    time.sleep(1)
    canvas.refresh()

  
if __name__ == '__main__':
    rocket_1 = open("rocket_frame_1.txt", "r", encoding='utf-8')
    file_1 = rocket_1.read()
    rocket_2 = open("rocket_frame_2.txt", "r", encoding='utf-8')
    file_2 = rocket_2.read()
    curses.update_lines_cols()  
    curses.wrapper(draw)