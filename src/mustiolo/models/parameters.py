from dataclasses import dataclass
from typing import Any, List, get_args, get_origin

from mustiolo.exception import ParameterWrongType


@dataclass
class ParsedCommand:
    name : str
    parameters: List[Any]


def ptype_to_str(ptype: Any) -> str:
    # return ptype.__name__.upper()
    if ptype is str:
        return "STRING"
    if ptype is int:
        return "INTEGER"
    if ptype is float:
        return "NUMBER"
    if ptype is bool:
        return "BOOLEAN"
    if get_origin(ptype) is list:
        type_str = "LIST"
        if get_args(ptype) is not None:
            type_str += f"[{ptype_to_str(get_args(ptype)[0])}]"
        return type_str
    return str(ptype)


@dataclass
class ParameterModel:
    name: str
    ptype: Any
    default: Any

    def __str__(self) -> str:
        # TODO handle list type and subtypes
        msg = [f"\t\t{self.name.upper()}\tType {ptype_to_str(self.ptype)} "]
        if self.default is not None:
            msg.append(f"[optional] [default: {self.default}]")
        else:
            msg.append("[required]")
        return "".join(msg)

    def convert_to_type(self, value: str) -> Any:
        
        try:
            # here we try to convert the value to the correct type
            # if it fails an exception is raised
            if get_origin(self.ptype) is list:
                values = value.split(',')
                subtype = get_args(self.ptype)[0] if len(get_args(self.ptype)) > 0 else None
                if subtype is not None:
                    return [subtype(v) for v in values]
                return values    
            return self.ptype(value)
        except Exception:
            raise ParameterWrongType(value, ptype_to_str(self.ptype))
