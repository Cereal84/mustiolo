from typing import Callable
#from mustiolo.command_model import CommandModel
from mustiolo.cli import CommandModel
from mustiolo.utils import parse_parameters


class Menu:

    def __init__(self, id: str):
        self.id = id
        self._commands = {}
        self._max_command_length = 0

    def _register_command(self, fn: Callable, name: str,
                    help_short: str, help_long: str) -> None:
    
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

        if command_name in self._commands:
            raise Exception(f"Command {command_name} already exists")
        parameters = parse_parameters(fn)
        model = CommandModel(name=command_name, f=fn, help_short=command_help_short, help_long=command_help_long, parameters=parameters)
        self._commands[command_name] = model
    

    def command(self, name: str = None, help_short: str = None, help_long: str = None) -> None:
        def decorator(funct: Callable) -> Callable:
    
            self._register_command(funct, name, help_short, help_long)
            return funct
        return decorator