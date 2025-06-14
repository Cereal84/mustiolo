
from collections.abc import Callable
import os
import sys
# used to have history and arrow handling
import readline

from mustiolo.exception import  CommandNotFound
from mustiolo.message_box import BorderStyle, draw_message_box
from mustiolo.models.parameters import ParsedCommand
from mustiolo.models.command import CommandGroup


class MenuGroup:

    def __init__(self, name: str = "", menu: str = "", usage: str = ""):
        self._group = CommandGroup(name, menu, usage)

    def command(self, name: str = None, menu: str = "", usage: str = ""):
        def decorator(f):
            self._group.register_command(f, name, menu, usage)
            return f
        return decorator

    def add_group(self, group: CommandGroup) -> None:
        self._group.add_command_group(group)

    def get_group(self) -> CommandGroup:
        return self._group


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
        """
        Autocomplete for nested CommandGroups.
        """
        # TODO: Implement a better autocomplete function, this code is just a starting point
        #       full of duplicated logic.

        current_group = self._menu
        cmd = None
        options = None
        is_help_command = False

        # Get the current input line and cursor position
        line_buffer = readline.get_line_buffer()
        split_line = line_buffer.strip().split()

        # in case of help command ('?') as first commmand we need to remove it
        # in order to have the correct command path and autocomplete
        if len(split_line) > 0 and split_line[0] == "?":
            split_line.pop(0)
            is_help_command = True

        # we have this cases
        # 1. no split_line, so we are at the root menu
        # 2. split_line and the last element is a command, so we need to autocomplete the command
        # 3. split_line and the last element is a group, so we need to shows all its commands
        # 4. split_line and the last element is a partial string so we need to autocomplete the command

        # []
        # [partial_command]
        # [command]
        # [command, ...,  partial_command]
        if len(split_line) == 0:
            options = [name for name in current_group.get_commands().keys()]
            if is_help_command:
                options.remove("?")
            options.sort()
            return options[state] + " "

        elif len(split_line) == 1:
            # we can have a full command, a partial command or a group
            if current_group.has_command(split_line[0]):
                # is a complete command.
                # get it and check if it is a CommandGroup
                cmd = current_group.get_command(split_line[0])
                if isinstance(cmd, CommandGroup):
                    # get all the subcommands for this group
                    options = [name for name in cmd.get_commands().keys()]
                else:
                    # get only the command that starts with the partial command
                    options = [name for name in current_group.get_commands().keys() if name.startswith(split_line[-1])]

            else:
                # is not a complete command, so we need to check if a subcommand starts with it
                # in the current group
                options = [name for name in current_group.get_commands().keys() if name.startswith(split_line[-1])]

        else:
            # Traverse the command path to the deepest CommandGroup
            for part in split_line[:-1]:
                if current_group.has_command(part.strip()):
                    cmd = current_group.get_command(part.strip())
                    if isinstance(cmd, CommandGroup):
                        current_group = cmd
                        continue
                    else:
                        # we have a command but we need a group
                        return None
                else:
                    # we are in the middle of the path but there is no command
                    return None
        
            # we've traversed the path and arrived at the last CommandGroup
            check_cmd = split_line[-1].strip()

            # so we need to check if it is a complete command or a partial command
            if current_group.has_command(check_cmd):
                # is a complete command
                cmd = current_group.get_command(check_cmd)
                if isinstance(cmd, CommandGroup):
                    # get all the subcommands for this group
                    options = [name for name in current_group.get_commands().keys()]
                else:
                    # get only the command that starts with the partial command
                    options = [name for name in current_group.get_commands().keys() if name.startswith(split_line[-1])] 
            else:
                # is a partial command
                options = [name for name in current_group.get_commands().keys() if name.startswith(split_line[-1])]
                
        options.sort()

        if len(split_line) == 0:
            return options

        if state < len(options):
            if options[state] == split_line[-1]:
                return None
            return options[state] + " "
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
        self._menu = CommandGroup(name="__root__", menu="",  usage="")
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

    def command(self, name: str = None, menu: str = "", usage: str = "") -> None:
        """Decorator to register a command in the __root_ CLI menu."""

        if name in self._reserved_commands:
            raise Exception(f"'{name}' is a reserved command name")

        def decorator(funct: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                funct(*args, **kwargs)

            self._menu.register_command(funct, name, menu, usage)
            return wrapper
        return decorator

    def add_group(self, group: MenuGroup) -> None:
        self._menu.add_command_group(group.get_group())


    def change_prompt(self, prompt: str) -> None:
        self._prompt = prompt


    def _exit_cmd(self) -> None:
        """Exit the program."""
        self._exit = True


    def _handle_exception(self, ex) -> None:
        print(self._draw_panel("Error", str(ex)))


    def _parse_command_line(self, command_line: str) -> ParsedCommand:
        """"
        Parse the command line and return a ParsedCommand object."""
        components = command_line.split()
        if len(components) == 0:
            return ParsedCommand(name="", parameters=[])
        command_name = components.pop(0)
        return ParsedCommand(name=command_name, parameters=components)


    def _execute_command(self, current_menu: CommandGroup,command: ParsedCommand):

        try:
            # split the command line into components
            #  - command name
            #  - parameters
            cmd_descriptor = current_menu.get_command(command.name)
            if len(command.parameters) == 0:
                cmd_descriptor.f()
            else:
                # special case which I want to change and make it works like the others
                if command.name == "?":
                    cmd_descriptor.f(command.parameters)
                    return
                
                arguments = cmd_descriptor.cast_arguments(command.parameters)
                cmd_descriptor.f(*arguments)
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
            
            command_path = command_path.split()
            # here we have a list of string that is the command path
            # plus eventually some parameters.
            # So we need to goes trought the menu command by command
            # and stop when we found a command that has no subcommand
            # and call that command with the parameters.
            current_menu = self._menu
            command = None

            try:
                while True:
                    command = command_path.pop(0)
                    if not current_menu.has_command(command):
                        raise CommandNotFound(command)

                    entry = current_menu.get_command(command)
                    if isinstance(entry, CommandGroup):
                        # we need to go to the next sub group
                        current_menu = entry
                        continue

                    break
                # here current_menu is a Command
                parsed_command = self._parse_command_line(command + " " + (" ".join(command_path)))
                if parsed_command.name == "":
                    continue
                self._execute_command(current_menu, parsed_command)

            except Exception as ex:
                print(self._draw_panel("Error", f"An error occurred: {ex}"))

            
