from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List, Optional, Any
import textwrap
from typing import Union
from Array2D import Array2D

class Color:
    is_ansicolor: bool
    ansi_value: str

    # Union[ANSIColor, RGBColor]
    def __init__(self, color: Union['ANSIColor', 'RGBColor', int]):
        if isinstance(color, int):
            self.is_ansicolor = True
            self.ansi_value = f"{color}"
        elif isinstance(color, ANSIColor):
            self.is_ansicolor = True
            self.ansi_value = f"{color.value}"
        elif isinstance(color, RGBColor):
            self.is_ansicolor = False
            self.ansi_value = f"2;{color.red};{color.green};{color.blue}"
        else:
            raise ValueError(f"Invalid color type: {color}")

    def ansi_fg(self) -> str:
        if self.is_ansicolor:
            return f"\033[3{self.ansi_value}m"
        return f"\033[38;{self.ansi_value}m"

    def ansi_bg(self) -> str:
        if self.is_ansicolor:
            return f"\033[4{self.ansi_value}m"

        return f"\033[48;{self.ansi_value}m"
class ANSIColor(Enum):
    black = 0
    red = 1
    green = 2
    yellow = 3
    blue = 4
    magenta = 5
    cyan = 6
    white = 7
    default = 9

    @staticmethod
    def from_str(color: str) -> 'ANSIColor':
        if color == "black":
            return ANSIColor.black
        if color == "red":
            return ANSIColor.red
        if color == "green":
            return ANSIColor.green
        if color == "yellow":
            return ANSIColor.yellow
        if color == "blue":
            return ANSIColor.blue
        if color == "magenta":
            return ANSIColor.magenta
        if color == "cyan":
            return ANSIColor.cyan
        if color == "white":
            return ANSIColor.white
        if color == "default":
            return ANSIColor.default
        raise ValueError(f"Invalid color: {color}")
class RGBColor:
    def __init__(self, red: int, green: int, blue: int):
        self.red = red
        self.green = green
        self.blue = blue

    def __str__(self) -> str:
        return f"RGBColor({self.red}, {self.green}, {self.blue})"

    def __repr__(self) -> str:
        return f"RGBColor({self.red}, {self.green}, {self.blue})"

@dataclass
class CellProperties:
    foreground_color: Color = Color(ANSIColor.default)
    background_color: Color = Color(ANSIColor.default)
    underlined: bool = False
    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    inverse: bool = False
    invisible: bool = False
    blink: bool = False

    def render(self) -> str:
        rendered_properties = []

        def append_effect(v: int) -> None:
            rendered_properties.append(f"\033[{v}m")

        if self.underlined:
            append_effect(4)
        if self.bold:
            append_effect(1)
        if self.italic:
            append_effect(3)
        if self.strikethrough:
            append_effect(9)
        if self.inverse:
            append_effect(7)
        if self.invisible:
            append_effect(8)
        if self.blink:
            append_effect(5)

        rendered_properties.append(self.foreground_color.ansi_fg())
        rendered_properties.append(self.background_color.ansi_bg())

        return f"{''.join(rendered_properties)}"

    def copy(self, **kwargs) -> "CellProperties":
        return CellProperties(
            foreground_color=kwargs.get("foreground_color", self.foreground_color),
            background_color=kwargs.get("background_color", self.background_color),
            underlined=kwargs.get("underlined", self.underlined),
            bold=kwargs.get("bold", self.bold),
            italic=kwargs.get("italic", self.italic),
            strikethrough=kwargs.get("strikethrough", self.strikethrough),
            inverse=kwargs.get("inverse", self.inverse),
            invisible=kwargs.get("invisible", self.invisible),
            blink=kwargs.get("blink", self.blink),
        )

    @staticmethod
    def default() -> "CellProperties":
        return CellProperties()

@dataclass
class Cell:
    # Cell is a single unit of a cell field. It has a character and a set of properties.
    character: str
    properties: CellProperties = field(default_factory=CellProperties)

    def render(self) -> str:
        # Render the cell with its properties
        # [ properties rendered() ] character [ reset ]
        return f"{self.properties.render()}{self.character}\033[0m"

    def bold(self) -> "Cell":
        return Cell(self.character, self.properties.copy(bold=True))

    def italic(self) -> "Cell":
        return Cell(self.character, self.properties.copy(italic=True))

    def underline(self) -> "Cell":
        return Cell(self.character, self.properties.copy(underlined=True))

    def strikethrough(self) -> "Cell":
        return Cell(self.character, self.properties.copy(strikethrough=True))

    def inverse(self) -> "Cell":
        return Cell(self.character, self.properties.copy(inverse=True))

    def invisible(self) -> "Cell":
        return Cell(self.character, self.properties.copy(invisible=True))

    def blink(self) -> "Cell":
        return Cell(self.character, self.properties.copy(blink=True))

    def fg_color(self, color: Color) -> "Cell":
        return Cell(self.character, self.properties.copy(foreground_color=color))

    def bg_color(self, color: Color) -> "Cell":
        return Cell(self.character, self.properties.copy(background_color=color))

@dataclass
class CellField:
    width: int
    height: int
    field : Optional[Array2D] = None

    def __post_init__(self):
        self.field = Array2D(self.height, self.width)
        self.field.fill(Cell(" "))

    def render(self) -> str:
        if self.field is None:
            return ""

        # Render the field
        rendered_field = ""
        for y in range(self.height):
            for x in range(self.width):
                rendered_field += self.field.at(x, y).render()
            rendered_field += "\n"
        return rendered_field

    def set(self, x: int, y: int, cell: Cell) -> "CellField":
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return self

        if self.field is None:
            return self

        # Set a cell in the field
        self.field.set_at(x, y, cell)
        return self

    def get(self, x: int, y: int) -> Cell:
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return Cell(" ")

        if self.field is None:
            return Cell(" ")

        # Get a cell from the field
        return self.field.at(x, y)

    # border of sets the border to the result of a callable function that takes in x and y coordinates
    def apply_border(self, border_func: Callable[['CellField', int, int], Cell]) -> "CellField":
        # Set the border of the field to the result of a function
        for y in range(self.height):
            for x in range(self.width):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    self.set(x, y, border_func(self, x, y))
        return self

    def apply_effect(self, effect_func: Callable[['CellField'], None]) -> "CellField":
        # Apply an effect to the field
        effect_func(self)
        return self
