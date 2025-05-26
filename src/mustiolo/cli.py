
from collections.abc import Callable
import os
import sys
# used to have history and arrow handling
import readline

from mustiolo.exception import *
from mustiolo.message_box import BorderStyle, draw_message_box
from mustiolo.models.command import ParsedCommand
from mustiolo.models.menu import MenuDescriptor, _ROOT_MENU

class CLI:

    def __init__(self, hello_message: str = "", prompt: str = ">", autocomplete: bool = True) -> None:
        self._hello_message = hello_message
        self._prompt = prompt
        self._autocomplete = autocomplete
        self._exit = False
        self._reserved_commands = ["?", "exit"] 
        self._columns = os.get_terminal_size().columns
        # contains all the menus by name
        self._menu = None
        self._istantiate_root_menu()


    def _completer(self, text, state):
        """Autocomplete function for the readline module."""
        options = [command for command in self._menu.get_commands().keys() if command.startswith(text)]
        if state < len(options):
            return options[state] + " "
        else:
            return None

    def _set_autocomplete(self):
        if self._autocomplete:
            match sys.platform:
                case 'linux':
                    readline.parse_and_bind("tab: complete")
                    readline.parse_and_bind("set show-all-if-ambiguous on")
                    readline.set_completer(self._completer)
                case 'darwin':
                    readline.parse_and_bind("bind ^I rl_complete")
                    readline.parse_and_bind("set show-all-if-ambiguous on")
                    readline.set_completer(self._completer)
                case _:
                    print("Autocomplete not supported for this OS")


    def _istantiate_root_menu(self) -> None:
        """Instantiate the root menu and register it in the menues list.
        """
        self._menu = MenuDescriptor(name=_ROOT_MENU)
        self._menu.add_help_command()
        # register the exit command
        self._menu.register_command(self._exit_cmd, name="exit", help_short="Exit the program",
                                                  help_long="Exit the program")
        


    def _draw_panel(self, title: str , content: str, border_style: BorderStyle = BorderStyle.SINGLE_ROUNDED, columns: int = None) -> str:
        """Draw panel with a title and content.
        """
        cols = self._columns
        if columns is not None:
            cols = columns
        return draw_message_box(title, content, border_style, cols)


    def command(self, name: str = None, help_short: str = None, help_long: str = None) -> None:
        """Decorator to register a command in the __root_ CLI menu."""

        if name in self._reserved_commands:
            raise Exception(f"'{name}' is a reserved command name")

        def decorator(funct: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                funct(*args, **kwargs)

            self._menu.register_command(funct, name, help_short, help_long)
            return wrapper
        return decorator


    def change_prompt(self, prompt: str) -> None:
        self._prompt = prompt


    def _exit_cmd(self) -> None:
        """Exit the program."""
        self._exit = True


    def _handle_exception(self, ex) -> None:
        print(self._draw_panel("Error", str(ex)))


    def _parse_command_line(self, command_line: str) -> ParsedCommand:
        components = command_line.split()
        if len(components) == 0:
            return ParsedCommand(name="", parameters=[])
        command_name = components.pop(0)

        return ParsedCommand(name=command_name, parameters=components)


    def _execute_command(self, command: ParsedCommand):

        try:
            # split the command line into components
            #  - command name
            #  - parameters
            cmd_descriptor = self._menu.get_command(command.name)
            if len(command.parameters) == 0:
                cmd_descriptor.f()
            else:
                # here we'll store the parameters to pass to the function with the correct type
                # in ParsedCommand we don't store the type but only the value as a string
                arguments = cmd_descriptor.cast_arguments(command.parameters)
                cmd_descriptor.f(*arguments)
        except CommandNotFound as ex:
            print(self._draw_panel("Error", f"{ex}"))
            self._menu_stack[-1].help()
            return
        except ValueError as ex:
            print(self._draw_panel("Error", f"Error in parameters: {ex}"))
        except Exception as ex:
            print(self._draw_panel("Error", f"An error occurred: {ex}"))


    def run(self) -> None:

        # clear the screen and print the hello message (if exists)
        print("\033[H\033[J", end="")
        self._set_autocomplete()

        if self._hello_message != "":
            print(self._hello_message)
        while self._exit is False:
            command = input(f"{self._prompt} ")
            if command == '':
                continue

            parsed_command = self._parse_command_line(command)
            if parsed_command.name == "":
                continue
            self._execute_command(parsed_command)

