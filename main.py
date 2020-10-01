import time
import curses
import asyncio
import random
from itertools import cycle

SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


def read_controls(canvas):
    """Read keys pressed and returns tuple witl controls state."""

    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


async def fire(canvas, start_row, start_column,
               rows_speed=-0.3, columns_speed=0):
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
        for star in range(
          random.randint(min_time_to_blink, max_time_to_blink)):
            canvas.addstr(row, column, symbol, curses.A_DIM)
            await asyncio.sleep(0)

        for star in range(
          random.randint(min_time_to_blink, max_time_to_blink)):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)

        for star in range(
          random.randint(min_time_to_blink, max_time_to_blink)):
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            await asyncio.sleep(0)

        for star in range(
          random.randint(min_time_to_blink, max_time_to_blink)):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.refresh()
    canvas.nodelay(True)
    rows = canvas.getmaxyx()[0] - 1
    columns = canvas.getmaxyx()[1] - 1
    symbols = ['+', '*', '.', ':']
    coroutines = [blink(canvas, random.randint(1, rows), random.randint(
        1, columns), random.choice(symbols)) for _ in range(100)]
    coroutines.append(fire(canvas, rows / 2, columns / 2 +
                           2, rows_speed=-0.5, columns_speed=0))
    coroutines.append(animate_spaceship(canvas, rows, columns))

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

            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


async def animate_spaceship(canvas, rows, columns):
    frames = [frame_1, frame_2]
    spaceship_speed = 5
    start_row, start_column = rows / 2, columns / 2
    max_row = rows - spaceship_speed
    max_column = columns - spaceship_speed

    for frame in cycle(frames):
        draw_frame(canvas, start_row, start_column, frame_1)
        canvas.refresh()
        time.sleep(0.1)
        await asyncio.sleep(0)

        draw_frame(canvas, start_row, start_column, frame_1, negative=True)
        canvas.refresh()
        await asyncio.sleep(0)

        draw_frame(canvas, start_row, start_column, frame_2)
        canvas.refresh()
        await asyncio.sleep(0)

        draw_frame(canvas, start_row, start_column, frame_2, negative=True)
        time.sleep(0.1)
        canvas.refresh()
        await asyncio.sleep(0)

        rows_direction, columns_direction, space_pressed = read_controls(
            canvas)

        if spaceship_speed < start_row < max_row:
            if rows_direction == -1:
                start_row -= spaceship_speed
            elif rows_direction == 1:
                start_row += spaceship_speed
        elif start_row <= spaceship_speed:
            if rows_direction == 1:
                start_row += spaceship_speed
        elif start_row >= max_row:
            if rows_direction == -1:
                start_row -= spaceship_speed

        if spaceship_speed < start_column < max_column:
            if columns_direction == -1:
                start_column -= spaceship_speed
            if columns_direction == 1:
                start_column += spaceship_speed
        elif start_column <= spaceship_speed:
            if columns_direction == 1:
                start_column += spaceship_speed
        elif start_column >= max_row:
            start_column -= spaceship_speed


if __name__ == '__main__':
    rocket_1 = open("rocket_frame_1.txt", "r", encoding='utf-8')
    frame_1 = rocket_1.read()
    rocket_2 = open("rocket_frame_2.txt", "r", encoding='utf-8')
    frame_2 = rocket_2.read()
    curses.update_lines_cols()
    curses.wrapper(draw)
