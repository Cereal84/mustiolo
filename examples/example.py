from mustiolo.cli import TinyCLI

cli = TinyCLI()

@cli.command()
def greet(name: str = "World"):
    """Greet a user by name."""
    print(f"Hello {name}!")


@cli.command(name="sum", help_short="Add two numbers", help_long="Add two numbers and print the result.")
def add(a: int, b: int):
    print(f"The result is: {a + b}")

if __name__ == "__main__":
    cli.run()
