from variable import *
from framemanager import *
from stack import *
from xml.etree import ElementTree as et
from instruction import *
import fileinput as fi
from argument import *
from InterpreterData import *
from instruction import *

# Interpreter class
class Interpreter():
    def __init__(self, instructions: List[Instruction], inputStream):
        # Seznam objektu instukci, vytvorene ze vstupniho XML
        self.instructionObjects = instructions
        # Data interpreteru (datovy zasobnik, ramce, vstupni stream)
        self.interpreterData = InterpreterData(inputStream)
        # Vyplni slovnik navesti
        self._getLabels()
        self.errorCode = 0
        self.errorMessage = ""

    def Interpret(self):
        while(self.interpreterData.instructionPointer < len(self.instructionObjects)):
            nextInstruction = self.instructionObjects[self.interpreterData.instructionPointer]
            try:
                nextInstruction.Execute(self.interpreterData)
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
            # FIXME - Index error muze nastat pravdepodobne i jindy
            except IndexError as e:
                self.errorMessage = "Neplatny pocet argumentu" + " : " + str(nextInstruction)
                self.errorCode = 32
            finally:
                if(self.errorCode != 0):
                    print(self.errorMessage, file=sys.stderr)
                    exit(self.errorCode)
            self.interpreterData.instructionPointer += 1
    
    def _getLabels(self):
        for index, instruction in enumerate(self.instructionObjects):
            if(instruction.opcode == "LABEL"):
                labelName = instruction.args[0]
                if(labelName.value in self.interpreterData.labels):
                    print(f"Chyba: Redefinice navesti {labelName.value}!", file=sys.stderr)
                    exit(52)
                self.interpreterData.labels[labelName.value] = index

