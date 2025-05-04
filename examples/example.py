from main import TinyCLI


cli = TinyCLI()

@cli.command
def test():
    """Print 'test'"""
    print("Test") 

@cli.command
def hello(name: str = "John"):
    """Say Hello to name"""
    print(f"Hello {name}")

if __name__ == "__main__":
    cli.run()
