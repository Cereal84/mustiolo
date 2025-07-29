from mustiolo.cli import CommandCollection

greeting = CommandCollection()


@greeting.command()
def greet(name: str = "World"):
    """<menu>Greet a user by name.</menu>"""
    print(f"Hello {name}!")
