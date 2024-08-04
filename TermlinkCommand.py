from dataclasses import dataclass
from typing import Dict
from typing_extensions import Optional

@dataclass
class TermlinkCommandRegistry:
    commands: Dict[str, 'TermlinkCommand']

    def __init__(self):
        self.commands = {}

    def register(self, command: 'TermlinkCommand'):
        self.commands[command.command_name] = command

    def get_command_for_shell_input(self, shell_input: str, builtin = False) -> Optional['TermlinkCommand']:
        # find key in dictionary that shell_input starts with, return value of key with shortest length
        for key in self.commands.keys():
            if shell_input.startswith((lambda: key + "" if builtin else key + " ")()):
                return self.commands[key]

        return None

@dataclass
class TermlinkCommand:
    command_name: str

    def handle(self, termlink: 'Termlink', passed_text: str):
        pass

    def __str__(self):
        return self.command_name

    def __repr__(self):
        return self.command_name

@dataclass
class TermlinkCommandHelp(TermlinkCommand):
    command_name: str = "help"

    def handle(self, termlink: 'Termlink', passed_text: str):
        termlink.terminal.print("Available commands:\n")
        for command in termlink.registry.commands.commands:
            if not command.startswith("_"):
                termlink.terminal.print(str(command) + "\n")

@dataclass
class TermlinkCommandBuiltIn_Unrecognized_Command(TermlinkCommand):
    command_name: str = "_unrecognized_command"

    def handle(self, termlink: 'Termlink', passed_text: str):
        termlink.terminal.print("Unrecognized command: " + passed_text)



COMMAND_INDEX = {
    "help": TermlinkCommandHelp(),
    "_unrecognized_command": TermlinkCommandBuiltIn_Unrecognized_Command()
}
