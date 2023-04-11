from typing import List, Union
from dataTypes import *
from exceptions import *
import sys
class Frame():
    def __init__(self) -> None:
        self.variables: dict[str, Union[IPPInt, IPPFloat, IPPBool, IPPString, Nil, None]] = {}

    def __str__(self) -> str:
        return str(self.variables)
    
    def AddVariable(self, variableName: str):
        if(variableName in self.variables):
            raise VariableRedefenitionError(f"Redefinice promenne {variableName}!")
        self.variables.update({variableName: None})
    
    def GetVariableValue(self, name: str) -> Union[IPPInt, IPPFloat, IPPBool, IPPString, Nil, None]: 
        if(name not in self.variables):
            raise MissingVariableError(f"Chyba: Promenna {name} neni definovana!") 
        return self.variables[name]
    
    def UpdateVariable(self, name: str, value: Union[IPPInt, IPPString, IPPBool, IPPFloat, Nil]):
        if(name not in self.variables):
            raise MissingVariableError(f"Chyba: Promenna {name} neni definovana!")
        self.variables[name] = value

    def GetVariableType(self, name: str) -> str:
        if(name not in self.variables):
            raise MissingVariableError(f"Chyba: Promenna {name} neni definovana!")
        if(isinstance(self.variables[name], IPPInt)):
            return "int"
        elif(isinstance(self.variables[name], IPPFloat)):
            return "float"
        elif(isinstance(self.variables[name], IPPString)):
            return "string"
        elif(isinstance(self.variables[name], IPPBool)):
            return "bool"
        elif(isinstance(self.variables[name], Nil)):
            return "nil"
        elif(self.variables[name] is None):
            return ""
        else:
            raise InterpreterInternalError("Chyba: Neznama chyba pri ziskavani typu promenne!")

