from variable import *
from framemanager import *
from stack import *
from xml.etree import ElementTree as et
from instruction import *
import fileinput as fi
from abc import ABC, abstractmethod

"""class InterpreterInterface(ABC):
    @abstractmethod
    def AddToFrame(self):
        pass

    @abstractmethod
    def GetVariable(self, var: Variable) -> Variable:
        pass

    @abstractmethod
    def SetVariable(self, var: Variable):
        pass

    @abstractmethod
    def GetInstructionPointer(self) -> int:
        pass

    @abstractmethod
    def SetInstructionPointer(self, instructionIndex: int):
        pass

    @abstractmethod
    def GetLabelIndex(self, labelName: str) -> dict[str, int]:
        pass
"""


# Interpreter class
class Interpreter:
    def __init__(self, instructions: List[Instruction], inputStream):
        # Seznam objektu instukci, vytvorene ze vstupniho XML
        self.instructionObjects = instructions
        # Ukazatel na aktualne provadenou instrukci
        self.instructionPointer: int = 0
        # Slovnik navesti (klic = nazev navesti, hodnota = index instrukce)
        self.labels: dict[str, int] = {}
        # Zasobnik volani
        self.callStack: Stack = Stack()
        # Zasobnik pro data
        self.dataStack: Stack = Stack()
        # Nastaveni vstupniho souboru 
        self.userInput = inputStream
        # Vyplni slovnik navesti
        self._getLabels()

    def Interpret(self):
        self.instructionPointer = 0
        while(self.instructionPointer < len(self.instructionObjects)):
            self._executeInstruction(self.instructionObjects[self.instructionPointer])
    
    def _getLabels(self):
        for index, instruction in enumerate(self.instructionObjects):
            if(instruction.opcode == "LABEL"):
                labelName = instruction.args[0]
                if(labelName.value in self.labels):
                    print(f"Chyba: Redefinice navesti {labelName.value}!", file=sys.stderr)
                    exit(52)
                self.labels[labelName.value] = index

    # Vypočítá výsledek aritmetmetických, logických, a konverzních operací
    # a uloží je do cílové proměnné
    def _getOperationResult(self, instruction):
        dest = instruction.args[0]
        op1 = instruction.args[1]
        op2 = instruction.args[2]
        destVar = FrameManager.SearchVariable(dest.value) 
        try:
            if(instruction.opcode == "ADD"):
                if((op1.GetArgDataType() == "int" and op2.GetArgDataType() == "int") 
                   or (op1.GetArgDataType() == "float" and op2.GetArgDataType() == "float")):
                    result, type = op1.GetArgValue() + op2.GetArgValue(), op1.GetArgDataType()
                else: raise TypeError
            elif(instruction.opcode == "SUB"):
                if((op1.GetArgDataType() == "int" and op2.GetArgDataType() == "int") 
                   or (op1.GetArgDataType() == "float" and op2.GetArgDataType() == "float")):
                    result, type = op1.GetArgValue() - op2.GetArgValue(), op1.GetArgDataType()
                else: raise TypeError
            elif(instruction.opcode == "MUL"):
                if((op1.GetArgDataType() == "int" and op2.GetArgDataType() == "int") 
                   or (op1.GetArgDataType() == "float" and op2.GetArgDataType() == "float")):
                    result, type = op1.GetArgValue() * op2.GetArgValue(), op1.GetArgDataType()
                else: raise TypeError
            elif(instruction.opcode == "IDIV"):
                if((op1.GetArgDataType() == "int" and op2.GetArgDataType() == "int"
                    or (op1.GetArgDataType() == "float" and op2.GetArgDataType() == "float"))):
                    try:
                        result, type = op1.GetArgValue() // op2.GetArgValue(), op1.GetArgDataType()
                    except ZeroDivisionError:
                        print("Chyba: Dělení nulou!", file=sys.stderr)
                        exit(57)
                else: raise TypeError
            elif(instruction.opcode == "DIV"):
                if((op1.GetArgDataType() == "int" and op2.GetArgDataType() == "int")
                   or (op1.GetArgDataType() == "float" and op2.GetArgDataType() == "float")):
                    try:
                        result, type = op1.GetArgValue() / op2.GetArgValue(), op1.GetArgDataType()
                    except ZeroDivisionError:
                        print("Chyba: Dělení nulou!", file=sys.stderr)
                        exit(57)
                else: raise TypeError
            elif(instruction.opcode == "LT"):
                result, type = op1.GetArgValue() < op2.GetArgValue(), "bool"
            elif(instruction.opcode == "GT"):
                result, type = op1.GetArgValue() > op2.GetArgValue(), "bool"
            elif(instruction.opcode == "EQ"):
                result, type = op1.GetArgValue() == op2.GetArgValue(), "bool"
            elif(instruction.opcode == "AND"):
                result, type = op1.GetArgValue() and op2.GetArgValue(), "bool"
            elif(instruction.opcode == "OR"):
                result, type = op1.GetArgValue() or op2.GetArgValue(), "bool"
            elif(instruction.opcode == "NOT"):
                result, type = not op1.GetArgValue(), "bool"
            else: 
                print("Interní chyba interpretu! (volání _getOperationResult s neznámou instrukcí)", file=sys.stderr)
                exit(99)
        except TypeError:
            print(f"Chyba: Nekompatibilni operandy pro instrukci {instruction.opcode} - {op1.GetArgDataType()} a {op2.GetArgDataType()}!", file=sys.stderr)
            exit(53)
        if(destVar is None):
            print(f"Chyba: {dest.value} není definována!", file=sys.stderr)
            exit(54)
        destVar.SetValue(result, type)

    # vytvoří dočasný rámec
    def _createframe(self, instruction: Instruction):
        FrameManager.CreateTempFrame()

    def _defvar(self, instruction: Instruction):
        var = instruction.args[0]
        varFrame = var.value.split('@')[0]
        name = var.value.split('@')[1]
        var = Variable(name, None, None)
        FrameManager.AddToFrame(varFrame, var)


    def _pushframe(self, instruction):
        FrameManager.PushFrame()

    def _replaceEscapeSequences(self, string):
        outputString = ""
        i = 0
        while i < len(string):
            if(string[i] == '\\'):
                asciiCode = int(string[i+1:i+4])
                outputString += chr(asciiCode)
                i += 3
            else:
                outputString += string[i]
            i += 1
        return outputString
    
    def _write(self, instruction):
        arg = instruction.args[0]
        argType = arg.GetArgDataType()
        argValue = arg.GetArgValue()
        if(argType == "string"):
            print(self._replaceEscapeSequences(argValue), end='', flush=True)
        elif(argType == "float"):
            print(float.hex(argValue), end='', flush=True)
        elif (argType == "bool"):
            if(argValue):
                print("true", end='', flush=True)
            else:
                print("false", end='', flush=True)
        else:
            print(argValue, end='', flush=True)
            

    def _popframe(self, instruction):
        try:
            FrameManager.PopFrame()
        except IndexError:
            print("Error: Lokalni ramec neni definovan!", file=sys.stderr)
            exit(55)

    def _call(self, instruction):
        self.callStack.push(self.instructionPointer)
        destLabel = instruction.args[0]
        labelInstIndex = self.labels.get(destLabel.value)
        if(labelInstIndex is None):
            print(f"Chyba: Navesti {destLabel.value} neni definovano!", file=sys.stderr)
            exit(52)
        self.instructionPointer = labelInstIndex

    def _return(self, instruction):
        if(self.callStack.empty()):
            print("Chyba: Nalezena instrukce navratu z funkce bez predchoziho volani funkce!", file=sys.stderr)
            exit(56)
        self.instructionPointer = self.callStack.pop()
    
    def _pushs(self, instruction):
        src = instruction.args[0]
        value = src.GetArgValue()
        type = src.GetArgDataType()
        self.dataStack.push(Argument(type, value))

    def _pops(self, instruction):
        if(self.dataStack.empty()):
            print("Chyba: Pokus o ziskani hodnoty z prazdneho datoveho zasobniku!", file=sys.stderr)
            exit(56)
        dest = instruction.args[0]
        destVar = FrameManager.SearchVariable(dest.value)
        if(destVar is None):
            print(f"Chyba: {dest.value} neni definovana!", file=sys.stderr)
            exit(54)
        popped = self.dataStack.pop()
        destVar.SetValue(popped.value, popped.type)

    def _adds(self, instruction):
        if(self.dataStack.elementCount() < 2):
            print("Chyba: Pokus o ziskani hodnoty z prazdneho datoveho zasobniku!", file=sys.stderr)
            exit(56)
        op2 = self.dataStack.pop()
        op1 = self.dataStack.pop()
        if((op2.type == "float" and op1.type == "float") or (op2.type == "int" and op1.type == "int")):
            self.dataStack.push(Argument("int",op1.value + op2.value))
        else:
            print("Chyba: Nekompatibilni operandy pro instrukci ADDS!", file=sys.stderr)
            exit(53)
        
    def _subs(self, instruction):
        if(self.dataStack.elementCount() < 2):
            print("Chyba: Pokus o ziskani hodnoty z prazdneho datoveho zasobniku!", file=sys.stderr)
            exit(56)
        op2 = self.dataStack.pop()
        op1 = self.dataStack.pop()
        if((op2.type == "float" and op1.type == "float") or (op2.type == "int" and op1.type == "int")):
            self.dataStack.push(Argument("int",op1.value - op2.value))
        else:
            print("Chyba: Nekompatibilni operandy pro instrukci SUBS!", file=sys.stderr)
            exit(53)

    def _muls(self, instruction):
        if(self.dataStack.elementCount() < 2):
            print("Chyba: Pokus o ziskani hodnoty z prazdneho datoveho zasobniku!", file=sys.stderr)
            exit(56)
        op2 = self.dataStack.pop()
        op1 = self.dataStack.pop()
        ## TODO FLOAT SUPPORT
        if((op2.type == "float" and op1.type == "float") or (op2.type == "int" and op1.type == "int")):
            self.dataStack.push(Argument("int",op1.value * op2.value))
        else:
            print("Chyba: Nekompatibilni operandy pro instrukci MULS!", file=sys.stderr)
            exit(53)
    
    def _divs(self, instruction):
        if(self.dataStack.elementCount() < 2):
            print("Chyba: Pokus o ziskani hodnoty z prazdneho datoveho zasobniku!", file=sys.stderr)
            exit(56)
        op2 = self.dataStack.pop()
        op1 = self.dataStack.pop()
        if((op2.type == "float" and op1.type == "float") or (op2.type == "int" and op1.type == "int")):
            self.dataStack.push(Argument("int",op1.value / op2.value))
        else:
            print("Chyba: Nekompatibilni operandy pro instrukci DIVS!", file=sys.stderr)
            exit(53)
    
    def _idivs(self, instruction):
        if(self.dataStack.elementCount() < 2):
            print("Chyba: Pokus o ziskani hodnoty z prazdneho datoveho zasobniku!", file=sys.stderr)
            exit(56)
        op2 = self.dataStack.pop()
        op1 = self.dataStack.pop()
        if(op2.type == "int" and op1.type == "int"):
            self.dataStack.push(Argument("int", op1.value // op2.value))
        else:
            print("Chyba: Nekompatibilni operandy pro instrukci IDIVS!", file=sys.stderr)
            exit(53)
    
    def _lts(self, instruction):
        if(self.dataStack.elementCount() < 2):
            print("Chyba: Pokus o ziskani hodnoty z prazdneho datoveho zasobniku!", file=sys.stderr)
            exit(56)
        op2 = self.dataStack.pop()
        op1 = self.dataStack.pop()
        if((op2.type == "float" and op1.type == "float") or (op2.type == "int" and op1.type == "int")
           or (op2.type == "string" and op1.type == "string") or (op2.type == "bool" and op1.type == "bool")):
            self.dataStack.push(Argument("bool", op1.value < op2.value))
        else:
            print("Chyba: Nekompatibilni operandy pro instrukci LTS!", file=sys.stderr)
            exit(53)

    def _gts(self, instruction):
        if(self.dataStack.elementCount() < 2):
            print("Chyba: Pokus o ziskani hodnoty z prazdneho datoveho zasobniku!", file=sys.stderr)
            exit(56)
        op2 = self.dataStack.pop()
        op1 = self.dataStack.pop()
        if((op2.type == "float" and op1.type == "float") or (op2.type == "int" and op1.type == "int")
           or (op2.type == "string" and op2.type == "string") or (op2.type == "bool" and op1.type == "bool")):
            self.dataStack.push(Argument("bool", op1.value > op2.value))
        else:
            print("Chyba: Nekompatibilni operandy pro instrukci GTS!", file=sys.stderr)
            exit(53)

    def _eqs(self, instruction):
        if(self.dataStack.elementCount() < 2):
            print("Chyba: Pokus o ziskani hodnoty z prazdneho datoveho zasobniku!", file=sys.stderr)
            exit(56)
        op2 = self.dataStack.pop()
        op1 = self.dataStack.pop()
        if((op2.type == "float" and op1.type == "float") or (op2.type == "int" and op1.type == "int")
           or (op2.type == "string" and op2.type == "string") or (op2.type == "bool" and op1.type == "bool")
           or (op1.type == "nil" or op2.type == "nil")):
            self.dataStack.push(Argument("bool", op1.value == op2.value))
        else:
            print("Chyba: Nekompatibilni operandy pro instrukci EQS!", file=sys.stderr)
            exit(53)
    
    def _nots(self, instruction):
        if(self.dataStack.empty()):
            print("Chyba: Pokus o ziskani hodnoty z prazdneho datoveho zasobniku!", file=sys.stderr)
            exit(56)
        op1 = self.dataStack.pop()
        if(op1.type == "bool"):
            self.dataStack.push(Argument("bool", not op1.value))
        else:
            print("Chyba: Nekompatibilni operandy pro instrukci NOTS!", file=sys.stderr)
            exit(53)

    def _ands(self, instruction):
        if(self.dataStack.elementCount() < 2):
            print("Chyba: Pokus o ziskani hodnoty z prazdneho datoveho zasobniku!", file=sys.stderr)
            exit(56)
        op2 = self.dataStack.pop()
        op1 = self.dataStack.pop()
        if(op1.type == "bool" and op2.type == "bool"):
            self.dataStack.push(Argument("bool", op1.value and op2.value))
        else:
            print("Chyba: Nekompatibilni operandy pro instrukci ANDS!", file=sys.stderr)
            exit(53)
    
    def _ors(self, instruction):
        if(self.dataStack.elementCount() < 2):
            print("Chyba: Pokus o ziskani hodnoty z prazdneho datoveho zasobniku!", file=sys.stderr)
            exit(56)
        op2 = self.dataStack.pop()
        op1 = self.dataStack.pop()
        if(op1.type == "bool" and op2.type == "bool"):
            self.dataStack.push(Argument("bool", op1.value or op2.value))
        else:
            print("Chyba: Nekompatibilni operandy pro instrukci ORS!", file=sys.stderr)
            exit(53)

    def _float2int(self, instruction):
        dest = instruction.args[0]
        op1 = instruction.args[1]
        destVar = FrameManager.SearchVariable(dest.value)
        if(destVar is None):
            print(f"Chyba: {dest.value} neni definovana!", file=sys.stderr)
            exit(54)
        if(op1.type == "var"):
            op1Var = FrameManager.SearchVariable(op1.value)
            if(op1Var is None):
                print(f"Chyba: {op1.value} neni definovana!", file=sys.stderr)
                exit(54)
            if(op1Var.type == None):
                print(f"Chyba: {op1.value} neni inicializovana!", file=sys.stderr)
                exit(56)

        if(op1.GetArgDataType() != "float"):
            print(f"Chyba: Chybny vstup pro instrukci float2int - {op1.GetArgValue()}!", file=sys.stderr)
            exit(53)
        destVar.SetValue(int(op1.GetArgValue()), "int")

    def _int2float(self, instruction):
        dest = instruction.args[0]
        op1 = instruction.args[1]
        op1Value = op1.GetArgValue()
        destVar = FrameManager.SearchVariable(dest.value)
        if(destVar is None):
            print(f"Chyba: {dest.value} neni definovana!", file=sys.stderr)
            exit(54)
        try:
            if(op1.GetArgDataType() != "int"):
                raise ValueError
            destVar.SetValue(float(op1Value), "float")
        except ValueError:
            print(f"Chyba: Chybny vstup pro instrukci int2float - {op1.GetArgValue()}!", file=sys.stderr)
            exit(53)

    def _int2char(self, instruction):
        dest = instruction.args[0]
        op1 = instruction.args[1]
        op1Value = op1.GetArgValue()
        destVar = FrameManager.SearchVariable(dest.value)
        if(destVar is None):
            print(f"Chyba: {dest.value} neni definovana!", file=sys.stderr)
            exit(54)
        try:
            if(op1.GetArgDataType() != "int"):
                raise ValueError
            destVar.SetValue(chr(op1Value), "string")
        except ValueError:
            print(f"Chyba: Chybny vstup pro instrukci int2char - {op1.GetArgValue()}!", file=sys.stderr)
            exit(53)
        except OverflowError:
            print(f"Chyba: Chybny vstup pro instrukci int2char - {op1.GetArgValue()}!", file=sys.stderr)
            exit(58)

    def _stri2int(self, instruction):
        dest = instruction.args[0]
        op1 = instruction.args[1]
        op2 = instruction.args[2]
        op1Value = op1.GetArgValue()
        op2Value = op2.GetArgValue()
        destVar = FrameManager.SearchVariable(dest.value)
        if(destVar is None):
            print(f"Chyba: {dest.value} neni definovana!", file=sys.stderr)
            exit(54)
        try:
            if(op1.GetArgDataType() != "string" or op2.GetArgDataType() != "int"):
                raise ValueError
            destVar.SetValue(ord(op1Value[op2Value]), "int")
        except ValueError:
            print(f"Chyba: Chybny vstup pro instrukci stri2int - {op1.GetArgValue()}!", file=sys.stderr)
            exit(53)
        except IndexError:
            print(f"Chyba: Chybny vstup pro instrukci stri2int - {op1.GetArgValue()}!", file=sys.stderr)
            exit(58)

    def _int2chars(self, instruction):
        if(self.dataStack.elementCount() < 1):
            print("Chyba: Pokus o ziskani hodnoty z prazdneho datoveho zasobniku!", file=sys.stderr)
            exit(56)
        op1 = self.dataStack.pop()
        if(op1.type == "int"):
            try:
                self.dataStack.push(Argument("string", chr(op1.value)))
            except OverflowError:
                print(f"Chyba: Chybny vstup pro instrukci int2char - {op1.value}!", file=sys.stderr)
                exit(58)
            except ValueError:
                print(f"Chyba: Chybny vstup pro instrukci int2char - {op1.value}!", file=sys.stderr)
                exit(58)
        else:
            print("Chyba: Nekompatibilni operandy pro instrukci INT2CHARS!", file=sys.stderr)
            exit(53)

    def _stri2ints(self, instruction):
        if(self.dataStack.elementCount() < 2):
            print("Chyba: Pokus o ziskani hodnoty z prazdneho datoveho zasobniku!", file=sys.stderr)
            exit(56)
        op2 = self.dataStack.pop()
        op1 = self.dataStack.pop()
        if(op1.type == "string" and op2.type == "int"):
            try:
                self.dataStack.push(Argument("int", ord(op1.value[op2.value])))
            except IndexError:
                print(f"Chyba: Chybny vstup pro instrukci stri2int - {op1.value}!", file=sys.stderr)
                exit(58)
        else:
            print("Chyba: Nekompatibilni operandy pro instrukci STRI2INTS!", file=sys.stderr)
            exit(53)

    def _int2floats(self, instruction):
        if(self.dataStack.elementCount() < 1):
            print("Chyba: Pokus o ziskani hodnoty z prazdneho datoveho zasobniku!", file=sys.stderr)
            exit(56)
        op1 = self.dataStack.pop()
        if(op1.type == "int"):
            self.dataStack.push(Argument("float", float(op1.value)))
        else:
            print("Chyba: Nekompatibilni operandy pro instrukci INT2FLOATS!", file=sys.stderr)
            exit(53)

    def _float2ints(self, instruction):
        if(self.dataStack.elementCount() < 1):
            print("Chyba: Pokus o ziskani hodnoty z prazdneho datoveho zasobniku!", file=sys.stderr)
            exit(56)
        op1 = self.dataStack.pop()
        if(op1.type == "float"):
            self.dataStack.push(Argument("int", int(op1.value)))
        else:
            print("Chyba: Nekompatibilni operandy pro instrukci FLOAT2INTS!", file=sys.stderr)
            exit(53)

    def _read(self, instruction):
        dest = instruction.args[0]
        type = instruction.args[1]
        destVar = FrameManager.SearchVariable(dest.value)
        if(destVar is None):
            print(f"Chyba: {dest.value} neni definovana!", file=sys.stderr)
            exit(54)

        userInput = self.userInput.readline().strip("\n")
        if(type.value == "float"):
            try:
                # hexadecimalni vstup
                if(userInput.startswith("0x") or userInput.startswith("-0x") or userInput.startswith("+0x")):
                    destVar.SetValue(float.fromhex(userInput), type.value)
                # dekadicky vstup
                else:
                    destVar.SetValue(float(userInput), type.value)
            except ValueError:
                print(f"Chyba: Chybny vstup pro instrukci read (float) - {userInput}!", file=sys.stderr)
                exit(53)
        elif(type.value == "int"):
            try:
                # hexadecimalni vstup
                if(userInput.startswith("0x") or userInput.startswith("-0x") or userInput.startswith("+0x")):
                    destVar.SetValue(int(userInput, 16), type.value)
                # oktalovy vstup
                elif(userInput.startswith("0") or userInput.startswith("-0") or userInput.startswith("+0")):
                    destVar.SetValue(int(userInput, 8), type.value)
                # dekadicky vstup
                else:
                    destVar.SetValue(int(userInput), type.value)
            except ValueError:
                print(f"Chyba: Chybny vstup pro instrukci read (int) - {userInput}!", file=sys.stderr)
                exit(53)
        else:
            destVar.SetValue(userInput, type.value)
    
    def _jump(self, instruction):
        destLabel = instruction.args[0]
        labelInstIndex = self.labels.get(destLabel.value)
        if(labelInstIndex is None):
            print(f"Chyba: skok na nedefinovanovane navesti {destLabel.value}!", file=sys.stderr)
            exit(52)
        self.instructionPointer = labelInstIndex 
       
        
    def _jumpifeq(self, instruction):
        op1 = instruction.args[1]
        op2 = instruction.args[2]
        if(op1.GetArgValue() == op2.GetArgValue()):
            self._jump(instruction)

    def _jumpifneq(self, instruction):
        op1 = instruction.args[1]
        op2 = instruction.args[2]
        if(op1.GetArgValue() != op2.GetArgValue()):
            self._jump(instruction)
          
    def _jumpifeqs(self, instruction):
        op2 = self.dataStack.pop()
        op1 = self.dataStack.pop()
        destLabel = instruction.args[0]
        labelInstIndex = self.labels.get(destLabel.value)
        if(labelInstIndex is None):
            print(f"Chyba: skok na nedefinovanovane navesti {destLabel.value}!", file=sys.stderr)
            exit(52)
        if(op1.GetArgDataType() == op2.GetArgDataType() or op1.GetArgDataType() == "nil" or op2.GetArgDataType() == "nil"):
            if(op1.GetArgValue() == op2.GetArgValue()):
                self.instructionPointer = labelInstIndex
        else:
            print("Chyba: Nekompatibilni operandy pro instrukci JUMPIFEQS!", file=sys.stderr)
            exit(53)
            
    def _jumpifneqs(self, instruction): 
        op2 = self.dataStack.pop()
        op1 = self.dataStack.pop()
        destLabel = instruction.args[0]
        labelInstIndex = self.labels.get(destLabel.value)
        if(labelInstIndex is None):
            print(f"Chyba: skok na nedefinovanovane navesti {destLabel.value}!", file=sys.stderr)
            exit(52)
        if(op1.GetArgDataType() == op2.GetArgDataType() or op1.GetArgDataType() == "nil" or op2.GetArgDataType() == "nil"):
            if(op1.GetArgValue() != op2.GetArgValue()):
                self.instructionPointer = labelInstIndex
        else:
            print("Chyba: Nekompatibilni operandy pro instrukci JUMPIFEQS!", file=sys.stderr)
            exit(53)
   
    def _dprint(self, instruction):
        op1 = instruction.args[0]
        print(op1.GetArgValue(), file=sys.stderr, end='')

    def _clears(self, instruction):
        self.dataStack.clear()
    
    def _exit(self, instruction):
        try:
            exit(instruction.args[0].GetArgValue())
        except TypeError:
            print(f"Chyba: Nekompatibilni hodnota typu {instruction.args[0].GetArgDataType()} : {instruction.args[0].GetArgValue()}!", file=sys.stderr)
            exit(53)
    
    def _type(self, instruction):
        dest = instruction.args[0]
        op1 = instruction.args[1]
        destVar = FrameManager.SearchVariable(dest.value)
        if(destVar is None):
            print(f"Chyba: {dest.value} neni definovana!", file=sys.stderr)
            exit(54)
        type = op1.GetArgDataType()
        if(type is None):
            type = ""
        destVar.SetValue(type, "string")

 
    def _concat(self, instruction):
        dest = instruction.args[0]
        op1 = instruction.args[1]
        op2 = instruction.args[2]
        destVar = FrameManager.SearchVariable(dest.value)
        if(destVar is None):
            print(f"Chyba: {dest.value} neni definovana!", file=sys.stderr)
            exit(54)
        try:
            destVar.SetValue(op1.GetArgValue() + op2.GetArgValue(), "string")
        except TypeError:
            print(f"Error: Nekompatibilni operandy pro instrukci {instruction.opcode} - {op1.GetArgDataType()} a {op2.GetArgDataType()}!", file=sys.stderr)
            exit(53)

    def _move(self, instruction):
        dest = instruction.args[0]
        src = instruction.args[1]
        varDest = FrameManager.SearchVariable(dest.value)
        srcValue = src.GetArgValue()
        srcType = src.GetArgDataType()
        if(varDest is None):
            print(f"Error: {dest.value} not defined!")
            exit(54)
        varDest.SetValue(srcValue, srcType)

    def _executeInstruction(self, instruction: Instruction) -> None:
        opcode = instruction.opcode.upper()
        if(opcode == 'CREATEFRAME'):
            self._createframe(instruction)
        elif(opcode == 'DEFVAR'):
            self._defvar(instruction)
        elif(opcode == 'PUSHFRAME'):
            self._pushframe(instruction)
        elif(opcode == 'POPFRAME'):
            self._popframe(instruction)
        elif(opcode == 'WRITE'):
            self._write(instruction)
        elif(opcode == 'CALL'):
            self._call(instruction)
        elif(opcode == 'RETURN'):
            self._return(instruction)
        elif(opcode == 'PUSHS'):
            self._pushs(instruction)
        elif(opcode == 'POPS'):
            self._pops(instruction)
        elif(opcode == 'ADD' or opcode == 'SUB' or opcode == 'MUL' or opcode == 'IDIV'
             or opcode == 'LT' or opcode == 'GT' or opcode == 'EQ' or opcode == 'AND' 
             or opcode == 'OR' or opcode == 'NOT' or opcode == 'DIV'):
            self._getOperationResult(instruction)
        elif(opcode == 'READ'):
            self._read(instruction)
        elif(opcode == 'WRITE'):
            self._write(instruction)
        elif(opcode == 'CONCAT'):
            self._concat(instruction)
        elif(opcode == 'MOVE'):
            self._move(instruction)
        elif (opcode == 'LABEL'):
            pass
        elif (opcode == 'JUMP'):
            self._jump(instruction)
        elif (opcode == 'JUMPIFEQ'):
            self._jumpifeq(instruction)
        elif (opcode == 'JUMPIFNEQ'):
            self._jumpifneq(instruction)
        elif (opcode == 'EXIT'):
            self._exit(instruction)
        elif (opcode == "FLOAT2INT"):
            self._float2int(instruction)
        elif (opcode == "INT2FLOAT"):
            self._int2float(instruction)
        elif (opcode == "STRI2INT"):
            self._stri2int(instruction)
        elif (opcode == "INT2CHAR"):
            self._int2char(instruction)
        elif (opcode == "TYPE"):
            self._type(instruction)
        elif (opcode == "ADDS"):
            self._adds(instruction)
        elif (opcode == "SUBS"):
            self._subs(instruction)
        elif (opcode == "DIVS"):
            self._divs(instruction)
        elif (opcode == "MULS"):
            self._muls(instruction)
        elif (opcode == "IDIVS"):
            self._idivs(instruction)
        elif (opcode == "LTS"):
            self._lts(instruction)
        elif (opcode == "GTS"):
            self._gts(instruction)
        elif (opcode == "EQS"):
            self._eqs(instruction)
        elif (opcode == "NOTS"):
            self._nots(instruction)
        elif (opcode == "ANDS"):
            self._ands(instruction)
        elif (opcode == "ORS"):
            self._ors(instruction)
        elif (opcode == "JUMPIFEQS"):
            self._jumpifeqs(instruction)
        elif (opcode == "JUMPIFNEQS"):
            self._jumpifneqs(instruction)
        elif (opcode == "FLOAT2INTS"):
            self._float2ints(instruction)
        elif (opcode == "INT2FLOATS"):
            self._int2floats(instruction)
        elif (opcode == "STRI2INTS"):
            self._stri2ints(instruction)
        elif (opcode == "INT2CHARS"):
            self._int2chars(instruction)
        elif (opcode == "CLEARS"):
            self._clears(instruction)
        elif (opcode == "DPRINT"):
            self._dprint(instruction)
        else:
            print(f"Error: {opcode} is not a valid instruction!", file=sys.stderr)
            exit(32)
        self.instructionPointer += 1
