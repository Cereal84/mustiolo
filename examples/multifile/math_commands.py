from mustiolo.cli import MenuGroup
from typing import List


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