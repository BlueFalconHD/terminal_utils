

ESC = "\033"
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
UNDERLINED = "\033[4m"
BLINK = "\033[5m"
REVERSE = "\033[7m"
HIDDEN = "\033[8m"

# Foreground Colors
FG_BLACK = "\033[30m"
FG_RED = "\033[31m"
FG_GREEN = "\033[32m"
FG_YELLOW = "\033[33m"
FG_BLUE = "\033[34m"
FG_MAGENTA = "\033[35m"
FG_CYAN = "\033[36m"
FG_WHITE = "\033[37m"

# Background Colors
BG_BLACK = "\033[40m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN = "\033[46m"
BG_WHITE = "\033[47m"


def cursor_up(n=1):
    return f"\033[{n}A"


def cursor_down(n=1):
    return f"\033[{n}B"


def cursor_forward(n=1):
    return f"\033[{n}C"


def cursor_backward(n=1):
    return f"\033[{n}D"


def cursor_next_line(n=1):
    return f"\033[{n}E"


def cursor_prev_line(n=1):
    return


def cursor_beginning_of_line():
    return "\033[G"


def move_cursor_horizontal(n=1):
    if n == 0:
        return ""
    elif n < 0:
        return f"\033[{n}D"
    elif n > 0:
        return f"\033[{n}C"

def move_cursor_to_position_in_line(self, n=1):
    return f"\033[{n}G"


def cursor_position(row=1, col=1):
    return f"\033[{row};{col}H"


def clear_screen():
    return "\033[2J"


def clear_line():
    return "\033[2K"


def save_cursor_position():
    return "\033[s"


def restore_cursor_position():
    return "\033[u"


def set_fg_color(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"


def set_bg_color(r, g, b):
    return f"\033[48;2;{r};{g};{b}m"
