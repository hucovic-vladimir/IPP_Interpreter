from frame import *
from exceptions import *
from argument import *
from stack import *
class InterpreterData:
    def __init__(self, userInputStream):
        self.userInputStream = userInputStream
        self.instructionPointer = 0
        self.globalFrame = Frame()
        self.tempFrame = None
        self.frameStack = Stack()
        self.dataStack = Stack()
        self.callStack = Stack()
        # slovnik navesti
        self.labels = {}


    def GetInitializedVarsCount(self) -> int:
        gfCount = self.globalFrame.GetInitializedVarsCount()
        tfCount = self.tempFrame.GetInitializedVarsCount() if self.tempFrame is not None else 0
        lfCount = self.frameStack.top().GetInitializedVarsCount() if not self.frameStack.empty() else 0
        return gfCount + tfCount + lfCount

    def CreateFrame(self):
        self.tempFrame = Frame()

    def PushFrame(self):
        if(self.tempFrame is None):
            raise MissingFrameError("Chyba: Pokus o ulozeni neexistujiciho ramce na zasobnik!")
        self.frameStack.push(self.tempFrame)
        self.tempFrame = None

    def PopFrame(self):
        if(self.frameStack.empty()):
            raise MissingFrameError("Chyba: Pokus o ziskani ramce z prazdneho zasobniku!")
        self.tempFrame = self.frameStack.pop()

    def GetJumpDestination(self, label: str):
        if(label not in self.labels):
            raise UndefinedLabelError(f"Chyba: Navesti {label} neni definovano!")
        return self.labels[label]
    
    def AddVariable(self, varName: str) -> None:
        split = varName.split("@")
        if(len(split) != 2):
            raise XMLInputError("Chyba: Neplatny nazev promenne!")
        frameType = split[0]
        varName = split[1] 
        frame = self._getFrame(frameType)
        frame.AddVariable(varName)

    def UpdateVariable(self, varName: str, value: Union[IPPString, IPPInt, IPPFloat, IPPBool, Nil]) -> None:
        frameType = varName.split("@")[0]
        varName = varName.split("@")[1]
        frame = self._getFrame(frameType)
        frame.UpdateVariable(varName, value)

    def GetInstructionPointer(self):
        return self.instructionPointer

    def SetInstructionPointer(self, value):
        self.instructionPointer = value

    def PushDataStack(self, value):
        self.dataStack.push(value)
        
    def PopDataStack(self) -> Union[IPPString, IPPInt, IPPFloat, IPPBool, Nil]:
        if(self.dataStack.empty()):
            raise MissingValueError("Chyba: Pristup k prazdnemu datovemu zasobniku!")
        return self.dataStack.pop()
   
    def ClearDataStack(self):
        self.dataStack.clear()

    def PushCallStack(self, value):
        self.callStack.push(value)

    def PopCallStack(self):
        if(self.callStack.empty()):
            raise MissingValueError("Chyba: Volani funkce RETURN bez predchoziho volani CALL!")
        return self.callStack.pop()

    def GetUserInputStream(self):
        return self.userInputStream
       
    def GetVariableType(self, varName: str) -> str:
        frame = varName.split("@")[0]
        name = varName.split("@")[1]
        return self._getFrame(frame).GetVariableType(name)

    def GetVariableValue(self, varName: str) -> Union[IPPString, IPPInt, IPPFloat, IPPBool, Nil]:
        frame = varName.split("@")[0]
        name = varName.split("@")[1]
        value = self._getFrame(frame).GetVariableValue(name)
        if(value is None):
            raise MissingValueError("Chyba: Pristup k neinicializovane promenne!")
        return value
  
    def GetArgumentValue(self, arg: Argument) -> Union[IPPInt, IPPFloat, IPPBool, IPPString, Nil]:
        if(isinstance(arg.value, VarName)):
            return self.GetVariableValue(arg.value.name)
        else:
            return arg.value

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


    def _getFrame(self, frame: str):
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
            raise InterpreterInternalError("Chyba: Neplatny ramec!")
