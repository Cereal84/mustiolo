from typing import Callable

from mustiolo.exception import CommandReserved
from mustiolo.models.command import CommandModel
from mustiolo.models.menu import MenuDescriptor
from mustiolo.utils import parse_parameters


class Menu:
    def __init__(self, name: str):
       self._descriptor = MenuDescriptor(name)
       self._descriptor.add_help_command()

       # add help command by default
       self._reserved_commands = ["exit"]

    def command(self, name: str = None, help_short: str = None, help_long: str = None) -> None:
        if name in self._reserved_commands:
            raise CommandReserved(name)
        def decorator(funct: Callable) -> Callable:
            self._descriptor.register_command(funct, name, help_short, help_long)
            return funct
        return decorator

    def descriptor(self) -> MenuDescriptor:
        return self._descriptor
