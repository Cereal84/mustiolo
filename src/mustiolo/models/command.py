from dataclasses import dataclass
from typing import Any, List, Callable

_pythonType2String = {}
_pythonType2String[str] = "STRING"
_pythonType2String[int] = "INTEGER"
_pythonType2String[float] = "NUMBER"
_pythonType2String[bool] = "BOOLEAN"


@dataclass
class ParsedCommand:
    name : str
    parameters: List[Any]


@dataclass
class ParameterModel:
    name: str
    ptype: Any
    default: Any

    def __str__(self) -> str:
        msg = [f"\t\t{self.name.upper()}\tType {_pythonType2String[self.ptype]} "]
        if self.default is not None:
            msg.append(f"[optional] [default: {self.default}]")
        else:
            msg.append("[required]")
        return "".join(msg)

    def  convert_to_type(self, value: str) -> Any:
        # here we try to convert the value to the correct type
        # if it fails an exception is raised
        return self.ptype(value)


@dataclass
class CommandModel:
    """This class is used as Model for help message and
       for handle checks on the command.

       'f' contains doc, name and parameters so in this case we're duplicating
       those informations
    """
    name: str
    f: Callable
    help_short: str
    help_long: str
    # TODO: change parameters into arguments
    parameters: List[ParameterModel]

    def __str__(self) -> str:
        help_msg = [f"{self.help_long}\n\n{self.name} {' '.join([p.name.upper() for p in self.parameters])}"]
        if len(self.parameters) == 0:
            return help_msg[0]

        help_msg.append("\nParameters:")
        help_msg.extend([ str(p) for p in self.parameters])
        return "\n".join(help_msg)

    def short_help(self, padding: int) -> str:
        return f"{self.name.ljust(padding)}\t{self.help_short}"

    def long_help(self) -> str:
        return f"{self.name}\n\n{self.help_long}\n\nParameters:\n" + "".join([ str(p) for p in self.parameters])

    def get_mandatory_parameters(self) -> List[ParameterModel]:
        return [ param for param in self.parameters if param.default is None ]

    def get_optional_parameters(self) -> List[ParameterModel]:
        return [ param for param in self.parameters if param.default is not None ]

    def cast_arguments(self, args: List[str]) -> List[Any]:
        """ This function cast the arguments to the correct type.
            It raises an exception if the number of arguments is less than the
            number of mandatory parameters or if it's greater of the total.
        """
        if len(args) < len(self.get_mandatory_parameters()):
            raise Exception("Missing parameters")
        if len(args) > len(self.parameters):
            raise Exception("Too many parameters")

        return [ self.parameters[index].ptype(args[index]) for index in range(0, len(args)) ]