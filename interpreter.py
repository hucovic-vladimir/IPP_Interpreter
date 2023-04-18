# Autor: Vladimír Hucovič
# Login: xhucov00

from instruction import Instruction
from interpreterdata import InterpreterData
from instruction import *

# Třída pro interpret
class Interpreter():
    def __init__(self, inputStream):
        # Seznam objektů instukcí, vytvořený ze vstupního XML
        self.instructionObjects: List[Instruction] = []
        # Data interpretu (datový zásobník, rámce, vstupní stream pro instrukci READ)
        self.interpreterData: InterpreterData = InterpreterData(inputStream)
        # Chybový kód a hláška
        self.errorCode = None
        self.errorMessage = None
    
    # Přidá instrukce do seznamu
    def AddInstructions(self, instructionObjects: List[Instruction]):
        self.instructionObjects.extend(instructionObjects)
        self._getLabels()

    # Interpretace instrukcí v seznamu instrukcí
    def Interpret(self):
        while(self.interpreterData.instructionPointer < len(self.instructionObjects)):
            result = self._interpretNext()
            if(result):
                self.interpreterData.instructionPointer += 1
            else:
                return False
        return True

    def _interpretNext(self) -> bool:
        nextInstruction = self.instructionObjects[self.interpreterData.instructionPointer]
        try:
            nextInstruction.Execute()
        # Odchycení výjímek definovaných v exceptions.py
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
            if(self.errorCode is not None):
                return False
        return True

    # Získá ze seznamu instrukcí názvy návěští a jejich index v seznamu instrukcí
    def _getLabels(self):
        for index, instruction in enumerate(self.instructionObjects):
            if(type(instruction) == Label):
                labelName = instruction.args[0]
                if(labelName.value in self.interpreterData.labels):
                    print(f"Chyba: Redefinice navesti {labelName.value}!", file=sys.stderr)
                    exit(52)
                if(isinstance(labelName.value, IPPString)):
                    self.interpreterData.labels[labelName.value] = index

# Třída pro interpret který sbírá statistiky
class StatisticsCollectingInterpreter(Interpreter):
    def __init__(self, inputStream):
        super().__init__(inputStream)
        self.instructionExecuteCount: dict[int, int] = {}
        self.maxInitVars: int = 0
        self.totalInstExecuted: int = 0
        self.opcodes: dict[str, int] = {}
    
    # Ziská počet výskytů operačních kódů
    def _getOpcodeCounts(self):
        for inst in self.instructionObjects:
            if(type(inst).__name__.upper() in self.opcodes):
                self.opcodes[type(inst).__name__.upper()] += 1
            else:
                self.opcodes[type(inst).__name__.upper()] = 1

    # Získá operační kódy, které se vyskytly nejvíce 
    def GetMaxOpcodes(self):
        maxCount = 0
        opcodes = ""
        for(count) in self.opcodes.values():
            if(count > maxCount):
                maxCount = count
        for opcode in [opcode for opcode in self.opcodes if self.opcodes[opcode] == maxCount]:
            opcodes += opcode + ","
        return opcodes[:-1]
       
    # Vrátí počet provedených instrukcí
    def GetTotalInstExecuted(self) -> int:
        return self.totalInstExecuted

    # Vrátí maximální počet inicializovaných proměnných
    def GetMaxInitVars(self) -> int:
        return self.maxInitVars
    
    # Vrací atribut order instrukce, která byla provedena nejvícekrát a má nejnižší order
    def GetHotInstructionOrder(self):
        if(len(self.instructionExecuteCount) == 0):
            return ""
        return max(self.instructionExecuteCount, key=lambda k: self.instructionExecuteCount[k])
    
    # Přidá do interpretu instrukce
    # Proti normálnímu interpretu získá ještě počty výskytů operačních kódů
    def AddInstructions(self, instructionObjects: List[Instruction]):
        self.instructionObjects.extend(instructionObjects)
        self._getLabels()
        self._getOpcodeCounts()

    # Interpretrace se sběrem statistik
    def Interpret(self):
        while(self.interpreterData.instructionPointer < len(self.instructionObjects)):    
            nextInstruction = self.instructionObjects[self.interpreterData.instructionPointer]
            result = self._interpretNext()
            # Zisk počtu inicializovaných proměnných a případné přepsání maxima
            self.maxInitVars = max(self.maxInitVars, self.interpreterData.GetInitializedVarsCount())
            # Přičtení počtu vykonání k insturkce s daným pořadím (pokud to není návěští nebo ladící instrukce)
            if(not isinstance (nextInstruction, Dprint) and not  isinstance (nextInstruction, Break) and not isinstance (nextInstruction, Label)):
                if(nextInstruction.order in self.instructionExecuteCount):
                    self.instructionExecuteCount[nextInstruction.order] += 1
                else:
                    self.instructionExecuteCount[nextInstruction.order] = 1 
            if(result):
                self.interpreterData.instructionPointer += 1
            else:
                self.totalInstExecuted = sum(self.instructionExecuteCount.values())
                return False
        self.totalInstExecuted = sum(self.instructionExecuteCount.values())
        return True
