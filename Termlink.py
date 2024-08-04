#
# TERMLINK - ROBCO INDUSTRIES UNIFIED OPERATING SYSTEM
# MAIN I/O SHELL FOR E330 TERMINAL CLIENT
# (c) 2075-2077 ROBCO INDUSTRIES
#

from typing_extensions import Optional
import E330
from dataclasses import dataclass, field
from typing import Callable, List
from time import sleep
import CtrlCodes
from IOEscape import IOEscape, IOKeycode, IOModifiers, parse_keycode, escape_escape, IOEscape, parse_extra_key
from enum import Enum

from TermlinkCommand import TermlinkCommand, TermlinkCommandRegistry, COMMAND_INDEX

# MARK: CONSTANTS
ESCAPE_SEQUENCE = "<esc>"


class ExecutionState(Enum):
    IDLE = "idle"
    INPUT = "input"
    COMMAND = "command"
    OUTPUT = "output"

@dataclass
class TermlinkRegistry:
    commands: TermlinkCommandRegistry = field(default_factory=TermlinkCommandRegistry)

@dataclass
class Termlink:

    terminal: E330.E330
    input_buffer: str = ""
    input_queue: str = ""
    cursor_position: int = 0
    execution_state: ExecutionState = ExecutionState.IDLE
    active: bool = True

    history: List[str] = field(default_factory=list)
    current_selected_history: int = -1

    registry: TermlinkRegistry = field(default_factory=TermlinkRegistry)


    def __post_init__(self):
        self.events = []
        self.terminal.subscribe_to_input(self.handle_key_press)

        for command in COMMAND_INDEX.values():
            self.registry.commands.register(command)

    def bell(self):
        self.terminal.print("\a")

    def input_queue_flush(self):
        self.input_queue = ""

    def handle_key_press(self, key: str):
        escaped_key = escape_escape(key, ESCAPE_SEQUENCE, "\\x1b")
        self.input_queue += escaped_key

        input_queue_keycode = parse_keycode(self.input_queue, ESCAPE_SEQUENCE)
        input_queue_extra = parse_extra_key(self.input_queue)


        if input_queue_keycode.is_special():
            if input_queue_keycode.is_possibly_incomplete():
                return
            self.handle_special_key(input_queue_keycode)
        elif input_queue_extra != "":
            self.handle_extra_key(input_queue_extra)
        else:
            self.handle_normal_key(input_queue_keycode)

        self.input_queue_flush()

    def handle_extra_key(self, key: str):
        handlers = {
            "<enter>": self.handle_enter_press,
            "<tab>": self.handle_tab_press,
            "<backspace>": self.handle_backspace,
            "<ctrl+c>": self.handle_ctrl_c
        }
        handler = handlers.get(key)
        if handler:
            handler()

    def handle_special_key(self, key: IOKeycode):
        handlers = {
            "Up": self.handle_up_arrow,
            "Down": self.handle_down_arrow,
            "Left": self.handle_left_arrow,
            "Right": self.handle_right_arrow,
            "Home": self.handle_home_key,
            "End": self.handle_end_key,
            "Delete": self.handle_delete_key
        }
        friendly_name = key.resolve_friendly_name(include_modifiers=False)
        handler = handlers.get(friendly_name)
        if handler:
            handler(key.modifier)
        else:
            print("Special key not handled: " + friendly_name)

    def handle_normal_key(self, key: IOKeycode):
        pos = self.cursor_position
        self.input_buffer = (
            self.input_buffer[:pos] + key.keycode_char + self.input_buffer[pos:]
        )
        self.cursor_position += 1

    def handle_enter_press(self):

        self.command(self.input_buffer)
        self.input_buffer = ""
        self.cursor_position = 0

    def handle_tab_press(self):
        pass

    def handle_backspace(self):
        if self.cursor_position > 0:
            pos = self.cursor_position
            self.input_buffer = (
                self.input_buffer[:pos - 1] + self.input_buffer[pos:]
            )
            self.cursor_position -= 1
        else:
            self.bell()

    def handle_left_arrow(self, modifiers: IOModifiers):
        if self.cursor_position > 0:
            self.cursor_position -= 1
        else:
            self.bell()

    def handle_right_arrow(self, modifiers: IOModifiers):
        if self.cursor_position < len(self.input_buffer):
            self.cursor_position += 1
        else:
            self.bell()

    def handle_up_arrow(self, modifiers: IOModifiers):
        # Cycle through history
        if self.current_selected_history < len(self.history) - 1:
            self.current_selected_history += 1
            self.input_buffer = self.history[self.current_selected_history]
            self.cursor_position = len(self.input_buffer)
        else:
            self.bell()

    def handle_down_arrow(self, modifiers: IOModifiers):
        if self.current_selected_history > 0:
            self.current_selected_history -= 1
            self.input_buffer = self.history[self.current_selected_history]
            self.cursor_position = len(self.input_buffer)
        else:
            self.bell()

    def handle_home_key(self, modifiers: IOModifiers):
        self.cursor_position = 0

    def handle_end_key(self, modifiers: IOModifiers):
        self.cursor_position = len(self.input_buffer)

    def handle_delete_key(self, modifiers: IOModifiers):
        pos = self.cursor_position
        if pos < len(self.input_buffer):
            self.input_buffer = (
                self.input_buffer[:pos] + self.input_buffer[pos + 1:]
            )
        else:
            self.bell()

    def handle_ctrl_c(self):
        global RUNNING
        RUNNING = False

    def print_prompt(self):
        reset_position = CtrlCodes.clear_line() + CtrlCodes.cursor_beginning_of_line()
        prompt = "> "
        input_buffer = self.input_buffer
        cursor_position = self.cursor_position

        # Unicode full block character
        full_block = "\u2588"


        # Insert the full block at the cursor position
        if cursor_position < len(input_buffer):
            # Split the input buffer at the cursor position
            before_cursor = input_buffer[:cursor_position]
            under_cursor = CtrlCodes.REVERSE + input_buffer[cursor_position] + CtrlCodes.RESET
            after_cursor = input_buffer[cursor_position + 1:]
            input_buffer_with_cursor = before_cursor + under_cursor + after_cursor
        else:
            # If the cursor is at the end of the input buffer
            input_buffer_with_cursor = input_buffer + CtrlCodes.REVERSE + " " + CtrlCodes.RESET

        self.terminal.print(reset_position + prompt + input_buffer_with_cursor)

    def command(self, command: str):
        self.history.append(command)

        self.terminal.print("\r\n")

        # Get the command corresponding to the input from the registry
        termlinkcmd = self.registry.commands.get_command_for_shell_input(command)

        if termlinkcmd:
            # Run the command
            termlinkcmd.handle(self, command)
        else:
            tcmd = self.registry.commands.get_command_for_shell_input("_unrecognized_command", builtin=True)
            if tcmd:
                tcmd.handle(self, command)
            else:
                self.terminal.print("FATAL: expected builtin _unrecognized_command to be in registry")

        self.terminal.print("\r\n")


RUNNING = True

terminal = E330.E330()
termlink = Termlink(terminal)

terminal.initialize_terminal()
terminal.start_input_thread()
terminal.print(CtrlCodes.clear_screen())
terminal.print(CtrlCodes.restore_cursor_position())

while RUNNING:
    termlink.print_prompt()
    sleep(0.001)

terminal.stop_input_thread()
terminal.shutdown_terminal()
