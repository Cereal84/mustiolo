from mustiolo.cli import CLI, MenuGroup

from typing import List

cli = CLI()

# add the commands to the root menu
@cli.command()
def greet(name: str = "World"):
    """<menu>Greet a user by name.</menu>"""
    print(f"Hello {name}!")

# create a sub menu called 'math'
math_submenu = MenuGroup("math", "Some math operations", "Some math operations")

@math_submenu.command()
def add(a: int, b: int):
    """<menu>Add two numbers.</menu>"""
    print(f"The result is: {a + b}")

@math_submenu.command(alias="alist")
def add_list(numbers: List[int]):
    """<menu>Add N numbers.</menu>
       <usage>
       Makes the sum of N interger.
       </usage>
    """
    tot = sum(numbers)
    print(f"The result is: {tot}")

@math_submenu.command()
def sub(a: int, b: int):
    """<menu>Subtract two numbers.</menu>"""
    print(f"The result is: {a - b}")

# add math submenu to the root menu
cli.add_group(math_submenu)

if __name__ == "__main__":
    cli.run()
