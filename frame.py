from variable import *
from typing import List, Union
import sys
class Frame():
    def __init__(self, type) -> None:
        self.type = type
        self.variables: dict[str, Variable] = {}

    def __str__(self) -> str:
        return self.type + " : " + str(self.variables)
    
    def AddVariable(self, variable: Variable):
        self.variables.update({variable.name: variable})
    
    def GetVariable(self, name: str):
        return self.variables.get(name)
    
    def UpdateVariable(self, name: str, value: Union[str, int, bool, float]):
        var = self.GetVariable(name)
        if(var is None):
            print(f"Chyba: Promenna {name} neni definovana!", file=sys.stderr)
            exit(54)
        self.variables[name].value = value

