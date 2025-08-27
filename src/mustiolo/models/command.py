from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, NewType, Union

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

CommandsType = NewType('CommandsType', Dict[str, Union['CommandModel', 'CommandAlias',
                                                        'SubCommandGroup']])


# TODO: Maybe we can use a virtual base class for CommandModel and CommandAlias and SubCommandGroup.
# This way we can have different benefits:
# 1. We can use isinstance to check if an object is a command by using Protocol or ABC.
# 2. Avoid the Union type in CommandsType
# 3. We can use a common interface for all commands, aliases and subcommandgroup.
# But this is not necessary at the moment, so we will leave it as it is.
# The main problem is SubCommandGroup, which is not an executable command.

CommandsType = NewType('CommandsType', Dict[str, Union['CommandModel', 'CommandAlias',
                                                        'SubCommandGroup']])

@dataclass(frozen=True, slots=True)
class CommandModel:
    """This class is used as Model for help message and
       for handle checks on the command.

       'f' contains doc, name and parameters so in this case we're duplicating
       this information
    """
    name: str = ""
    alias: str = ""
    f: Union[Callable, None] = None
    menu: str = ""   # this is the short help message
    usage: str = ""  # this is the long help message
    arguments: List[ParameterModel] = field(default_factory=list)


    @property
    def argument_padding(self) -> int:
        """
        This function returns the padding used for the help message.
        It is used to align the parameters in the help message.
        """
        # compute the padding based on the arguments
        return max(len(arg.metavar) for arg in self.arguments) if self.arguments else 0

    def __str__(self) -> str:
        return self.get_usage()

    def get_menu(self, padding: int) -> str:
        name_and_alias = self.name
        if len(self.alias) > 0:
            name_and_alias +=  f", {self.alias}"
        return f"{name_and_alias.ljust(padding)}\t\t{self.menu}"

    def get_usage(self) -> str:
        help_msg = [f"{self.usage}\n\n{self.name} {' '.join([p.metavar.upper() for p in self.arguments])}"]
        if len(self.arguments) == 0:
            return help_msg[0]

        help_msg.append("\nParameters:\n")
        help_msg.extend([p.get_usage(self.argument_padding) for p in self.arguments])
        return "\n".join(help_msg)

    def get_mandatory_parameters(self) -> List[ParameterModel]:
        return [ arg for arg in self.arguments if arg.default is None ]

    def get_optional_parameters(self) -> List[ParameterModel]:
        return [ arg for arg in self.arguments if arg.default is not None ]

    def cast_arguments(self, args: List[str]) -> List[Any]:
        """
        This function cast the arguments to the correct type.
        Raises an exception if the number of arguments is less than the
        number of mandatory parameters or if it's greater of the total.
        """
        if len(args) < len(self.get_mandatory_parameters()):
            raise Exception("Missing parameters")
        if len(args) > len(self.arguments):
            raise Exception("Too many parameters")

        return [ self.arguments[index].convert_to_type(args[index]) for index in range(0, len(args)) ]

    def __call__(self, *args, **kwargs) -> Any:
        if self.f is None:
            raise Exception("No function associated with this command.")
        return self.f(*args, **kwargs)


@dataclass(frozen=True, slots=True)
class CommandAlias:
    """
    This class is used to create an alias for a command.
    It is used to allow another name for the same command.
    We copy the command model and use it as an alias.
    TODO: maybe we can use a weaker reference to the command model to better manage memory.
    """

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

# TODO find a better name for this class, maybe CommandSet or CommandCollection
class CommandGroup:
    """
    This class contains a set of CommandsModel and/or SubCommandGroup, in
    this way we can define a command tree.
    """
    def __init__(self):
        # commands key is the command name and its alias (2 entries which points to the same value)
        self._commands: CommandsType = {}
        self._max_command_length = 0

    @property
    def commands(self) -> CommandsType:
        """
        Returns the commands in this group.
        """
        return self._commands

    @property
    def max_command_length(self) -> int:
        """
        Returns the maximum length of the command name in this group.
        This is used to format the help menu.
        """
        return self._max_command_length

    def has_command(self, name: str) -> bool:
        """
        Check if the command with the given name exists in this group.
        """
        return name in self._commands

    def register_command(self, fn: Callable, name: Union[str, None] = None, alias: str = "",
                         metavars: Dict[str, str] = {},
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

        display_cmd = f"{command_name}, {alias}"

        if len(display_cmd) > self._max_command_length:
            self._max_command_length = len(display_cmd)

        if command_name in self._commands:
            location = get_function_location(fn)
            raise CommandDuplicate(command_name, location.filename, location.lineno)

        if alias in self._commands:
            location = get_function_location(fn)
            raise CommandDuplicate(alias, location.filename, location.lineno)

        parameters = parse_parameters(f=fn, metavars=metavars)
        cmd = CommandModel(name=command_name, alias=alias, f=fn, menu=command_menu, usage=command_usage,
                            arguments=parameters)
        self._commands[command_name] = cmd
        if len(alias) > 0:
            self._commands[alias] = CommandAlias(command=cmd)

    def include_commands(self, cmds: Union['CommandGroup', 'SubCommandGroup']) -> None:
        """
        Include commands from another CommandGroup into this one.
        This will not replace existing commands.
        The merged commands will be available in the current group.
        """

        if isinstance(cmds, SubCommandGroup):
            # if the cmds is a SubCommandGroup we need to include SubCommandGroup.
            # We need to check if the SubCommandGroup name is already in  the commands
            if cmds.name in self._commands:
                # probably we need to raise a custom exception here
                raise CommandDuplicate(cmds.name, cmds._current_cmd.f.__code__.co_filename, cmds._current_cmd.f.__code__.co_firstlineno)
            self._commands[cmds.name] = cmds

            # update width for subgroup name
            if len(cmds.name) > self._max_command_length:
                self._max_command_length = len(cmds.name)
            return

        if isinstance(cmds, CommandGroup):
            # we need to iterate over the commands in the group and add them one by one.
            # probably to have better performance we can use a set to check for duplicates without for loop.
            for cmd_name, cmd in cmds.commands.items():
                if cmd_name in self._commands:
                    # probably we need to raise a custom exception here
                    raise CommandDuplicate(cmd_name, cmd.f.__code__.co_filename, cmd.f.__code__.co_firstlineno)
                self._commands[cmd_name] = cmd
            # update the max command length
            if self._max_command_length < cmds.max_command_length:
                self._max_command_length = cmds.max_command_length

    def get_command(self, name: str) -> CommandModel:
        if name not in self._commands:
            raise CommandNotFound(name)
        return self._commands.get(name)


class SubCommandGroup(CommandGroup):
    """
    This class contains a set of CommandsModel, AliasCommandModel, SubCommandGroup.
    In this way we can define a command tree.
    """
    def __init__(self, name: str, menu : str = "", usage: str = ""):
        super().__init__()
        self._name: str = name
        self._menu: str = menu
        self._usage: str = usage
        self._current_cmd = CommandModel(f=None, name=name, alias="", menu=menu, usage=usage, arguments=[])

    @property
    def name(self) -> str:
        return self._name

    def add_help_command(self) -> None:
        self.register_command(self.help, name="?", menu="Shows this help.")

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
        if isinstance(command, SubCommandGroup):
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
        # at the moment this kind of commands are not executable
        raise Exception(f"'{self._name}' is not executable")

