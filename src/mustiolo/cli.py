
from collections.abc import Callable
from dataclasses import dataclass
import os
from typing import Any, List
from mustiolo.message_box import BorderStyle, draw_message_box

pythonType2String = {}
pythonType2String[str] = "STRING"
pythonType2String[int] = "INTEGER"


@dataclass
class ParsedCommand:
    name : str
    parameters: List[Any]


@dataclass
class ParameterModel:
    name: str
    ptype: Any
    default: Any

    def __str__(self) -> str:
        msg = [f"\t\t{self.name.upper()}\tType {pythonType2String[self.ptype]} "]
        if self.default is not None:
            msg.append(f"[optional] [default: {self.default}]")
        else:
            msg.append("[required]")
        return "".join(msg)

    def  convert_to_type(self, value: str) -> Any:
        # here we try to convert the value to the correct type
        # if it fails an exception is raised
        return self.ptype(value)


@dataclass
class CommandModel:
    """This class is used as Model for help message and
       for handle checks on the command.

       'f' contains doc, name and parameters so in this case we're duplicating
       those informations
    """
    name: str
    f: Callable
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

    def short_help(self) -> str:
        return f"{self.name}{' '*4}{self.help_short}"

    def long_help(self) -> str:
        return f"{self.name}\n\n{self.help_long}\n\nParameters:\n" + "".join([ str(p) for p in self.parameters])

    def get_mandatory_parameters(self) -> List[ParameterModel]:
        return [ param for param in self.parameters if param.default is None ]

    def get_optional_parameters(self) -> List[ParameterModel]:
        return [ param for param in self.parameters if param.default is not None ]

    def cast_arguments(self, args: List[str]) -> List[Any]:
        """ This function cast the arguments to the correct type.
            It raises an exception if the number of arguments is less than the
            number of mandatory parameters or if it's greater of the total.
        """
        if len(args) < len(self.get_mandatory_parameters()):
            raise Exception("Missing parameters")
        if len(args) > len(self.parameters):
            raise Exception("Too many parameters")

        return [ self.parameters[index].ptype(args[index]) for index in range(0, len(args)) ]


class TinyCLI:

    def __init__(self, hello_message: str = "Welcome to TinyCLI", prompt: str = ">"):
        self._hello_message = hello_message
        self._prompt = prompt
        self._columns = os.get_terminal_size().columns
        self._commands = {}


    def _draw_panel(self, title: str , content: str, border_style: BorderStyle = BorderStyle.SINGLE_ROUNDED, columns: int = None) -> str:
        """Draw panle with a title and content.
        """
        cols = self._columns
        if columns is not None:
            cols = columns
        return draw_message_box(title, content, border_style, cols)


    def _register_command(self, f_wrapper: Callable, f: Callable, name: str = None, help_short: str = None, help_long: str = None) -> None:

        command_name = name if name is not None else f.__name__
        command_help_short = help_short if help_short is not None else f.__doc__.split("\n")[0]
        command_help_long = help_long if help_long is not None else f.__doc__

        if command_name is None or command_name == "":
            raise Exception("Command name cannot be None or empty")

        if command_help_long is None:
            command_help_long = ""
        if command_help_short is None:
            command_help_short = ""

        # TODO while register the commands store also the max command length and max short help length
        # in order to print the help in a better way.

        if f.__name__ in self._commands:
            raise Exception(f"Command {f.__name__} already exists")
        parameters = self._parse_parameters(f)
        model = CommandModel(name=command_name, f=f_wrapper, help_short=command_help_short, help_long=command_help_long, parameters=parameters)
        self._commands[command_name] = model

    def command(self, name: str = None, help_short: str = None, help_long: str = None) -> None:
        def decorator(funct: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                try:
                    funct(*args, **kwargs)
                except Exception as ex:
                    self._handle_exception(ex)

            self._register_command(wrapper, funct, name, help_short, help_long)
            return wrapper
        return decorator


    def _get_defaults(self, fn):
        """
        Get the default values of the passed function or method.
        """
        output = {}
        if fn.__defaults__ is not None:
            # Get the names of all provided default values for args
            default_varnames = list(fn.__code__.co_varnames)[:fn.__code__.co_argcount][-len(fn.__defaults__):]
            # Update the output dictionary with the default values
            output.update(dict(zip(default_varnames, fn.__defaults__)))
        if fn.__kwdefaults__ is not None:
            # Update the output dictionary with the keyword default values
            output.update(fn.__kwdefaults__)
        return output

    def _parse_parameters(self, f: Callable) -> List[ParameterModel]:
        parameters = []
        defaults = self._get_defaults(f)
        for pname, ptype in f.__annotations__.items():
            parameters.append(ParameterModel(name=pname, ptype=ptype, default=(defaults.get(pname, None))))

        return parameters

    def change_prompt(self, prompt: str) -> None:
        self._prompt = prompt

    def _help(self) -> str:
        return "\n".join([ command.short_help() for _, command in self._commands.items()])

    def _help_specific_command(self, cmd: str) -> str:
        if cmd not in self._commands:
            # substitute with a custom exception
            print(self._draw_panel("Error", f"Command '{cmd}' does not exists."))
            print(self._help())
            return ""

        return f"Usage {cmd} {str(self._commands[cmd])}"

    def _handle_exception(self, ex) -> None:
        print(self._draw_panel("Error", str(ex)))

    def _parse_command_line(self, command_line: str) -> ParsedCommand:
        components = command_line.split()
        command_name = components.pop(0)

        return ParsedCommand(name=command_name, parameters=components)


    def _execute_command(self, command: ParsedCommand):

        try:
            # split the command line into components
            #  - command name
            #  - parameters
            cmd_descriptor = self._commands[command.name]
            if len(command.parameters) == 0:
                cmd_descriptor.f()
            else:
                # here we'll store the parameters to pass to the function with the correct type
                # in ParsedCommand we don't store the type but only the value as a string
                arguments = cmd_descriptor.cast_arguments(command.parameters)
                cmd_descriptor.f(*arguments)
        except ValueError as ex:
            print(self._draw_panel("Error", f"Error in parameters: {ex}"))
        except KeyError:
            print(self._draw_panel("Error", f"Command {command.name} not found. Type '?' for help."))
        except Exception as ex:
            print(self._draw_panel("Error", f"An error occurred: {ex}"))


    def run(self) -> None:
        # clear the screen and print the hello message (if exists)
        print("\033[H\033[J", end="")
        if self._hello_message != "":
            print(self._hello_message)
        while True:
            # TODO substitute input with a for loop getchar
            # in order to support up key and history command
            command = input(f"{self._prompt} ")
            if command == '':
                continue

            parsed_command = self._parse_command_line(command)

            match parsed_command.name:
                case 'exit':
                    break
                case '?':
                    if len(parsed_command.parameters):
                        print(self._help_specific_command(parsed_command.parameters[0]))
                    else:
                        print(self._help())
                    continue
                case _:  # wildcard - simile ad un else, deve stare alla fine
                    if parsed_command.name not in self._commands:
                        print(self._draw_panel("Error", f"Command {parsed_command.name} not found. Type '?' for help."))
                        continue
                    self._execute_command(parsed_command)
