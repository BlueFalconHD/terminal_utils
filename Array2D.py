
from dataclasses import dataclass, field
from typing import Any, List

@dataclass
class Array2D:
    """
    # Array2D
    A 2D array data structure that allows for easy manipulation of 2D data. The array is represented as a list of lists, where each inner list represents a row in the array.

    Properties:

        (*) rows        The number of rows in the array.
                        @Type: int
                        @Required

        (*) cols        The number of columns in the array.
                        @Type: int
                        @Required

        (*) array       The 2D array represented as a list of lists.
                        @Type: List[List[Any]]
                        @Default: [[None for _ in range(cols)] for _ in range(rows)]

    Methods:

        (*) get         Get the value at a specific index in the array.
                        @Returns: Any [ typeof(array[row][col]) ]
                        @Params:
                            (*) index   The row and column index.
                                        @Type: Tuple[int, int]
                                        @Required

        (*) set         Set the value at a specific index in the array.
                        @Returns: None
                        @Params:
                            (*) index   The row and column index.
                                        @Type: Tuple[int, int]
                                        @Required

                            (*) value   The value to set.
                                        @Type: Any
                                        @Required

        (*) put_at_row  Place a list of values at a specific row in the array.
                        @Returns: None
                        @Params:
                            (*) row     The row index.
                                        @Type: int
                                        @Required

                            (*) index   The starting column index.
                                        @Type: int
                                        @Required

                            (*) data    The list of values to place.
                                        @Type: List[Any]
                                        @Required

        (*) put_at_col  Place a list of values at a specific column in the array.
                        @Returns: None
                        @Params:
                            (*) col     The column index.
                                        @Type: int
                                        @Required

                            (*) index   The starting row index.
                                        @Type: int
                                        @Required

                            (*) data    The list of values to place.
                                        @Type: List[Any]
                                        @Required

        (*) get_row     Get a specific row in the array.
                        @Returns: List[Any]
                        @Params:
                            (*) row     The row index.
                                        @Type: int
                                        @Required

        (*) set_row     Set a specific row in the array.
                        @Returns: None
                        @Params:
                            (*) row     The row index.
                                        @Type: int
                                        @Required

                            (*) data    The list of values to set.
                                        @Type: List[Any]
                                        @Required

        (*) get_col     Get a specific column in the array.
                        @Returns: List[Any]
                        @Params:
                            (*) col     The column index.
                                        @Type: int
                                        @Required


        (*) set_col     Set a specific column in the array.
                        @Returns: None
                        @Params:
                            (*) col     The column index.
                                        @Type: int
                                        @Required

                            (*) data    The list of values to set.
                                        @Type: List[Any]
                                        @Required

        (*) composite   Place a 2D array at a specific x,y coordinate in the array.
                        @Returns: None
                        @Params:
                            (*) other   The other 2D array to place.
                                        @Type: Array2D
                                        @Required

                            (*) index   The x,y coordinate to place the array.
                                        @Type: Tuple[int, int]
                                        @Required

        (*)


    """

    rows: int
    cols: int
    array: List[List[Any]] = field(init=False)

    def __post_init__(self):
        self.array = [[None for _ in range(self.cols)] for _ in range(self.rows)]

    def get(self, index):
        row, col = index
        return self.array[row][col]

    def set(self, index, value):
        row, col = index
        self.array[row][col] = value

    def at(self, x: int, y: int):
        return self.array[y][x]

    def set_at(self, x: int, y: int, value: Any):
        self.array[y][x] = value



    # Put at allows placing some list of values at some x,y coordinate. The list of items will be placed in the array starting from the x,y coordinate, if the overflow
    # option is set to True, the items will overflow the array and be placed in the next row or column starting from the beginning. If the overflow option is set to False
    # an error will be raised if the items overflow the array.
    def put_at_row(self, row: int, index: int, data: List[Any]):
        if len(data) + index > self.cols:
            raise ValueError("Data is too long for the row.")
        self.array[row][index:index+len(data)] = data

    # Same function as put_at_row, but for columns. Just use the transpose function to transpose the array and use put_at_row, then transpose back.
    def put_at_col(self, col: int, index: int, data: List[Any]):
        self.transpose()
        self.put_at_row(col, index, data)
        self.transpose()

    def composite(self, other: "Array2D", x: int, y: int):
        for row in range(other.rows):
            for col in range(other.cols):
                if row + y >= self.rows or col + x >= self.cols:
                    # Skip if the other array is out of bounds
                    continue

                self.array[row + y][col + x] = other.array[row][col]

    def subset(self, x: int, y: int, width: int, height: int):
        subset = Array2D(width, height)
        for row in range(height):
            for col in range(width):
                subset.array[row][col] = self.array[row + y][col + x]
        return subset

    def get_row(self, row: int) -> List[Any]:
        return self.array[row]

    def get_col(self, col: int) -> List[Any]:
        return [self.array[row][col] for row in range(self.rows)]

    def set_row(self, row: int, values: List[Any]):
        if len(values) != self.cols:
            raise ValueError("Length of values must match the number of columns.")
        self.array[row] = values

    def set_col(self, col: int, values: List[Any]):
        if len(values) != self.rows:
            raise ValueError("Length of values must match the number of rows.")
        for row in range(self.rows):
            self.array[row][col] = values[row]

    def transpose(self):
        transposed = [[self.array[row][col] for row in range(self.rows)] for col in range(self.cols)]
        self.array = transposed
        self.rows, self.cols = self.cols, self.rows

    def fill(self, value: Any):
        for row in range(self.rows):
            for col in range(self.cols):
                self.array[row][col] = value

    def display(self):
        for row in self.array:
            print(row)
