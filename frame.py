from variable import *
from typing import List

class Frame():
    def __init__(self, type) -> None:
        self.type = type
        self.variables: List[Variable] = []

    def __str__(self) -> str:
        return self.type + " : " + str(self.variables)
    
    def AddVariable(self, variable: Variable):
        self.variables.append(variable)
    
    def GetVariable(self, name: str):
        for var in self.variables:
            if(var.name == name):
                return var
        return None
