from mustiolo.cli import CLI

cli = CLI()

@cli.command()
def greet(name: str = "World"):
    """Greet a user by name."""
    print(f"Hello {name}!")


@cli.command(name="sum", menu="Sum two numbers", usage="Add two numbers and print the result.")
def add(a: int, b: int):
    print(f"The result is: {a + b}")


if __name__ == "__main__":
    cli.run()
