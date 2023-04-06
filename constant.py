from typing import List, Any, Union
from enum import Enum

class Type(Enum):
    INT = 1
    FLOAT = 2
    STRING = 3
    NIL = 4

class Constant:
    def __init__(self, type: Type, value: Union[str, int, float, None] ) -> None:
        self.type = type 
        self.value = value

    def __str__(self) -> str:
        if(self.type == Type.NIL):
            return "nil"
        return f"{self.value}"

