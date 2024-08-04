from dataclasses import dataclass
from enum import Enum
from typing import List


class WrappingBehaviour(Enum):
    WORD = 0
    HARD = 1
    HYPHENATE = 2
    TRUNCATE = 3
    TRUNCATE_WITH_ELLIPSIS = 4

@dataclass
class TextWrapping:
    method: WrappingBehaviour
    width: int

    def wrap(self, text: str) -> List[str]:
        if self.method == WrappingBehaviour.WORD:
            return self.word_wrap(text)
        elif self.method == WrappingBehaviour.HARD:
            return self.hard_wrap(text)
        elif self.method == WrappingBehaviour.HYPHENATE:
            return self.hyphenate_wrap(text)
        elif self.method == WrappingBehaviour.TRUNCATE:
            return self.truncate_wrap(text)
        elif self.method == WrappingBehaviour.TRUNCATE_WITH_ELLIPSIS:
            return self.truncate_with_ellipsis_wrap(text)
        else:
            raise ValueError(f"Invalid wrapping method: {self.method}")

    def word_wrap(self, text: str) -> List[str]:
        # Algorithm:
            # Split the text into words
            # Initialize a list of lines
            # Initialize a current line string
            # For each word:
                # If adding the word to the current line would exceed the width:
                    # Add the current line to the list of lines
                    # Start a new current line with the word
                    # Continue
                # Otherwise:
                    # Add the word to the current line
                    # Continue

            # Add the last current line to the list of lines

        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) > self.width:
                lines.append(current_line)
                current_line = word
            else:
                if current_line:
                    current_line += " "
                current_line += word

        lines.append(current_line)

        return lines

    def hard_wrap(self, text: str) -> List[str]:
        # Algorithm:
            # Initialize a list of lines
            # Initialize a current line string
            # For each character in the text:
                # If adding the character to the current line would exceed the width:
                    # Add the current line to the list of lines
                    # Start a new current line with the character
                    # Continue
                # Otherwise:
                    # Add the character to the current line
                    # Continue
            # Add the last current line to the list of lines
            # Return the list of lines

        lines = []
        current_line = ""

        for char in text:
            if len(current_line) + 1 > self.width:
                lines.append(current_line)
                current_line = char
            else:
                current_line += char

        lines.append(current_line)

        return lines

    def hyphenate_wrap(self, text: str) -> List[str]:
        # Algorithm:
            # Split the text into words
            # Initialize a list of lines
            # Initialize a current line string
            # For each word:
                # If adding the word to the current line would exceed the width - 1:
                    # Add a hyphen to the current line
                    # Add the current line to the list of lines
                    # Start a new current line with the word
                    # Continue
                # Otherwise:
                    # Add the word to the current line
                    # Continue

            # Add the last current line to the list of lines
            # Return the list of lines

        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 > self.width:
                current_line += "-"
                lines.append(current_line)
                current_line = word
            else:
                if current_line:
                    current_line += " "
                current_line += word

        lines.append(current_line)

        return lines

    def truncate_wrap(self, text: str) -> List[str]:
        # Algorithm:
            # Initialize a list of lines
            # Initialize a current line string
            # For each line (.split("\n")) in the text:
                # If the line is longer than the width:
                    # Truncate the line to the width
                    # Continue
                # Add the line to the list of lines
                # Continue
            # Return the list of lines

        lines = []
        current_line = ""

        for line in text.split("\n"):
            if len(line) > self.width:
                line = line[:self.width]
            lines.append(line)

        return lines

    def truncate_with_ellipsis_wrap(self, text: str) -> List[str]:
        # Algorithm:
            # Initialize a list of lines
            # Initialize a current line string
            # For each line (.split("\n")) in the text:
                # If the line is longer than the width:
                    # Truncate the line to the width - 3
                    # Add "..." to the line
                    # Continue
                # Add the line to the list of lines
                # Continue
            # Return the list of lines

        lines = []
        current_line = ""

        for line in text.split("\n"):
            if len(line) > self.width:
                line = line[:self.width - 3] + "..."
            lines.append(line)

        return lines
