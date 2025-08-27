
import os

# used to have history and arrow handling
import readline
import sys
from collections.abc import Callable
from typing import Union

from mustiolo.exception import CommandNotFound
from mustiolo.message_box import BorderStyle, draw_message_box
from mustiolo.models.command import CommandGroup, SubCommandGroup
from mustiolo.models.parameters import ParsedCommand

class CommandCollection:
    """This class is used to collect all the commands and command groups."""
    def __init__(self):
        self._group = CommandGroup()

    def command(self, name: Union[str, None] = None, alias: str = "",
                metavars: dict[str, str] = {},
                menu: str = "", 
                usage: str = "") -> Callable:
        def decorator(f):
            self._group.register_command(f, name, alias, metavars, menu, usage)
            return f

        return decorator

    def metavar(self, name: str, description: str) -> Callable:
        """Decorator to register a metavar in the command group."""
        def decorator(f):
            self._group.register_metavar(name, description)
            return f

        return decorator

    def add_commands(self, group: 'CommandCollection') -> None:
        self._group.include_commands(group.get_group())

    def get_group(self) -> CommandGroup:
        return self._group


class MenuGroup:

    def __init__(self, name: str = "", menu: str = "", usage: str = ""):
        self._group = SubCommandGroup(name, menu, usage)

    def command(self, name: Union[str, None] = None, alias: str = "",
                metavars: dict[str, str] = {},
                menu: str = "", usage: str = "") -> Callable:
        def decorator(f):
            self._group.register_command(f, name, alias, metavars, menu, usage)
            return f
        return decorator

    def add_commands(self, commands: Union[CommandCollection, 'MenuGroup']) -> None:
        self._group.include_commands(commands.get_group())

    def get_group(self) -> SubCommandGroup:
        return self._group


class CLI:

    def __init__(self, hello_message: str = "", prompt: str = ">", autocomplete: bool = True) -> None:
        self._hello_message = hello_message
        self._prompt = prompt
        self._autocomplete = autocomplete
        self._exit = False
        self._reserved_commands = ["?", "exit"] 
        try:
            self._columns = os.get_terminal_size().columns
        except OSError:
            # If we cannot get the terminal size, we default to 80 columns
            self._columns = 80
        # contains all the menus by name
        self._menu : Union[CommandGroup, SubCommandGroup] = None
        self._istantiate_root_menu()

    def _completer(self, text: str, state: int):
        """
        Autocomplete function for the CLI.
        This function is used by readline to provide autocompletion.
        """
        if not self._autocomplete:
            return None
        
        curr_subtree = self._menu

        # split input into tokens
        line_buffer = readline.get_line_buffer()
        tokens = line_buffer.strip().split()

        # ideally we should complete the last token.
        # if there are no tokens, we return the list of commands.
        # Otherwise we need to traverse the command path
        # and return the list of commands or subcommands that match the last token.

        # We need to handler the case of help command ('?') as first token removing it
        if len(tokens) > 0 and tokens[0] == "?":
            tokens.pop(0)

        # We traverse the list of tokens until we reach the last one.
        # Doing it we need to check if the tokens are existing commands (os subcommands).
        # If the current token (which is not the last one) is not a SubCommandGroup we need to
        # return None, because we cannot complete the command.
        # Othersiwe we can continue to traverse the command path.

        if len(tokens) == 0:
            # no tokens, so we return the list of commands
            options = [name for name in curr_subtree.commands.keys()]
            if "?" in options:
                options.remove("?")
            options.sort()
            if state < len(options):
                return options[state] + " "
            return None

        for index, token in enumerate(tokens):
            if index == len(tokens) - 1:
                # we are at the last token, so we need to check if it is a SubCommandGroup
                # or single command.

                # TODO: get_command() raises an exception if the
                # command is not found... maybe we should use has_command() whhich
                # returns boolean and/or change get_command() to return None.
                # This choice affects the run() method.
                try:
                    cmd = curr_subtree.get_command(token)

                    # it is a valid command
                    if isinstance(cmd, SubCommandGroup):
                        # we return the list of subcommands for this group
                        options = [name for name in cmd.commands.keys()]
                        options.sort()

                        if state < len(options):
                            return options[state] + " "

                    return None
                except CommandNotFound:
                    # is not a complete command, so we need to check if the curr_subtree is
                    # a subcommand and get the list of commands that starts with the token
                    options = [name for name in curr_subtree.commands.keys() if name.startswith(token)]
                    options.sort()
                    if state < len(options):
                        return options[state] + " "
                    return None
                  
            
            # we are not at the last token, so we need to check if it is a SubCommandGroup
            try:
                next_branch = curr_subtree.get_command(token)
                if not isinstance(next_branch, SubCommandGroup):
                    # the current token is not a SubCommandGroup, so we cannot continue
                    return None
                curr_subtree = next_branch
            except CommandNotFound:
                return None

    def _set_autocomplete(self) -> None:

        if not self._autocomplete:
            return
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
        self._menu = SubCommandGroup(name="__root__", menu="",  usage="")
        self._menu.add_help_command()
        # register the exit command
        self._menu.register_command(self._exit_cmd, name="exit", menu="Exit the program",
                                                  usage="Exit the program")

    def _draw_panel(self, title: str , content: str, border_style: BorderStyle = BorderStyle.SINGLE_ROUNDED, columns: int = None) -> str:
        """Draw panel with a title and content.
        """
        cols = self._columns
        if columns is not None:
            cols = columns
        return draw_message_box(title, content, border_style, cols)

    def command(self, name: Union[str, None] = None, alias: str = "", 
                metavars: dict[str, str] = {},    
                menu: str = "", usage: str = "") -> None:
        """Decorator to register a command in the __root_ CLI menu."""

        if name in self._reserved_commands:
            raise Exception(f"'{name}' is a reserved command name")

        def decorator(funct: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                funct(*args, **kwargs)

            self._menu.register_command(funct, name, alias, metavars, menu, usage)
            return wrapper
        return decorator


    def add_commands(self, commands: Union[CommandCollection, MenuGroup]) -> None:
        """Add a collection of commands to the root menu."""
        if not isinstance(commands, (CommandCollection, MenuGroup)):
            raise TypeError("commands must be an instance of CommandCollection or MenuGroup")

        self._menu.include_commands(commands.get_group())

    def add_group(self, group: MenuGroup) -> None:
        self._menu.include_commands(group.get_group())


    def change_prompt(self, prompt: str) -> None:
        self._prompt = prompt


    def _exit_cmd(self) -> None:
        """Exit the program."""
        self._exit = True


    def _handle_exception(self, ex: Exception) -> None:
        print(self._draw_panel("Error", str(ex)))


    def _parse_command_line(self, command_line: str) -> ParsedCommand:
        """"
        Parse the command line and return a ParsedCommand object."""
        components = command_line.split()
        if len(components) == 0:
            return ParsedCommand(name="", parameters=[])
        command_name = components.pop(0)
        return ParsedCommand(name=command_name, parameters=components)


    def _execute_command(self, current_menu: SubCommandGroup, command: ParsedCommand) -> None:

        try:
            # split the command line into components
            #  - command name
            #  - parameters
            cmd_descriptor = current_menu.get_command(command.name)
            if len(command.parameters) == 0:
                cmd_descriptor()
            else:
                # special case which I want to change and make it works like the others
                if command.name == "?":
                    cmd_descriptor(command.parameters)
                    return
                
                arguments = cmd_descriptor.cast_arguments(command.parameters)
                cmd_descriptor(*arguments)
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
            command_path = input(f"{self._prompt} ")
            if command_path == '':
                continue
            
            commands = command_path.split()
            # here we have a list of string that is the command path
            # plus eventually some parameters.
            # So we need to goes trought the menu command by command
            # and stop when we found a command that has no subcommand
            # and call that command with the parameters.
            current_menu = self._menu
            command = None

            try:
                while True:
                    command = commands.pop(0)
                    if not current_menu.has_command(command):
                        raise CommandNotFound(command)

                    entry = current_menu.get_command(command)
                    if isinstance(entry, SubCommandGroup):
                        # we need to go to the next sub group
                        current_menu = entry
                        continue

                    break
                # here current_menu is a Command
                parsed_command = self._parse_command_line(command + " " + (" ".join(commands)))
                if parsed_command.name == "":
                    continue
                self._execute_command(current_menu, parsed_command)

            except Exception as ex:
                print(self._draw_panel("Error", f"An error occurred: {ex}"))

            
