from frame import Frame
from exceptions import *
from argument import Argument, VarName
from typing import Optional
from dataTypes import *
from stack import Stack

# Data pro interpret
class InterpreterData:
    def __init__(self, userInputStream):
        # Vstupní stream pro instrukci READ
        self.userInputStream = userInputStream
        # Ukazatel na další prováděnou instrukci
        self.instructionPointer: int = 0
        # Globální rámec
        self.globalFrame: Frame = Frame()
        # Lokální rámec
        self.tempFrame: Optional[Frame] = None
        # Zásobník rámců
        self.frameStack: Stack = Stack()
        # Datový zásobník
        self.dataStack: Stack = Stack()
        # Zásobník volání
        self.callStack: Stack = Stack()
        # slovnik navesti
        self.labels: dict[IPPString, int] = {}

    # Získá počet inicializovaných proměnných ve všech rámcích
    def GetInitializedVarsCount(self) -> int:
        gfCount = self.globalFrame.GetInitializedVarsCount()
        tfCount = self.tempFrame.GetInitializedVarsCount() if self.tempFrame is not None else 0
        lfCount = self.frameStack.top().GetInitializedVarsCount() if not self.frameStack.empty() else 0
        return gfCount + tfCount + lfCount

    # Vytvoří dočasný rámec
    def CreateFrame(self) -> None:
        self.tempFrame = Frame()

    # Uloží dočasný rámec na zásobník
    def PushFrame(self) -> None:
        if(self.tempFrame is None):
            raise MissingFrameError("Chyba: Pokus o ulozeni neexistujiciho ramce na zasobnik!")
        self.frameStack.push(self.tempFrame)
        self.tempFrame = None

    # Uloží vrchní rámec ze zásobníku do dočasného rámce
    def PopFrame(self) -> None:
        if(self.frameStack.empty()):
            raise MissingFrameError("Chyba: Pokus o ziskani ramce z prazdneho zasobniku!")
        self.tempFrame = self.frameStack.pop()
    
    # Získá index daného návěští podle jména
    def GetJumpDestination(self, label: str) -> int:
        if(label not in self.labels):
            raise UndefinedLabelError(f"Chyba: Navesti {label} neni definovano!")
        return self.labels[label]
   
    # Přidá proměnnou do rámce (rámec je součástí jména proměnné)
    def AddVariable(self, varName: str) -> None:
        split = varName.split("@")
        if(len(split) != 2):
            raise XMLInputError("Chyba: Neplatny nazev promenne!")
        frameType = split[0]
        varName = split[1] 
        frame = self._getFrame(frameType)
        frame.AddVariable(varName)

    # Aktualizuje hodnotu proměnné
    def UpdateVariable(self, varName: str, value: Union[IPPString, IPPInt, IPPFloat, IPPBool, Nil]) -> None:
        frameType = varName.split("@")[0]
        varName = varName.split("@")[1]
        frame = self._getFrame(frameType)
        frame.UpdateVariable(varName, value)

    def GetUserInputStream(self):
        return self.userInputStream

    def GetInstructionPointer(self) -> int:
        return self.instructionPointer
    
    def SetInstructionPointer(self, value) -> None:
        self.instructionPointer = value
    
    def PushDataStack(self, value):
        self.dataStack.push(value)
    
    # Získá hodnotu z vrcholu datového zásobníku
    def PopDataStack(self) -> Union[IPPString, IPPInt, IPPFloat, IPPBool, Nil]:
        if(self.dataStack.empty()):
            raise MissingValueError("Chyba: Pristup k prazdnemu datovemu zasobniku!")
        return self.dataStack.pop()
   
    def ClearDataStack(self):
        self.dataStack.clear()
    
    # Uloží hodnotu do zásobníku volání
    def PushCallStack(self, value: int) -> None:
        self.callStack.push(value)

    # Získá hodnotu z vrcholu zásobníku volání
    def PopCallStack(self):
        if(self.callStack.empty()):
            raise MissingValueError("Chyba: Volani funkce RETURN bez predchoziho volani CALL!")
        return self.callStack.pop()
    
    # Vrátí typ uložený v proměnné daného jména
    def GetVariableType(self, varName: str) -> str:
        frame = varName.split("@")[0]
        name = varName.split("@")[1]
        return self._getFrame(frame).GetVariableType(name)

    # Vrátí hodnotu uloženou v proměnné daného jména
    def GetVariableValue(self, varName: str) -> Union[IPPString, IPPInt, IPPFloat, IPPBool, Nil]:
        frame = varName.split("@")[0]
        name = varName.split("@")[1]
        value = self._getFrame(frame).GetVariableValue(name)
        if(value is None):
            raise MissingValueError("Chyba: Pristup k neinicializovane promenne!")
        return value
  
    # Vrátí hodnotu argument: v případě konstanty je to hodnota samotná, v případě proměnné se nalezne
    # její aktuální hodnota v rámci
    def GetArgumentValue(self, arg: Argument) -> Union[IPPInt, IPPFloat, IPPBool, IPPString, Nil]:
        if(isinstance(arg.value, VarName)):
            return self.GetVariableValue(arg.value.name)
        else:
            return arg.value

    # Získá datový typ argumentu
    def GetArgumentType(self, arg: Argument) -> str:
        if(isinstance(arg.value, VarName)):
            return self.GetVariableType(arg.value.name)
        else:
            if(isinstance(arg.value, IPPInt)):
                return "int"
            elif(isinstance(arg.value, IPPFloat)):
                return "float"
            elif(isinstance(arg.value, IPPBool)):
                return "bool"
            elif(isinstance(arg.value, IPPString)):
                return "string"
            elif(isinstance(arg.value, Nil)):
                return "nil"
            else:
                raise InterpreterInternalError("Chyba: Neplatny typ argumentu!")

    
    # Získá rámec podle jména
    def _getFrame(self, frame: str) -> Frame:
        if(frame == "GF"):
            return self.globalFrame
        elif(frame == "LF"):
            if(self.frameStack.empty()):
                raise MissingFrameError("Chyba: Pristup k lokalnimu ramci, ktery neexistuje!")
            return self.frameStack.top()
        elif(frame == "TF"):
            if(self.tempFrame is None):
                raise MissingFrameError("Chyba: Pristup k docasnemu ramci, ktery neexistuje!")
            return self.tempFrame
        else:
            raise XMLInputError("Chyba: Neplatny ramec!")
