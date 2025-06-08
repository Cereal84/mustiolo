from mustiolo.cli import CLI, MenuGroup

from typing import List

cli = CLI()

# add the commands to the root menu
@cli.command()
def greet(name: str = "World"):
    """Greet a user by name."""
    print(f"Hello {name}!")

math_submenu = MenuGroup("math", "Some math operations", "Some math operations")
@math_submenu.command()
def add(a: int, b: int):
    """Add two numbers."""
    print(f"The result is: {a + b}")

@math_submenu.command()
def add_list(numbers: List[int]):
    """Add N numbers."""
    tot = sum(numbers)
    print(f"The result is: {tot}")

@math_submenu.command()
def sub(a: int, b: int):
    """Subtract two numbers."""
    print(f"The result is: {a - b}")

# add math submenu to the root menu
cli.add_group(math_submenu)


if __name__ == "__main__":
    cli.run()