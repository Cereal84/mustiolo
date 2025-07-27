from mustiolo.cli import CLI, MenuGroup
from math_commands import math_submenu

cli = CLI()

# add the commands to the root menu
@cli.command()
def greet(name: str = "World"):
    """<menu>Greet a user by name.</menu>"""
    print(f"Hello {name}!")
    
# add math submenu to the root menu
cli.add_group(math_submenu)

if __name__ == "__main__":
    cli.run()