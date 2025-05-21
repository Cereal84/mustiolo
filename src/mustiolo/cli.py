
from collections.abc import Callable
import os
from mustiolo.message_box import BorderStyle, draw_message_box
from mustiolo.models.command import CommandModel, ParsedCommand
from mustiolo.models.menu import MenuDescriptor, _ROOT_MENU
from mustiolo.utils import parse_parameters

class TinyCLI:

    def __init__(self, hello_message: str = "Welcome", prompt: str = ">"):
        self._hello_message = hello_message
        self._prompt = prompt
        self._exit = False
        self._columns = os.get_terminal_size().columns
        self._commands = {}
        # this is used to align the help menu
        self._max_command_length = 0
        self._menues = {}
        # istance of the root menu
        self._menues[_ROOT_MENU] = MenuDescriptor(name=_ROOT_MENU)

    def _istantiate_root_menu(self) -> None:
        """Instantiate the root menu and register it in the menues list.
        """
        self._menues[_ROOT_MENU] = MenuDescriptor(name=_ROOT_MENU)
        # register the root menu in the commands list
        self._commands[_ROOT_MENU] = CommandModel(name="?", f=self._help_cmd, help_short="Show this help",
                                                 help_long="Show this help", parameters=[])
        # register the exit command
        self._commands["exit"] = CommandModel(name="exit", f=self._exit_cmd, help_short="Exit the program",
                                                  help_long="Exit the program", parameters=[])


    def _draw_panel(self, title: str , content: str, border_style: BorderStyle = BorderStyle.SINGLE_ROUNDED, columns: int = None) -> str:
        """Draw panel with a title and content.
        """
        cols = self._columns
        if columns is not None:
            cols = columns
        return draw_message_box(title, content, border_style, cols)


    def command(self, name: str = None, help_short: str = None, help_long: str = None) -> None:
        """Decorator to register a command in the __root_ CLI menu."""
        def decorator(funct: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                try:
                    funct(*args, **kwargs)
                except Exception as ex:
                    self._handle_exception(ex)

            self._menues[_ROOT_MENU].register_command(wrapper, funct, name, help_short, help_long)
            return wrapper
        return decorator

    def change_prompt(self, prompt: str) -> None:
        self._prompt = prompt

    def _exit_cmd(self) -> None:
        """Exit the program."""
        self._exit = True

    def _help(self) -> str:
        return "\n".join([ command.short_help(self._max_command_length) for _, command in self._commands.items()])

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
        while self._exit is False:
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
