from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Dict, List


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
         msg = f"\n\t\t{self.name.upper()}\tType {pythonType2String[self.ptype]}"
         if self.default is not None:
              msg += f", Required: False Default: {self.default}"
         else:
              msg += ", Required: True"
         msg += "\n"
         return msg


@dataclass
class CommandModel:
    """This class is used as Model for help message and
       for handle checks on the command.

       'f' contains doc, name and parameters so in this case we're duplicating
       those informations
    """
    name: str
    f: Callable
    doc: str
    parameters: List[ParameterModel] 

    def __str__(self) -> str:
        help_msg = f"""{self.name} {' '.join([p.name.upper() for p in self.parameters])}"""
        if len(self.parameters):
            help_msg += "\n\nParameters:\n"
        help_msg += "".join([ str(p) for p in self.parameters])
        return help_msg

    def short_help(self) -> str:
        return f"{self.name}\t{self.doc}"


class TinyCLI:

    def __init__(self, hello_message: str = "Welcome to TinyCLI", prompt: str = ">"):
        self._hello_message = hello_message
        self._prompt = prompt
        self._commands = {}


    def command(self, f: Callable) -> None:
        """This is the decorator used to register a CLI command"""
        def wrapper(*args, **kwargs):
            """
            """
            try:
                f(*args, **kwargs)
            except Exception as ex:
                self._handle_exception(ex) 

        self._register_command(wrapper, f)
        return wrapper


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


    def _register_command(self, f_wrapper: Callable, f: Callable) -> None:
        if f.__name__ in self._commands:
            raise Exception(f"Command {f.__name__} already exists")
        parameters = self._parse_parameters(f)
        model = CommandModel(name=f.__name__, f=f_wrapper, doc=f.__doc__, parameters=parameters)
        self._commands[f.__name__] = model


    def _help(self) -> str:
        msg = "Commands:\n\n\t"
        msg +=  "\n\t".join([ command.short_help() for _, command in self._commands.items()])
        return msg

    def _help_specific_command(self, cmd: str) -> str:
        if cmd not in self._commands:
            # substitute with a custom exception
            print(f"Error: Command '{cmd}' not exists")
            print(self._help())
            return
         
        return str(self._commands[cmd])

    def _handle_exception(self, ex) -> None:
        print(f"Error: {ex}")


    def _parse_command_line(self, command_line: str) -> ParsedCommand:
        components = command_line.split()
        command_name = components.pop(0)

        return ParsedCommand(name=command_name, parameters=components)


    def _execute_command(self, command: ParsedCommand):
        # split the command line into components
        #  - command name
        #  - parameters
        if len(command.parameters) == 0:
              self._commands[command.name].f()
        else:
              # before to execute the function we need to check the parameters:
              #  - param missing
              #  - param type
              self._commands[command.name].f(*command.parameters)


    def run(self) -> None:
        # clear the screen and print the hello mesage (if exists)
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
                    if parsed_command.name in self._commands:
                        self._execute_command(parsed_command)
