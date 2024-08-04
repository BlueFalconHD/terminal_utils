from typing_extensions import Callable
from CellField import CellField, Cell, Color, ANSIColor, RGBColor, CellProperties
from typing import List, Tuple, Union, Optional
from enum import Enum
from dataclasses import dataclass, field
import math

from TextWrapping import WrappingBehaviour, TextWrapping

class View2DFlowDirection(Enum):
    ROWS = 0
    COLUMNS = 1
class View2DAlignment(Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2
class View2DSizing(Enum):
    FIXED = 0
    FILL = 1
    AUTO = 2
class View2DJustification(Enum):
    START = 0
    CENTER = 1
    END = 2

@dataclass
class View2DSize():
    type: View2DSizing
    value: int

    @staticmethod
    def fixed(value: int) -> 'View2DSize':
        return View2DSize(View2DSizing.FIXED, value)

    @staticmethod
    def fill() -> 'View2DSize':
        return View2DSize(View2DSizing.FILL, 0)

    @staticmethod
    def auto() -> 'View2DSize':
        return View2DSize(View2DSizing.AUTO, 0)

@dataclass
class View2D:
    children: Optional[List['View2D']] = None
    direction: View2DFlowDirection = View2DFlowDirection.ROWS

    alignment: View2DAlignment = View2DAlignment.LEFT
    justification: View2DJustification = View2DJustification.START
    spacing: int = 0

    width: View2DSize = field(default_factory=View2DSize.auto)
    height: View2DSize = field(default_factory=View2DSize.auto)

    debug_bg: bool = False

    def render(self, parent_callback: Optional[Callable] = None) -> CellField:
        # Render the view
        # Render each child and place them below each other
        rendered_children = []
        if self.children is None:
            return CellField(0, 0)


        # Depending on the direction, we will render the children in a different way
        #  case ROWS:
        #   Render each child and place them below each other
        #   The width of the Field will be the maximum width of the children, and the height will be the sum of the heights of the children
        #  case COLUMNS:
        #   Render each child and place them next to each other
        #   The width of the Field will be the sum of the widths of the children, and the height will be the maximum height of the children
        #  case _:
        #   Raise an exception

        sum_width = sum(child.width for child in rendered_children) + self.spacing * (len(rendered_children) - 1)
        max_height = max(child.height for child in rendered_children)
        sum_height = sum(child.height for child in rendered_children) + self.spacing * (len(rendered_children) - 1)
        max_width = max(child.width for child in rendered_children)

        # SIZING
        if self.width.type == View2DSizing.FIXED:
            max_width = self.width.value

        if self.height.type == View2DSizing.FIXED:
            sum_height = self.height.value

        if self.width.type == View2DSizing.FILL:

            if parent_callback is not None:
                max_width = parent_callback().width

                self.width = View2DSize.fixed(max_width)
            else:
                raise Exception("Cannot fill width without parent callback")

        if self.height.type == View2DSizing.FILL:
            if parent_callback is not None:
                sum_height = parent_callback().height

                self.height = View2DSize.fixed(sum_height)
            else:
                raise Exception("Cannot fill height without parent callback")

        def pcallback():
            return {
                "width": max_width,
                "height": sum_height
            }

        for child in self.children:
            rendered_children.append(child.render(parent_callback=pcallback))

        if self.direction == View2DFlowDirection.ROWS:
            field = CellField(max_width, sum_height)

            if self.justification == View2DJustification.CENTER:
                current_y = math.floor((sum_height - sum_height) / 2)
            elif self.justification == View2DJustification.END:
                # currently identity, when different padding is added, this will be updated
                current_y = sum_height - sum_height
            else:
                current_y = 0

            for child in rendered_children:
                if field.field is None:
                    continue

                # If the alignment is CENTER, we need to center the child in the field horizontally
                # We can do this by calculating the x position of the child
                # The x position will be the center of the field minus the half of the width of the child
                # If the alignment is RIGHT, we need to right align the child
                # The x position will be the width of the field minus the width of the child

                if self.alignment == View2DAlignment.CENTER:
                    current_x = math.floor((max_width - child.width) / 2)
                elif self.alignment == View2DAlignment.RIGHT:
                    current_x = max_width - child.width
                else:
                    current_x = 0

                field.field.composite(child.field, current_x, current_y)
                current_y += child.height
                current_y += self.spacing

            return field

        elif self.direction == View2DFlowDirection.COLUMNS:
            field = CellField(sum_width, max_height)

            if self.justification == View2DJustification.CENTER:
                current_x = math.floor((sum_width - sum_width) / 2)
            elif self.justification == View2DJustification.END:
                # currently identity, when different padding is added, this will be updated
                current_x = sum_width - sum_width
            else:
                current_x = 0

            for child in rendered_children:
                if field.field is None:
                    continue

                if self.alignment == View2DAlignment.CENTER:
                    current_y = math.floor((max_height - child.height) / 2)
                elif self.alignment == View2DAlignment.RIGHT:
                    current_y = max_height - child.height
                else:
                    current_y = 0

                field.field.composite(child.field, current_x, current_y)
                current_x += child.width
                current_x += self.spacing

            self.debug(field)

            return field

        else:
            raise ValueError("Invalid direction")

    def debug(self, f: CellField):
        if self.debug_bg and f.field is not None:

            # fill any cells that are None with a " "
            for y in range(f.height):
                for x in range(f.width):
                    if f.get(x, y) is None:
                        f.set(x, y, Cell(character=" "))

            for y in range(f.height):
                for x in range(f.width):
                    f.set(x, y, f.get(x, y).bg_color(Color(ANSIColor.red)))

@dataclass
class PaddedView2D(View2D):
    padding: int = 0

    def render(self, parent_callback: Optional[Callable] = None) -> CellField:

        if self.children is None:
                    return CellField(0, 0)

        if len(self.children) != 1:
            raise ValueError("PaddedView2D must have exactly one child")

        if self.children[0] is None:
            return CellField(0, 0)

        def pcallback():
            return {
                "width": self.children[0].width,
                "height": self.children[0].height
            }

        # Render the child
        child_field = self.children[0].render(parent_callback=pcallback)

        # Create a new field with the padding
        field = CellField(child_field.width + self.padding * 2, child_field.height + self.padding * 2)

        if field.field is None:
            return field

        if child_field.field is None:
            return field

        # Composite the child field into the new field
        field.field.composite(child_field.field, self.padding, self.padding)

        return field

@dataclass
class PrimitiveTextView2D(View2D):
    text: str = ""

    def render(self, parent_callback: Optional[Callable] = None) -> CellField:
        # Create a field with the text
        field = CellField(len(self.text), 1)

        if field.field is None:
            return field

        for i, c in enumerate(self.text):
            field.set(i, 0, Cell(character=c))

        return field

@dataclass
class TextView2D(View2D):
    text: str = ""
    wrap: WrappingBehaviour = WrappingBehaviour.WORD

    def render(self, parent_callback: Optional[Callable] = None) -> CellField:
        split_lines_max_width = max(len(line) for line in self.text.split("\n"))
        max_width = self.width.value

        if self.width.type == View2DSizing.AUTO:
            max_width = split_lines_max_width
        elif self.width.type == View2DSizing.FILL:
            if parent_callback is None:
                raise ValueError("Parent callback must be provided when using FILL sizing, but none was provided")
            max_width = parent_callback().width

        wrapper = TextWrapping(self.wrap, max_width)
        wrapped_text = wrapper.wrap(self.text)

        # Create a view2d that stacks a textview2d for each line
        children = [PrimitiveTextView2D(text=line) for line in wrapped_text]

        print(children)

        # ignore this error, TextView2D is a subclass of View2D, so it should be fine
        stack = View2D(children=children, direction=View2DFlowDirection.ROWS, alignment=View2DAlignment.LEFT, spacing=0)

        # Render the stack
        return stack.render()

@dataclass
class BorderedView2D(View2D):
    padding: int = 0
    border_color: Color = Color(ANSIColor.white)
    content: Optional[View2D] = None

    def render(self, parent_callback: Optional[Callable] = None) -> CellField:
        if self.content is None:
            return CellField(0, 0)


        content_field = self.content.render()
        border_field = CellField(content_field.width + self.padding * 2, content_field.height + self.padding * 2)

        # Custom border function that will draw a border around the field
        def border(f: CellField, x: int, y: int) -> Cell:
            c: Optional[Cell] = None

            # Draw the border using box drawing characters
            if x == 0 and y == 0:
                c = Cell(character='┌')
            elif x == 0 and y == f.height - 1:
                c = Cell(character='└')
            elif x == f.width - 1 and y == 0:
                c = Cell(character='┐')
            elif x == f.width - 1 and y == f.height - 1:
                c = Cell(character='┘')
            elif x == 0 or x == f.width - 1:
                c = Cell(character='│')
            elif y == 0 or y == f.height - 1:
                c = Cell(character='─')

            if c is not None:
                c = c.fg_color(self.border_color)
                return c
            else:
                return Cell(" ")

        border_field.apply_border(border)

        if content_field.field is None:
            return border_field

        if border_field.field is None:
            return border_field


        self.debug(border_field)

        # Composite the content onto the border
        border_field.field.composite(content_field.field, self.padding, self.padding)


        return border_field

@dataclass
class SpacerView2D(View2D):
    def render(self, parent_callback: Optional[Callable] = None) -> CellField:
        c = CellField(self.width.value, self.height.value)


        self.debug(c)

        return c

# @dataclass
# class WrappingView2D(View2D):
#     item_spacing: int = 0  # New property for item spacing
#     def render(self) -> CellField:
#         if self.width.type != View2DSizing.FIXED:
#             raise ValueError("WrappingView2D requires a fixed width")

#         max_width = self.width.value
#         lines = []
#         current_line = []
#         current_width = 0

#         if self.children is None:
#             return CellField(max_width, 0)

#         # Wrapping algorithm with item spacing
#         for child in self.children:
#             child_field = child.render()
#             child_width = child_field.width + (self.item_spacing if current_line else 0)

#             if current_width + child_width > max_width:
#                 lines.append(current_line)
#                 current_line = [child_field]
#                 current_width = child_field.width
#             else:
#                 if current_line:
#                     current_width += self.item_spacing
#                 current_line.append(child_field)
#                 current_width += child_field.width

#         if current_line:
#             lines.append(current_line)

#         # Calculate height
#         total_height = sum(max(child.height for child in line) for line in lines)
#         if self.spacing > 0:
#             total_height += self.spacing * (len(lines) - 1)

#         # Create the CellField
#         field = CellField(max_width, total_height)
#         current_y = 0

#         for line in lines:
#             line_height = max(child.height for child in line)
#             current_x = 0

#             if self.alignment == View2DAlignment.CENTER:
#                 current_x = (max_width - sum(child.width for child in line) - self.item_spacing * (len(line) - 1)) // 2
#             elif self.alignment == View2DAlignment.RIGHT:
#                 current_x = max_width - sum(child.width for child in line) - self.item_spacing * (len(line) - 1)

#             for child in line:
#                 if field.field is None:
#                     continue

#                 field.field.composite(child.field, current_x, current_y)
#                 current_x += child.width + self.item_spacing

#             current_y += line_height
#             current_y += self.spacing

#         self.debug(field)

#         return field

# class WordWrappingBehavior(Enum):
#     HARD = 1
#     WORD = 2

# @dataclass
# class WrappingTextView2D(WrappingView2D):
#     # For the wrappingtextview, we split text into seperate textviews based on
#     # the wrapping behavior defined

#     wrap: WordWrappingBehavior = WordWrappingBehavior.HARD
#     text: str = ""

#     def render(self) -> CellField:
#         if self.wrap == WordWrappingBehavior.HARD:
#             return self.render_hard_wrap()
#         elif self.wrap == WordWrappingBehavior.WORD:
#             return self.render_word_wrap()
#         else:
#             raise ValueError("Invalid wrapping behavior")

#     def render_hard_wrap(self) -> CellField:
#         # Split the text into seperate TextViews when the width of the text
#         # exceeds the width of the view

#         lines = []
#         current_line = ""
#         current_width = 0

#         # Add current line to the list of lines when the length of current line exceeds the width
#         for c in self.text:
#             if c == "\n":
#                 lines.append(current_line)
#                 current_line = ""
#                 current_width = 0
#             else:
#                 current_line += c
#                 current_width += 1

#                 if current_width >= self.width.value:
#                     lines.append(current_line)
#                     current_line = ""
#                     current_width = 0

#         if current_line:
#             lines.append(current_line)

#         # Set children to the list of TextViews
#         self.children = [TextView2D(text=line) for line in lines]
#         return super().render()

#     def render_word_wrap(self) -> CellField:
#         # All we do for word wrap is split the text into words and then set the children
#         # to the list of TextViews, also we set spacing to 1 to simulate word wrapping
#         words = self.text.split(" ")
#         self.children = [TextView2D(text=word) for word in words]
#         self.item_spacing = 1
#         return super().render()



def test_view2d():
    # Example structure:
    # <BorderedView2D Border Color: Blue, Padding: 1>
    #   <BorderedView2D Border Color: White, Padding: 2>
    #       <WrappingView2D Width: 20>
    #           <TextView2D "Hello">
    #           <TextView2D "World">
    #           <TextView2D "This">
    #           <TextView2D "is">
    #           <TextView2D "a">
    #           <TextView2D "test">
    #           <TextView2D "of">
    #           <TextView2D "WrappingView2D">
    #           <TextView2D "with">
    #           <TextView2D "multiple">
    #           <TextView2D "children">
    #       </WrappingView2D>
    #       <View2D Direction: ROWS>
    #           <TextView2D "Below">
    #           <TextView2D "WrappingView2D">
    #           <View2D Direction: COLUMNS, Spacing: 2>
    #               <TextView2D "A">
    #               <TextView2D "B">
    #               <TextView2D "C">
    #           </View2D>
    #       </View2D>
    #   </BorderedView2D>
    # </BorderedView2D>

    view = BorderedView2D(
        padding=1,
        border_color=Color(ANSIColor.blue),
        content=BorderedView2D(
            padding=2,
            border_color=Color(ANSIColor.white),
            content=View2D(
                direction=View2DFlowDirection.ROWS,
                alignment=View2DAlignment.CENTER,
                justification=View2DJustification.CENTER,
                spacing=1,
                children=[
                    TextView2D(
                        wrap=WrappingBehaviour.WORD,
                        width=View2DSize.fixed(10),
                        text="Hello World This is a test of TextView2D with wrapping enabled"
                    ),
                    SpacerView2D(height=View2DSize.fixed(1), debug_bg=True),
                    View2D(
                        debug_bg=True,
                        direction=View2DFlowDirection.ROWS,
                        children=[
                            TextView2D(text="Below"),
                            TextView2D(text="WrappingView2D"),
                            SpacerView2D(height=View2DSize.fixed(1)),
                            View2D(
                                width=View2DSize.fill(),
                                debug_bg=True,
                                direction=View2DFlowDirection.COLUMNS,
                                spacing=2,
                                children=[
                                    TextView2D(text="A"),
                                    TextView2D(text="B"),
                                    TextView2D(text="C")
                                ]
                            )
                        ]
                    )
                ]
            )
        )
    )

    field = view.render()
    print(field.render())

if __name__ == "__main__":
    test_view2d()
