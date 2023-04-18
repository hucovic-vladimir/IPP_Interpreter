# Autor: Vladimír Hucovič
# Login: xhucov00


from typing import Union
from dataTypes import *
from exceptions import *

# Třída reprezentující rámec pro proměnné v IPPCode23
class Frame():
    def __init__(self) -> None:
        # Slovnik proměnných
        self.variables: dict[str, Union[IPPInt, IPPFloat, IPPBool, IPPString, Nil, None]] = {}

    def __str__(self) -> str:
        return str(self.variables)
    # Přidá proměnnou do rámce. Pokud proměnná již existuje, je vyhozena výjimka 
    def AddVariable(self, variableName: str) -> None:
        if(variableName in self.variables):
            raise VariableRedefenitionError(f"Redefinice promenne {variableName}!")
        self.variables.update({variableName: None})
   
    # Získá hodnotu proměnné. Pokud proměnná neexistuje, je vyhozena výjimka
    def GetVariableValue(self, name: str) -> Union[IPPInt, IPPFloat, IPPBool, IPPString, Nil, None]: 
        if(name not in self.variables):
            raise MissingVariableError(f"Chyba: Promenna {name} neni definovana!") 
        return self.variables[name]
    
    # Nastaví hodnotu proměnné. Pokud proměnná neexistuje, je vyhozena výjimka
    def UpdateVariable(self, name: str, value: Union[IPPInt, IPPString, IPPBool, IPPFloat, Nil]):
        if(name not in self.variables):
            raise MissingVariableError(f"Chyba: Promenna {name} neni definovana!")
        self.variables[name] = value

    # Získá typ proměnné. Pokud proměnná neexistuje, je vyhozena výjimka
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

    # Spočítá inicializované proměnné v rámci
    def GetInitializedVarsCount(self):
        count = 0
        for var in self.variables:
            if(self.variables[var] is not None):
                count += 1
        return count
