import os
from typing import Callable

from mustiolo.exception import *
from mustiolo.models.command import CommandModel
from mustiolo.utils import parse_parameters


_ROOT_MENU = "_root_"


class MenuDescriptor:

    def __init__(self, name: str = _ROOT_MENU):
        self.name = name
        self._commands = {}
        self._max_command_length = 0


    def add_help_command(self):
        self.register_command(self.help, name="?", help_short="Shows this help.")


    def register_command(self, fn: Callable, name: str,
                          help_short: str, help_long: str = None) -> None:

        command_name = name if name is not None else fn.__name__
        command_help_short = help_short if help_short is not None else fn.__doc__.split("\n")[0]
        command_help_long = help_long if help_long is not None else fn.__doc__

        if command_name is None or command_name == "":
            raise Exception("Command name cannot be None or empty")

        if command_help_long is None:
            command_help_long = ""
        if command_help_short is None:
            command_help_short = ""

        # TODO while register the commands store also the max command length and max short help length
        # in order to print the help in a better way.
        if len(command_name) > self._max_command_length:
            self._max_command_length = len(command_name)

        if command_name in self._commands.keys():
            filename = os.path.basename(self._commands[command_name].f.__code__.co_filename)
            lineno = self._commands[command_name].f.__code__.co_firstlineno
            real_function_name = self._commands[command_name].f.__name__
            raise CommandDuplicate(command_name, filename, lineno)

        parameters = parse_parameters(fn)
        model = CommandModel(name=command_name, f=fn, help_short=command_help_short, help_long=command_help_long,
                             parameters=parameters)
        self._commands[command_name] = model


    def has_command(self, name: str) -> bool:
        return name in self._commands
    
    def get_command(self, name: str) -> CommandModel:
        if name not in self._commands:
            raise CommandNotFound(name)
        return self._commands.get(name)

    def get_commands(self) -> dict[str, CommandModel]:
        return self._commands

    def _help_message_specific_command(self, cmd: str) -> str:
        return f"Usage {cmd} {str(self._commands[cmd])}"


    def help(self, command_name: str = ""):
        """Shows the help menu."""
        if command_name != "":
            if command_name not in self._commands:
                raise CommandNotFound(command_name) 
 
            print(self._help_message_specific_command(command_name))
        else:
            print("\n".join([ command.short_help(self._max_command_length) for _, command in self._commands.items()]))


        
