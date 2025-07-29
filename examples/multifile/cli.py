from mustiolo.cli import CLI, MenuGroup
from math_commands import math_submenu
from greeting_command import greeting

cli = CLI()

# add math submenu to the root menu
cli.add_group(math_submenu)
cli.add_group(greeting)

if __name__ == "__main__":
    cli.run()
