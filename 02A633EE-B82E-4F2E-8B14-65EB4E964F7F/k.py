import curses
import random

KEYS = {
    curses.KEY_UP: "up",
    curses.KEY_DOWN: "down",
    curses.KEY_LEFT: "left",
    curses.KEY_RIGHT: "right"
}

SIZE = 4


def init_board():
    board = [[0] * SIZE for _ in range(SIZE)]
    add_tile(board)
    add_tile(board)
    return board


def add_tile(board):
    empty = [(r, c) for r in range(SIZE) for c in range(SIZE) if board[r][c] == 0]
    if empty:
        r, c = random.choice(empty)
        board[r][c] = 2 if random.random() < 0.9 else 4


def compress(line):
    new = [i for i in line if i != 0]
    new += [0] * (SIZE - len(new))
    return new


def merge(line):
    for i in range(SIZE - 1):
        if line[i] != 0 and line[i] == line[i + 1]:
            line[i] *= 2
            line[i + 1] = 0
    return line


def move_left(board):
    changed = False
    new_board = []

    for r in range(SIZE):
        line = board[r]
        compressed = compress(line)
        merged = merge(compressed)
        final = compress(merged)

        if final != line:
            changed = True

        new_board.append(final)

    return new_board, changed


def move_right(board):
    reversed_board = [row[::-1] for row in board]
    moved, changed = move_left(reversed_board)
    moved = [row[::-1] for row in moved]
    return moved, changed


def transpose(board):
    return [list(row) for row in zip(*board)]


def move_up(board):
    t = transpose(board)
    moved, changed = move_left(t)
    return transpose(moved), changed


def move_down(board):
    t = transpose(board)
    moved, changed = move_right(t)
    return transpose(moved), changed


# ================= POPUP WINDOW ================= #
def popup(stdscr, title, message):
    h, w = stdscr.getmaxyx()

    win_h = 7
    win_w = max(len(message) + 6, len(title) + 6, 26)

    start_y = (h - win_h) // 2
    start_x = (w - win_w) // 2

    win = curses.newwin(win_h, win_w, start_y, start_x)
    win.box()

    win.addstr(1, 2, title)
    win.addstr(3, 2, message)
    win.addstr(5, win_w // 2 - 7, "[ y ]   [ n ]")

    win.refresh()

    while True:
        key = win.getch()
        if key in (ord('y'), ord('Y')):
            return True
        if key in (ord('n'), ord('N')):
            return False


# ================= DRAW GAME ================= #
def draw(stdscr, board):
    stdscr.clear()
    stdscr.addstr("==== 2048 (curses version) ====\n\n")

    for r in range(SIZE):
        for c in range(SIZE):
            v = board[r][c]
            if v == 0:
                stdscr.addstr("[    ] ")
            else:
                stdscr.addstr(f"[{str(v).center(4)}] ")
        stdscr.addstr("\n")

    stdscr.addstr("\nUse arrow keys to move. Press q to quit.\n")
    stdscr.refresh()


def has_moves(board):
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == 0:
                return True
            if r < SIZE - 1 and board[r][c] == board[r+1][c]:
                return True
            if c < SIZE - 1 and board[r][c] == board[r][c+1]:
                return True
    return False


def main(stdscr):
    curses.curs_set(0)
    board = init_board()
    draw(stdscr, board)

    while True:
        key = stdscr.getch()

        # ==== Show popup when pressing Q ====
        if key == ord('q'):
            confirm = popup(stdscr, "Exit?", "Yakin mau keluar?")
            if confirm:
                break
            else:
                draw(stdscr, board)
                continue

        if key not in KEYS:
            continue

        direction = KEYS[key]

        if direction == "left":
            board, changed = move_left(board)
        elif direction == "right":
            board, changed = move_right(board)
        elif direction == "up":
            board, changed = move_up(board)
        elif direction == "down":
            board, changed = move_down(board)

        if changed:
            add_tile(board)

        draw(stdscr, board)

        if not has_moves(board):
            stdscr.addstr("\nGAME OVER! Press any key to exit.")
            stdscr.refresh()
            stdscr.getch()
            break


if __name__ == "__main__":
    curses.wrapper(main)
