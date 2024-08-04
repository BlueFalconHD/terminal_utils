
from CtrlCodes import FG_BLACK, FG_RED, FG_GREEN, FG_YELLOW, FG_BLUE, FG_MAGENTA, FG_CYAN, FG_WHITE, RESET
from enum import Enum, auto

class Color(Enum):
    black = 0
    red = 1
    green = 2
    yellow = 3
    blue = 4
    magenta = 5
    cyan = 6
    white = 7
    default = 9

class FrameStyle(Enum):
    none = auto()
    light = auto()
    heavy = auto()
    double = auto()
    dashed = auto()
    rounded = auto()

LINE_CHARACTERS = {
    FrameStyle.light: {
        "top_left": "\u250C",
        "top_right": "\u2510",
        "bottom_left": "\u2514",
        "bottom_right": "\u2518",
        "vertical": "\u2502",
        "horizontal": "\u2500",
    },
    FrameStyle.heavy: {
        "top_left": "\u250F",
        "top_right": "\u2513",
        "bottom_left": "\u2517",
        "bottom_right": "\u251B",
        "vertical": "\u2503",
        "horizontal": "\u2501",
    },
    FrameStyle.double: {
        "top_left": "\u2554",
        "top_right": "\u2557",
        "bottom_left": "\u255A",
        "bottom_right": "\u255D",
        "vertical": "\u2551",
        "horizontal": "\u2550",
    },
    FrameStyle.dashed: {
        "top_left": "\u250C",
        "top_right": "\u2510",
        "bottom_left": "\u2514",
        "bottom_right": "\u2518",
        "vertical": "\u254E",
        "horizontal": "\u254C",
    },
    FrameStyle.rounded: {
        "top_left": "\u256D",
        "top_right": "\u256E",
        "bottom_left": "\u2570",
        "bottom_right": "\u256F",
        "vertical": "\u2502",
        "horizontal": "\u2500",
    },
}

def colorcode_for_color(c: Color):
    return {
        Color.black: FG_BLACK,
        Color.red: FG_RED,
        Color.green: FG_GREEN,
        Color.yellow: FG_YELLOW,
        Color.blue: FG_BLUE,
        Color.magenta: FG_MAGENTA,
        Color.cyan: FG_CYAN,
        Color.white: FG_WHITE,
        Color.default: RESET
    }[c]

def colored_text(text: str, color: Color):
    return colorcode_for_color(color) + text + colorcode_for_color(Color.default)


def render_frame(style: FrameStyle, width: int, height: int, color: Color = Color.default):
    lines = LINE_CHARACTERS[style]
    print(colored_text(lines["top_left"] + lines["horizontal"] * (width - 2) + lines["top_right"], color))
    for _ in range(height - 2):
        print(colored_text(lines["vertical"] + " " * (width - 2) + lines["vertical"], color))
    print(colored_text(lines["bottom_left"] + lines["horizontal"] * (width - 2) + lines["bottom_right"], color))
