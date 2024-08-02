from dataclasses import dataclass
import re
from typing import Dict, Any
from enum import Enum, auto

# MARK: Constants
ESCAPE_CHAR_RAW = '\x1b'
ESCAPE_SEQUENCE = "<esc>"
extra_key_map = {
    0x7f: "<backspace>",
    0x09: "<tab>"
}

# MARK: Enums
class IOEscape(Enum):
    NONE = auto()
    CHAR = auto()
    ESC = auto()
    ALT_KEYPRESS = auto()
    ALT_BRACKET = auto()
    KEYCODE_SEQUENCE = auto()
    INCOMPLETE = auto()

class IOTerminalStandard(Enum):
    XTERM = auto()
    VT = auto()
    UNKNOWN = auto()

# MARK: Classes
@dataclass
class IOModifiers:
    SHIFT: bool = False
    ALT: bool = False
    CTRL: bool = False
    META: bool = False

@dataclass
class IOKeycode:
    """
    # IOKeycode
    @dataclass

    This class is used to represent a keypress event, and contains all the necessary information to process the keypress.

    Parameters:

        (*) keycode                 Keycode of the keypress
                                    @Type: int

        (*) keycode_char            Character representation of the keycode
                                    @Type: str

        (*) modifier                Modifiers applied to the keypress
                                    @Type: IOModifiers

        (*) terminal                Terminal type
                                    @Type: IOTerminalStandard (Enum)

        (*) escape_type             Escape type of the keypress
                                    @Type: IOEscape (Enum)

        (*) has_modifier_extra      Whether the keypress has a modifier extra
                                    @Type: bool

        (*) escape_sequence         Escape sequence of the keypress
                                    @Type: str

        (*) vt_sequences            Dictionary of VT sequences
                                    @Type: Dict[str, str]

        (*) xterm_sequences         Dictionary of XTERM sequences
                                    @Type: Dict[str, str]

        (*) was_terminated          Whether the raw keycode was terminated
                                    @Type: bool

    Methods:

        (*) is_special              Check if the keypress is a special
                                    key (not a character)
                                    @return bool

        (*) is_char                 Opposite of is_special
                                    @return bool

        (*) is_escape               Check if the keypress is any escape sequence
                                    @return bool

        (*) resolve_friendly_name   Resolve the friendly name of the keypress
                                    @return str

    """


    keycode: int
    keycode_char: str
    modifier: IOModifiers
    terminal: IOTerminalStandard
    escape_type: IOEscape
    has_modifier_extra: bool
    escape_sequence: str
    terminated: bool

    # Initialize human readable key based on escape sequence
    # List partially from https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
    def __post_init__(self):
        self.vt_sequences = {
            self.escape_sequence + "[1~": "Home",
            self.escape_sequence + "[2~": "Insert",
            self.escape_sequence + "[3~": "Delete",
            self.escape_sequence + "[4~": "End",
            self.escape_sequence + "[5~": "PgUp",
            self.escape_sequence + "[6~": "PgDn",
            self.escape_sequence + "[7~": "Home",
            self.escape_sequence + "[8~": "End",
            self.escape_sequence + "[9~": "",
            self.escape_sequence + "[10~": "F0",
            self.escape_sequence + "[11~": "F1",
            self.escape_sequence + "[12~": "F2",
            self.escape_sequence + "[13~": "F3",
            self.escape_sequence + "[14~": "F4",
            self.escape_sequence + "[15~": "F5",
            self.escape_sequence + "[16~": "",
            self.escape_sequence + "[17~": "F6",
            self.escape_sequence + "[18~": "F7",
            self.escape_sequence + "[19~": "F8",
            self.escape_sequence + "[20~": "F9",
            self.escape_sequence + "[21~": "F10",
            self.escape_sequence + "[22~": "",
            self.escape_sequence + "[23~": "F11",
            self.escape_sequence + "[24~": "F12",
            self.escape_sequence + "[25~": "F13",
            self.escape_sequence + "[26~": "F14",
            self.escape_sequence + "[27~": "",
            self.escape_sequence + "[28~": "F15",
            self.escape_sequence + "[29~": "F16",
            self.escape_sequence + "[30~": "",
            self.escape_sequence + "[31~": "F17",
            self.escape_sequence + "[32~": "F18",
            self.escape_sequence + "[33~": "F19",
            self.escape_sequence + "[34~": "F20",
            self.escape_sequence + "[35~": ""
        }

        self.xterm_sequences = {
            self.escape_sequence + "[A": "Up",
            self.escape_sequence + "[B": "Down",
            self.escape_sequence + "[C": "Right",
            self.escape_sequence + "[D": "Left",
            self.escape_sequence + "[E": "",
            self.escape_sequence + "[F": "End",
            self.escape_sequence + "[G": "Keypad 5",
            self.escape_sequence + "[H": "Home",
            self.escape_sequence + "[I": "",
            self.escape_sequence + "[J": "",
            self.escape_sequence + "[K": "",
            self.escape_sequence + "[L": "",
            self.escape_sequence + "[M": "",
            self.escape_sequence + "[N": "",
            self.escape_sequence + "[O": "",
            self.escape_sequence + "[1P": "F1",
            self.escape_sequence + "[1Q": "F2",
            self.escape_sequence + "[1R": "F3",
            self.escape_sequence + "[1S": "F4",
            self.escape_sequence + "[T": "",
            self.escape_sequence + "[U": "",
            self.escape_sequence + "[V": "",
            self.escape_sequence + "[W": "",
            self.escape_sequence + "[X": "",
            self.escape_sequence + "[Y": "",
            self.escape_sequence + "[Z": ""
        }

    def is_special(self) -> bool:
        """
        # is_special

        Check if the keypress is a special key (not a character)
        """
        return self.escape_type != IOEscape.CHAR and self.escape_type != IOEscape.NONE

    def is_char(self) -> bool:
        return self.escape_type == IOEscape.CHAR

    def is_escape(self) -> bool:
        return self.escape_type in {IOEscape.ESC, IOEscape.ALT_KEYPRESS, IOEscape.ALT_BRACKET, IOEscape.KEYCODE_SEQUENCE}

    def is_possibly_incomplete(self) -> bool:
        # IOEscape.ALT_BRACKET or IOEscape.INCOMPLETE or IOEscape.ESC
        return self.escape_type in {IOEscape.ALT_BRACKET, IOEscape.INCOMPLETE, IOEscape.ESC}

    def resolve_friendly_name(self, include_modifiers: bool = True) -> str:
        modifier_names = []
        if self.modifier.SHIFT:
            modifier_names.append("Shift+")
        if self.modifier.ALT:
            modifier_names.append("Alt+")
        if self.modifier.CTRL:
            modifier_names.append("Ctrl+")
        if self.modifier.META:
            modifier_names.append("Meta+")

        key_name = ""
        if self.terminal == IOTerminalStandard.VT:
            key_name = self.vt_sequences.get(f"{self.escape_sequence}[{self.keycode_char}~", "")
        elif self.terminal == IOTerminalStandard.XTERM:
            key_name = self.xterm_sequences.get(f"{self.escape_sequence}[{self.keycode_char}", "")

        if not key_name:
            key_name = self.keycode_char

        if include_modifiers:
            return f"{"".join(modifier_names)}{key_name}"

        return f"{key_name}"

    def __repr__(self) -> str:
        return f"""
        IOKeycode(
            escape_sequence = {self.escape_sequence},
            escape_type = {self.escape_type},
            terminal = {self.terminal},
            modifier = {self.modifier},
            keycode_char = {self.keycode_char}
            terminated = {self.terminated}
        )
        """

    def __str__(self) -> str:
        return self.__repr__()

# MARK: Functions
def parse_keycode(input: str, escape_sequence = "<esc>") -> IOKeycode:
    """
    # parse_keycode(input: str, escape_sequence: str = "<esc>") -> IOKeycode
    Parse a keycode from a string input.

    Parameters:

        (*) input:              The input string to parse
                                the keycode from.

                                @Type str;
                                @Required;

        (*) escape_sequence:    The escape sequence to use to
                                replace the escape character
                                in the input string.

                                @Default str("<esc>");
                                @Type str;

    Return Value:

        (*) The parsed IOKeycode object
            @Type IOKeycode

    Credits:

        (*) Logic used to parse the input
            https://en.wikipedia.org/wiki/ANSI_escape_code#Terminal_input_sequences
    """


    escape_len = len(escape_sequence)

    was_terminated = False

    if not input:
        return IOKeycode(-1, "", IOModifiers(), IOTerminalStandard.UNKNOWN, IOEscape.NONE, False, escape_sequence, was_terminated)

    if input.startswith(escape_sequence):

        if len(input) == escape_len or input[escape_len:escape_len + escape_len] == escape_sequence:
            was_terminated = True
            return IOKeycode(-1, "", IOModifiers(), IOTerminalStandard.UNKNOWN, IOEscape.ESC, False, escape_sequence, was_terminated)

        if input[escape_len] == '[':
            if len(input) == escape_len + 1:
                was_terminated = True
                return IOKeycode(-1, "", IOModifiers(), IOTerminalStandard.UNKNOWN, IOEscape.ALT_BRACKET, False, escape_sequence, was_terminated)

            if input.endswith('~'):
                was_terminated = True

                match = re.match(re.escape(escape_sequence) + r'\[(\d+)(?:;(\d+))?~', input)
                if match:
                    keycode = int(match.group(1))
                    modifier = int(match.group(2)) if match.group(2) else 1
                    has_modifier_extra = bool(match.group(2))
                    modifiers = calculate_modifier(modifier)
                    return IOKeycode(keycode, str(keycode), modifiers, IOTerminalStandard.VT, IOEscape.KEYCODE_SEQUENCE, has_modifier_extra, escape_sequence, was_terminated)

            else:
                match = re.match(re.escape(escape_sequence) + r'\[(\d+)?([a-zA-Z])', input)

                if match:
                    modifier = int(match.group(1)) if match.group(1) else 1
                    char = match.group(2)
                    if char != None:
                        was_terminated = True
                    modifiers = calculate_modifier(modifier)
                    has_modifier_extra = bool(match.group(1))
                    return IOKeycode(-1, char, modifiers, IOTerminalStandard.XTERM, IOEscape.KEYCODE_SEQUENCE, has_modifier_extra, escape_sequence, was_terminated)

                else: # This case is for when the escape sequence is not a known keycode, or has improper formatting.
                    was_terminated = False
                    return IOKeycode(-1, "", IOModifiers(), IOTerminalStandard.UNKNOWN, IOEscape.INCOMPLETE, False, escape_sequence, was_terminated)

        if len(input) == escape_len + 1 and input[escape_len] != '[':
            was_terminated = True
            return IOKeycode(-1, input[escape_len], IOModifiers(), IOTerminalStandard.UNKNOWN, IOEscape.ALT_KEYPRESS, False, escape_sequence, was_terminated)

    was_terminated = True
    return IOKeycode(-1, input[0], IOModifiers(), IOTerminalStandard.UNKNOWN, IOEscape.CHAR, False, escape_sequence, was_terminated)

def escape_escape(escape: str, escape_sequence: str, escape_char_raw: str) -> str:
    return escape.encode('unicode_escape').decode('utf-8').replace(escape_char_raw, escape_sequence)

def calculate_modifier(modifier: int) -> IOModifiers:
    modifier -= 1
    return IOModifiers(
        SHIFT=(modifier & 1) != 0,
        ALT=(modifier & 2) != 0,
        CTRL=(modifier & 4) != 0,
        META=(modifier & 8) != 0,
    )
def parse_extra_key(input: str) -> str:
    """
    # parse_extra_key(input: str) -> str
    Parse an extra key from a string input.

    Parameters:
        (*) input:              The input string to parse
                                the extra key from.
                                @Type str;

    Return Value:
        (*) The parsed extra key
            @Type str

            Possible extra keys:
                (*) <backspace>
                (*) <tab>
                (*) <enter>
                (*) <ctrl-c>
    """

    encoded_input = input.encode('unicode_escape').decode('utf-8')

    if encoded_input.startswith("\\\\r"):
        return "<enter>"
    if encoded_input.startswith("\\\\n"):
        return "<enter>"
    if encoded_input.startswith("\\\\t"):
        return "<tab>"
    if encoded_input.startswith("\\\\b"):
        return "<backspace>"
    if encoded_input.startswith("\\\\x7f"):
        return "<backspace>"
    if encoded_input.startswith("\\\\x08"):
        return "<backspace>"
    if encoded_input.startswith("\\\\x09"):
        return "<tab>"
    if encoded_input.startswith("\\\\x0D"):
        return "<enter>"
    if encoded_input.startswith("\\\\x03"):
        return "<ctrl+c>"

    return ""
