from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Union

from mustiolo.exception import (
    CommandDuplicate,
    CommandMissingMenuMessage,
    CommandNotFound,
)
from mustiolo.models.parameters import ParameterModel
from mustiolo.utils import (
    get_function_location,
    get_function_metadata,
    parse_docstring_for_menu_usage,
    parse_parameters,
)


@dataclass
class CommandModel:
    """This class is used as Model for help message and
       for handle checks on the command.

       'f' contains doc, name and parameters so in this case we're duplicating
       those informations
    """
    name: str = ""
    alias: str = ""
    f: Union[Callable, None] = None
    menu: str = ""
    usage: str = ""
    # TODO: change parameters into arguments
    parameters: List[ParameterModel] = field(default_factory=list)

    def __str__(self) -> str:
        return self.get_usage()

    def get_menu(self, padding: int) -> str:
        name_and_alias = self.name
        if len(self.alias) > 0:
            name_and_alias +=  f", {self.alias}"
        return f"{name_and_alias.ljust(padding)}\t\t{self.menu}"

    def get_usage(self) -> str:
        help_msg = [f"{self.usage}\n\n{self.name} {' '.join([p.name.upper() for p in self.parameters])}"]
        if len(self.parameters) == 0:
            return help_msg[0]

        help_msg.append("\nParameters:")
        help_msg.extend([str(p) for p in self.parameters])
        return "\n".join(help_msg)

    def get_mandatory_parameters(self) -> List[ParameterModel]:
        return [ param for param in self.parameters if param.default is None ]

    def get_optional_parameters(self) -> List[ParameterModel]:
        return [ param for param in self.parameters if param.default is not None ]

    def cast_arguments(self, args: List[str]) -> List[Any]:
        """
        This function cast the arguments to the correct type.
        Raises an exception if the number of arguments is less than the
        number of mandatory parameters or if it's greater of the total.
        """
        if len(args) < len(self.get_mandatory_parameters()):
            raise Exception("Missing parameters")
        if len(args) > len(self.parameters):
            raise Exception("Too many parameters")

        return [ self.parameters[index].convert_to_type(args[index]) for index in range(0, len(args)) ]

    def __call__(self, *args, **kwargs) -> Any:
        if self.f is None:
            raise Exception("No function associated with this command.")
        return self.f(*args, **kwargs)


@dataclass
class CommandAlias:
    command: CommandModel

    def __str__(self) -> str:
        return self.command.get_usage()

    def get_menu(self, padding: int) -> str:
        return self.command.get_menu(padding)

    def get_usage(self) -> str:
        return self.command.get_usage()

    def get_mandatory_parameters(self) -> List[ParameterModel]:
        return self.command.get_mandatory_parameters()

    def get_optional_parameters(self) -> List[ParameterModel]:
        return self.command.get_optional_parameters()

    def cast_arguments(self, args: List[str]) -> List[Any]:
        return self.command.cast_arguments(args)

    def __call__(self, *args, **kwargs) -> Union[Any, None]:
        if self.command.f is None:
            return None
        return self.command(*args, **kwargs)


class CommandGroup:
    """
    This class contains a set of CommandsModel and/or CommandGroup, in
    this way we can define a command tree.
    """
    def __init__(self, name: str, menu : str = "", usage: str = ""):
        # commands key is the command name and its alias (2 entries which points to the same value)
        self._commands: Dict[str, Union[CommandModel, CommandGroup, CommandAlias]] = {}
        self._name: str = name
        self._menu: str = menu
        self._usage: str = usage
        self._max_command_length = 0
        self._current_cmd = CommandModel(f=None, name=name, alias="", menu=menu, usage=usage, parameters=[])

    @property
    def name(self) -> str:
        return self._name

    def add_help_command(self) -> None:
        self.register_command(self.help, name="?", menu="Shows this help.")

    def add_command_group(self, group: 'CommandGroup') -> None:
        if group._name in self._commands:
            raise Exception(f"Command with name '{group._name}' already exists")
        
        self._commands[group._name] = group

    def register_command(self, fn: Callable, name: Union[str, None] = None, alias: str = "",
                          menu: str = "", usage: str = "") -> None:

        docstring_msgs = parse_docstring_for_menu_usage(fn)

        command_name = name if name is not None else fn.__name__
        command_menu = menu if menu != "" else docstring_msgs[0]
        command_usage = usage if usage != "" else docstring_msgs[1]

        if command_name == "" or command_name is None:
            raise Exception(f"Command name '{command_name}' '{fn.__name__}' cannot be None or empty")

        if command_menu == "":
            fmeta = get_function_metadata(fn)
            raise CommandMissingMenuMessage(fmeta.name, fmeta.location.filename, fmeta.location.lineno)

        # if usage is not defined use menu help message
        if command_usage == "":
            command_usage = command_menu

        if len(command_name) + len(", ") + len(alias) > self._max_command_length:
            self._max_command_length = len(command_name)

        if command_name in self._commands.keys():
            location = get_function_location(fn)
            raise CommandDuplicate(command_name, location.filename, location.lineno)

        if alias in self._commands.keys():
            location = get_function_location(fn)
            raise CommandDuplicate(alias, location.filename, location.lineno)

        parameters = parse_parameters(fn)
        cmd = CommandModel(name=command_name, alias=alias, f=fn, menu=command_menu, usage=command_usage,
                             parameters=parameters)
        self._commands[command_name] = cmd
        if len(alias) > 0:
            self._commands[alias] = CommandAlias(command=cmd)

    def has_command(self, name: str) -> bool:
        return name in self._commands
    
    def get_command(self, name: str) -> CommandModel:
        if name not in self._commands:
            raise CommandNotFound(name)
        return self._commands.get(name)

    def get_commands(self) -> dict[str, Union[CommandModel, CommandAlias, 'CommandGroup']]:
        return self._commands

    def get_usage(self, cmd: str) -> str:
        return self._commands[cmd].get_usage()

    def help(self, cmd_path: List[str] = []) -> None:
        """
        Shows the help menu.
        We need to iterate over the cmd_path in order to reach the correct command.
        """

        if len(cmd_path) == 0:
            print("\n".join([ command.get_menu(self._max_command_length) for _, command in self._commands.items() if not isinstance(command, CommandAlias)]))
            return
 
        cmd_name = cmd_path.pop(0)
        command = self.get_command(cmd_name)
        if isinstance(command, CommandGroup):
            command.help(cmd_path)
            return
        
        if len(cmd_path) > 0:
            raise Exception(f"{cmd_name} is not a subcommand of {self._name}")
        print(self.get_usage(cmd_name))

    def __str__(self) -> str:
        return self._current_cmd.get_usage()

    def get_menu(self, padding: int) -> str:
        return self._current_cmd.get_menu(padding)

    def __call__(self) -> Any:
        if self._current_cmd.f is None:
            raise Exception(f"'{self._name}' is not executable")

        return self._current_command()
