from stack import *
from xml.etree import ElementTree as et
from instruction import *
import fileinput as fi
from argument import *
from InterpreterData import *
from instruction import *

# Interpreter class
class Interpreter():
    def __init__(self, inputStream):
        # Seznam objektu instukci, vytvorene ze vstupniho XML
        self.instructionObjects = []
        # Data interpreteru (datovy zasobnik, ramce, vstupni stream)
        self.interpreterData = InterpreterData(inputStream)
        # Vyplni slovnik navesti
        self.errorCode = None
        self.errorMessage = None

    def AddInstructions(self, instructionObjects: List[Instruction]):
        self.instructionObjects.extend(instructionObjects)
        self._getLabels()

    def Interpret(self):
        # FIXME asi vytknout tuhle cast do private metody _executeNext aby to nemuselo byt v obou interpretech
        while(self.interpreterData.instructionPointer < len(self.instructionObjects)):
            nextInstruction = self.instructionObjects[self.interpreterData.instructionPointer]
            try:
                nextInstruction.Execute()
            # Odchyceni vyjimek definovanych v exceptions.py
            except XMLInputError as e:
                self.errorCode = 32
                self.errorMessage = e.message + " : " + str(nextInstruction)
            except UndefinedLabelError as e:
                self.errorCode = 52
                self.errorMessage = e.message + " : " + str(nextInstruction)
            except VariableRedefenitionError as e:
                self.errorMessage = e.message + " : " + str(nextInstruction)
                self.errorCode = 52 
            except OperandTypeError as e:
                self.errorMessage = e.message + " : " + str(nextInstruction)
                self.errorCode = 53
            except MissingVariableError as e:
                self.errorMessage = e.message + " : " + str(nextInstruction)
                self.errorCode = 54
            except MissingFrameError as e:
                self.errorMessage = e.message + " : " + str(nextInstruction)
                self.errorCode = 55
            except MissingValueError as e:
                self.errorMessage = e.message + " : " + str(nextInstruction)
                self.errorCode = 56
            except OperandValueError as e:
                self.errorMessage = e.message + " : " + str(nextInstruction)
                self.errorCode = 57            
            except StringOperationError as e:
                self.errorMessage = e.message + " : " + str(nextInstruction)
                self.errorCode = 58
            except InterpreterInternalError as e:
                self.errorMessage = e.message + " : " + str(nextInstruction)
                self.errorCode = 99 
            except ExitInstruction as e:
                self.errorCode = e.code
                return True
            finally:
                if(self.errorMessage is not None):
                    return False
            self.interpreterData.instructionPointer += 1
        return True
    
    def _getLabels(self):
        for index, instruction in enumerate(self.instructionObjects):
            if(type(instruction) == Label):
                labelName = instruction.args[0]
                if(labelName.value in self.interpreterData.labels):
                    print(f"Chyba: Redefinice navesti {labelName.value}!", file=sys.stderr)
                    exit(52)
                self.interpreterData.labels[labelName.value] = index

class StatisticsCollectingInterpreter(Interpreter):
    def __init__(self, inputStream):
        super().__init__(inputStream)
        self.instructionExecuteCount: dict[int, int] = {}
        self.maxInitVars = 0
        self.totalInstExecuted = 0
        self.opcodes: dict[str, int] = {}

    def _getOpcodeCounts(self):
        for inst in self.instructionObjects:
            if(type(inst).__name__.upper() in self.opcodes):
                self.opcodes[type(inst).__name__.upper()] += 1
            else:
                self.opcodes[type(inst).__name__.upper()] = 1

    def GetMaxOpcodes(self):
        maxCount = 0
        opcodes = ""
        for(count) in self.opcodes.values():
            if(count > maxCount):
                maxCount = count
        for opcode in [opcode for opcode in self.opcodes if self.opcodes[opcode] == maxCount]:
            opcodes += opcode + ","
        return opcodes[:-1]
        
    def GetTotalInstExecuted(self) -> int:
        return self.totalInstExecuted

    def GetMaxInitVars(self) -> int:
        return self.maxInitVars

    def GetHotInstructionOrder(self):
        if(len(self.instructionExecuteCount) == 0):
            return ""
        return max(self.instructionExecuteCount, key=lambda k: self.instructionExecuteCount[k])
 
    def AddInstructions(self, instructionObjects: List[Instruction]):
        self.instructionObjects.extend(instructionObjects)
        self._getLabels()
        self._getOpcodeCounts()

    def Interpret(self):
        while(self.interpreterData.instructionPointer < len(self.instructionObjects)):
            nextInstruction = self.instructionObjects[self.interpreterData.instructionPointer]
            try:
                nextInstruction.Execute()
                self.maxInitVars = max(self.maxInitVars, self.interpreterData.GetInitializedVarsCount())
                if(not isinstance (nextInstruction, Dprint) or not  isinstance (nextInstruction, Break) or not isinstance (nextInstruction, Exit)):
                    if(nextInstruction in self.instructionExecuteCount):
                        self.instructionExecuteCount[nextInstruction.order] += 1
                    else:
                        self.instructionExecuteCount[nextInstruction.order] = 1 

            # Odchyceni vyjimek definovanych v exceptions.py
            except XMLInputError as e:
                self.errorCode = 32
                self.errorMessage = e.message + " : " + str(nextInstruction)
            except UndefinedLabelError as e:
                self.errorCode = 52
                self.errorMessage = e.message + " : " + str(nextInstruction)
            except VariableRedefenitionError as e:
                self.errorMessage = e.message + " : " + str(nextInstruction)
                self.errorCode = 52 
            except OperandTypeError as e:
                self.errorMessage = e.message + " : " + str(nextInstruction)
                self.errorCode = 53
            except MissingVariableError as e:
                self.errorMessage = e.message + " : " + str(nextInstruction)
                self.errorCode = 54
            except MissingFrameError as e:
                self.errorMessage = e.message + " : " + str(nextInstruction)
                self.errorCode = 55
            except MissingValueError as e:
                self.errorMessage = e.message + " : " + str(nextInstruction)
                self.errorCode = 56
            except OperandValueError as e:
                self.errorMessage = e.message + " : " + str(nextInstruction)
                self.errorCode = 57            
            except StringOperationError as e:
                self.errorMessage = e.message + " : " + str(nextInstruction)
                self.errorCode = 58
            except InterpreterInternalError as e:
                self.errorMessage = e.message + " : " + str(nextInstruction)
                self.errorCode = 99 
            except ExitInstruction as e:
                self.errorCode = e.code
                return True
            finally:
                if(self.errorMessage is not None):
                    return False
            self.interpreterData.instructionPointer += 1
        self.totalInstExecuted = sum(self.instructionExecuteCount.values()) 
        return True
