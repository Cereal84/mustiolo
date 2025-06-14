

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


class CommandMissingMenuMessage(Exception):
    def __init__(self, fun_name: str, filename: str, lineno: int):
        self.function_name = fun_name
        self.filename = filename
        self.lineno = lineno
        super().__init__()
    
    def __str__(self):
        return f"Missing menu message in '{self.function_name}' at '{self.filename}:{self.lineno}'"


class ParameterWrongType(Exception):
    def __init__(self, value: str, expected_type: str):
        self.value = value
        self.expected_type = expected_type
        super().__init__()

    def __str__(self):
        return f"Get '{self.value}' expected {self.expected_type}"
    
class ParameterMissingType(Exception):
    def __init__(self, fun_name: str, filename: str, lineno: int):
        self.function_name = fun_name
        self.filename = filename
        self.lineno = lineno
        super().__init__()
    
    def __str__(self):
        return f"Function '{self.function_name}' at '{self.filename}:{self.lineno}' has a parameter without type"