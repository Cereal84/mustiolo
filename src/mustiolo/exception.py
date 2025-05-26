

class CommandNotFound(Exception):
    def __init__(self, command: str):
        self._command = command
        super().__init__()

    def __str__(self):
        return f"Command '{self._command}' does not exists."


class CommandDuplicate(Exception):

    def __init__(self, command: str, filename: str, lineno: int):
        self.command = command
        self.filename = filename
        self.lineno = lineno
        super().__init__()

    def __str__(self) -> str:
        return f"Command '{self.command}' is already defined. Check '{self.filename}:{self.lineno}'"


class CommandReserved(Exception):
    def __init__(self, command: str):
        self.command = command
        super().__init__()

    def __str__(self):
        return f"Command '{self.command}' is a reserved one."



