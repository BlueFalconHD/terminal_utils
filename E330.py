##################################################################################
#                                                                                #
# E330 - TERMINAL CLIENT                                                         #
# THE ROBCO MODEL E-330 IS THE MOST RELIABLE CLIENT TERMINAL EVER BUILT.         #
#                                                                                #
# (c) 2075-2077 ROBCO INDUSTRIES                                                 #
#                                                                                #
##################################################################################

from os import linesep
from re import X
import threading
import sys
import tty
import termios
from enum import Enum
from dataclasses import dataclass, field
from typing import Callable, List

# Constants
SAVE_SCREEN = "\033[?1049h\033[?25l"
RESTORE_SCREEN = "\033[?1049l\033[?25h"

@dataclass
class E330:
    input_buffer: str = ""
    subscribers: List[Callable[[str], None]] = field(default_factory=list)
    input_thread: threading.Thread = field(init=False, default=None)
    stop_input_event: threading.Event = field(init=False, default_factory=threading.Event)

    # Terminal Initialization and Shutdown
    def initialize_terminal(self):
        print(SAVE_SCREEN, end='', flush=True)

    def shutdown_terminal(self):
        # Unsuscribe all subscribers
        self.subscribers.clear()

        print(RESTORE_SCREEN, end='', flush=True)
        exit(0)


    # Output Method
    def print(self, text):
        print(text, end='', flush=True)

    # Subscription Events
    def subscribe_to_input(self, callback: Callable[[str], None]):
        if callback not in self.subscribers:
            self.subscribers.append(callback)

    def unsubscribe_from_input(self, callback: Callable[[str], None]):
        if callback in self.subscribers:
            self.subscribers.remove(callback)

    # Input Handling
    def handle_input(self, char: str):
        self.input_buffer += char
        for callback in self.subscribers:
            callback(char)

    def flush_input_buffer(self):
        self.input_buffer = ""

    def read_input(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while not self.stop_input_event.is_set():
                char = sys.stdin.read(1)
                if char:
                    self.handle_input(char)
                if char == '\x03':  # Ctrl+C to exit
                    break
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    # Threading
    def start_input_thread(self):
        self.input_thread = threading.Thread(target=self.read_input, daemon=True)
        self.input_thread.start()

    def stop_input_thread(self):
        self.stop_input_event.set()
        if self.input_thread is not None:
            print("Stopping input thread")
            self.input_thread.join()
