from mustiolo.cli import CLI

cli = CLI()

@cli.command()
def greet(name: str = "World"):
    """<menu>Greet a user by name.</menu>"""
    print(f"Hello {name}!")


@cli.command(name="sum", menu="Sum two numbers", usage="Add two numbers and print the result.", metavars={"a": "addend1", "b": "addend2"})
def add(a: int, b: int):
    print(f"The result is: {a + b}")

@cli.command(name="sub", menu="Subtraction two numbers", usage="Subtract two numbers and print the result.", metavars={"a": "minuend", "b": "subtrahend"})
def sub(a: int, b: int):
    print(f"The result is: {a - b}")


if __name__ == "__main__":
    cli.run()
