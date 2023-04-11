from frame import *
from variable import *
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
        frameType = varName.split("@")[0]
        varName = varName.split("@")[1]
        frame = self._GetFrame(frameType)
        frame.AddVariable(varName)

    def UpdateVariable(self, varName: str, value: Union[IPPString, IPPInt, IPPFloat, IPPBool, Nil]) -> None:
        frameType = varName.split("@")[0]
        varName = varName.split("@")[1]
        frame = self._GetFrame(frameType)
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
        return self._GetFrame(frame).GetVariableType(name)

    def GetVariableValue(self, varName: str) -> Union[IPPString, IPPInt, IPPFloat, IPPBool, Nil]:
        frame = varName.split("@")[0]
        name = varName.split("@")[1]
        value = self._GetFrame(frame).GetVariableValue(name)
        if(value is None):
            raise MissingValueError("Chyba: Pristup k neinicializovane promenne!")
        return value


    def _GetFrame(self, frame: str):
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
