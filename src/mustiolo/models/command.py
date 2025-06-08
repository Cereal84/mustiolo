from dataclasses import dataclass
from typing import Any, Dict, Callable, List, Union

from mustiolo.utils import parse_parameters
from mustiolo.models.parameters import ParameterModel
from mustiolo.exception import CommandNotFound, CommandDuplicate


@dataclass
class CommandModel:
    """This class is used as Model for help message and
       for handle checks on the command.

       'f' contains doc, name and parameters so in this case we're duplicating
       those informations
    """
    name: str
    f: Union[Callable, None]
    help_short: str
    help_long: str
    # TODO: change parameters into arguments
    parameters: List[ParameterModel]

    def __str__(self) -> str:
        help_msg = [f"{self.help_long}\n\n{self.name} {' '.join([p.name.upper() for p in self.parameters])}"]
        if len(self.parameters) == 0:
            return help_msg[0]

        help_msg.append("\nParameters:")
        help_msg.extend([ str(p) for p in self.parameters])
        return "\n".join(help_msg)

    def short_help(self, padding: int) -> str:
        return f"{self.name.ljust(padding)}\t{self.help_short}"

    def long_help(self) -> str:
        return f"{self.name}\n\n{self.help_long}\n\nParameters:\n" + "".join([ str(p) for p in self.parameters])

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


class CommandGroup:
    """
    This class contains a set of CommandsModel and/or CommandGroup, in
    this way we candefine a command tree.
    """
    def __init__(self, name: str, help_short : str = "", help_long: str = ""):
        self._commands: Dict[str, Union[ CommandModel, CommandGroup ] ] = {}
        self._name: str = name
        self._help_short: str = help_short
        self._help_long: str = help_long
        self._max_command_length = 0
        self._current_cmd = CommandModel(f=None, name=name, help_short=help_short, help_long=help_long, parameters=[])


    @property
    def name(self) -> str:
        return self._name

    def add_help_command(self):
        self.register_command(self.help, name="?", help_short="Shows this help.")

    def add_command_group(self, group: 'CommandGroup') -> None:
        if group._name in self._commands:
            raise Exception(f"Command with name '{group._name}' already exists")
        
        self._commands[group._name] = group

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
        return f"\n{str(self._commands[cmd])}"


    def help(self, cmd_path: List[str] = []) -> None:
        """
        Shows the help menu.
        We need to iterate over the cmd_path in order to reach the correct command.
        """

        if len(cmd_path) == 0:
            print("\n".join([ command.short_help(self._max_command_length) for _, command in self._commands.items()]))
            return
 
        cmd_name = cmd_path.pop(0)
        command = self.get_command(cmd_name)
        if isinstance(command, CommandGroup):
            command.help(cmd_path)
            return
        
        if len(cmd_path) > 0:
            raise Exception(f"{cmd_name} is not a subcommand of {self._name}")
        print(self._help_message_specific_command(cmd_name))


    def __str__(self) -> str:
        return str(self._current_cmd)

    def short_help(self, padding: int) -> str:
        return self._current_cmd.short_help(padding)

    def long_help(self) -> str:
        return self._current_cmd.long_help()

    def __call__(self) -> Any:
        if self._current_cmd.f is None:
            raise Exception(f"'{self._name}' is not executable")

        return self._current_command()