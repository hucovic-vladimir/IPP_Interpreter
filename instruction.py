# Autor: Vladimír Hucovič
# Login: xhucov00

from typing import List
import xml.etree.ElementTree as et
from argument import *
from interpreterdata import *
from exceptions import *
from abc import abstractmethod
import sys

# Bázová třída pro instrukce v IPPCode23
class Instruction:
    def __init__(self, args: List[Argument], interpreterData: InterpreterData, order: int) -> None:
        # Seznam argumentů
        self.args: List[Argument] = args
        # Data interpretu, se kterými instrukce pracuje
        self.interpreterData: InterpreterData = interpreterData
        self.order: int = order

    def __str__(self):
        return f"{self.__class__.__name__} Order: {self.order} Arguments: {(' '.join(str(arg) for arg in self.args))} "

    # Abstraktní metoda, kterou implementují konkrétní instruce
    @abstractmethod
    def Execute(self):
       pass 

# MOVE <var> <symb>
class Move(Instruction):
    def Execute(self):
        argValue = self.interpreterData.GetArgumentValue(self.args[1])
        self.interpreterData.UpdateVariable(str(self.args[0]), argValue)

# CREATEFRAME
class CreateFrame(Instruction):
    def Execute(self):
        self.interpreterData.CreateFrame()

# PUSHFRAME
class PushFrame(Instruction):
    def Execute(self) -> None:
        self.interpreterData.PushFrame()

# POPFRAME
class PopFrame(Instruction):
    def Execute(self):
        self.interpreterData.PopFrame()

# DEFVAR <var>
class Defvar(Instruction):
    def Execute(self):
        self.interpreterData.AddVariable(str(self.args[0])) 

# CALL <label>
class Call(Instruction):
    def Execute(self):
        self.interpreterData.PushCallStack(self.interpreterData.GetInstructionPointer())
        newInstrPointer = self.interpreterData.GetJumpDestination(str(self.args[0].value))
        self.interpreterData.SetInstructionPointer(newInstrPointer)


# RETURN
class Return(Instruction):
    def Execute(self):
        self.interpreterData.SetInstructionPointer(self.interpreterData.PopCallStack())

# PUSHS <symb>
class Pushs(Instruction):
    def Execute(self):
        self.interpreterData.PushDataStack(self.interpreterData.GetArgumentValue(self.args[0]))

# POPS <var>
class Pops(Instruction):
    def Execute(self):
        self.interpreterData.UpdateVariable(str(self.args[0]), self.interpreterData.PopDataStack())


# ADD <var> <symb1> <symb2>
class Add(Instruction):
    def Execute(self):
        result = self.interpreterData.GetArgumentValue(self.args[1]) + self.interpreterData.GetArgumentValue(self.args[2]) 
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)

# SUB <var> <symb1> <symb2>
class Sub(Instruction):
    def Execute(self): 
        result = self.interpreterData.GetArgumentValue(self.args[1]) - self.interpreterData.GetArgumentValue(self.args[2])
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)

# MUL <var> <symb1> <symb2>
class Mul(Instruction):
    def Execute(self):
        result = self.interpreterData.GetArgumentValue(self.args[1]) * self.interpreterData.GetArgumentValue(self.args[2])
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)

# IDIV <var> <symb1> <symb2>
class IDiv(Instruction):
    def Execute(self):
        result = self.interpreterData.GetArgumentValue(self.args[1]) // self.interpreterData.GetArgumentValue(self.args[2])
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)

# DIV <var> <symb1> <symb2>
class Div(Instruction):
    def Execute(self):
        result = self.interpreterData.GetArgumentValue(self.args[1]) / self.interpreterData.GetArgumentValue(self.args[2])
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)

# LT <var> <symb1> <symb2>
class Lt(Instruction):
    def Execute(self):
        result = self.interpreterData.GetArgumentValue(self.args[1]) < self.interpreterData.GetArgumentValue(self.args[2])
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)

# GT <var> <symb1> <symb2>
class Gt(Instruction):
    def Execute(self):
        result = self.interpreterData.GetArgumentValue(self.args[1]) > self.interpreterData.GetArgumentValue(self.args[2])
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)

# EQ <var> <symb1> <symb2>
class Eq(Instruction):
    def Execute(self):
        result = self.interpreterData.GetArgumentValue(self.args[1]) == self.interpreterData.GetArgumentValue(self.args[2])
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)

# AND <var> <symb1> <symb2>
class And(Instruction):
    def Execute(self):
        arg1 = self.interpreterData.GetArgumentValue(self.args[1])
        arg2 = self.interpreterData.GetArgumentValue(self.args[2])
        result = arg1.__and__(arg2)
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)

# OR <var> <symb1> <symb2>
class Or(Instruction):
    def Execute(self):
        arg1 = self.interpreterData.GetArgumentValue(self.args[1])
        arg2 = self.interpreterData.GetArgumentValue(self.args[2])
        result = arg1.__or__(arg2)
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)

# NOT <var> <symb>
class Not(Instruction):
    def Execute(self):
        result = not self.interpreterData.GetArgumentValue(self.args[1])
        self.interpreterData.UpdateVariable(str(self.args[0].value), IPPBool(result))

# INT2CHAR <var> <symb>
class Int2Char(Instruction):
    def Execute(self):
        argValue = self.interpreterData.GetArgumentValue(self.args[1])
        if(not isinstance(argValue, IPPInt)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        try:
            result = IPPString(chr(argValue))
            self.interpreterData.UpdateVariable(str(self.args[0].value), result)
        except ValueError:
            raise StringOperationError("Chyba: Neplatny kod znaku!")

# STRI2INT <var> <symb1> <symb2>
class Stri2Int(Instruction):
    def Execute(self):
        string = self.interpreterData.GetArgumentValue(self.args[1])
        index = self.interpreterData.GetArgumentValue(self.args[2])
        if(not isinstance(string, IPPString)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        if(not isinstance(index, IPPInt)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        if(index > IPPInt(len(string) - 1) or index < IPPInt(0)):
            raise StringOperationError("Chyba: Neplatny index!")
        result = IPPInt(ord(string[index]))
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)

# CLEARS
class Clears(Instruction):
    def Execute(self):
        self.interpreterData.ClearDataStack()

# READ <var> <type>
class Read(Instruction):
    def Execute(self):
        argValue = self.interpreterData.GetArgumentValue(self.args[1])
        userInput = self.interpreterData.GetUserInputStream().readline()
        if(userInput == ""):
            self.interpreterData.UpdateVariable(str(self.args[0].value), Nil())
            return
        userInput = userInput.strip("\n")
        if(argValue == IPPString("int")):
            try:
                result = IPPInt(userInput)
            except InvalidStringToIntError:
                result = Nil() 
        elif(argValue == IPPString("bool")):
            result = IPPBool(userInput.lower() == "true")
        elif(argValue == IPPString("string")):
            result = IPPString.CreateFromRead(userInput)
        elif(argValue == IPPString("float")):
            try:
                result = IPPFloat(userInput)
            except InvalidStringToFloatError:
                result = Nil()
        else:
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)

# FLOAT2INT <var> <symb>
class Float2Int(Instruction):
    def Execute(self):
        argValue = self.interpreterData.GetArgumentValue(self.args[1])
        if(not isinstance(argValue, IPPFloat)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        result = IPPInt(int(argValue))
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)

# INT2FLOAT <var> <symb>
class Int2Float(Instruction):
    def Execute(self):
        argValue = self.interpreterData.GetArgumentValue(self.args[1])
        if(not isinstance(argValue, IPPInt)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        result = IPPFloat(float(argValue))
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)

# CONCAT <var> <symb1> <symb2>
class Concat(Instruction):
    def Execute(self):
        string1 = self.interpreterData.GetArgumentValue(self.args[1])
        string2 = self.interpreterData.GetArgumentValue(self.args[2])
        if(not isinstance(string1, IPPString)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        if(not isinstance(string2, IPPString)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        result = string1.Concat(string2)
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)

# STRLEN <var> <symb>
class Strlen(Instruction):
    def Execute(self):
        string = self.interpreterData.GetArgumentValue(self.args[1])
        if(not isinstance(string, IPPString)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        result = IPPInt(len(string))
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)

# GETCHAR <var> <symb1> <symb2>
class Getchar(Instruction):
    def Execute(self):
        string = self.interpreterData.GetArgumentValue(self.args[1])
        index = self.interpreterData.GetArgumentValue(self.args[2])
        if(not isinstance(string, IPPString)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        if(not isinstance(index, IPPInt)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        if(index > IPPInt(len(string) - 1) or index < IPPInt(0)):
            raise StringOperationError("Chyba: Neplatny index!")
        result = IPPString(string[index])
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)

# SETCHAR <var> <symb1> <symb2>
class Setchar(Instruction):
    def Execute(self):
        string = self.interpreterData.GetArgumentValue(self.args[0])
        index = self.interpreterData.GetArgumentValue(self.args[1])
        char = self.interpreterData.GetArgumentValue(self.args[2])
        if(not isinstance(string, IPPString)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        if(not isinstance(index, IPPInt)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        if(not isinstance(char, IPPString)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        if(index > IPPInt(len(string) - 1) or index < IPPInt(0)):
            raise StringOperationError("Chyba: Neplatny index!")
        if(len(char) < 1):
            raise StringOperationError("Chyba: Prazdny retezec v instrukci setchar!")
        result = IPPString(str(string)[:index] + str(char[0]) + str(string)[index + IPPInt(1):])
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)

# TYPE <var> <symb>
class Type(Instruction):
    def Execute(self):
        argType = self.interpreterData.GetArgumentType(self.args[1])
        self.interpreterData.UpdateVariable(str(self.args[0].value), IPPString(argType))
    
# LABEL <label>
class Label(Instruction):
    def Execute(self):
         pass

# JUMP <label>
class Jump(Instruction):
    def Execute(self):
        argValue = self.interpreterData.GetArgumentValue(self.args[0])
        if(not isinstance(argValue, IPPString)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        if(argValue not in self.interpreterData.labels):
            raise UndefinedLabelError("Chyba: Neplatne navesti!")
        self.interpreterData.SetInstructionPointer(self.interpreterData.labels[argValue])

# JUMPIFEQ <label> <symb1> <symb2>
class Jumpifeq(Instruction):
    def Execute(self):
        argValue1 = self.interpreterData.GetArgumentValue(self.args[1])
        argValue2 = self.interpreterData.GetArgumentValue(self.args[2])
        label = self.interpreterData.GetArgumentValue(self.args[0])
        if(isinstance(label, IPPString)):
            if(argValue1 == argValue2):
                self.interpreterData.SetInstructionPointer(self.interpreterData.GetJumpDestination(label))
        else:
            raise XMLInputError("Chyba: Neplatny typ pro instrukci JUMPIFEQ, ocekavan label!")

# JUMPIFNEQ <label> <symb1> <symb2>
class Jumpifneq(Instruction):
    def Execute(self):
        argValue1 = self.interpreterData.GetArgumentValue(self.args[1])
        argValue2 = self.interpreterData.GetArgumentValue(self.args[2])
        label = self.interpreterData.GetArgumentValue(self.args[0])
        if(isinstance(label, IPPString)):
            if(argValue1 != argValue2):
                self.interpreterData.SetInstructionPointer(self.interpreterData.GetJumpDestination(label))
        else:
            raise XMLInputError("Chyba: Neplatny typ pro instrukci JUMPIFNEQ, ocekavan label!")

# ADDS
class Adds(Instruction):
    def Execute(self):
        argValue2 = self.interpreterData.PopDataStack()
        argValue1 = self.interpreterData.PopDataStack()
        self.interpreterData.PushDataStack(argValue1 + argValue2)

# SUBS
class Subs(Instruction):
    def Execute(self):
            argValue2 = self.interpreterData.PopDataStack()
            argValue1 = self.interpreterData.PopDataStack()
            self.interpreterData.PushDataStack(argValue1 - argValue2)

# MULS
class Muls(Instruction):
    def Execute(self):
        argValue2 = self.interpreterData.PopDataStack()
        argValue1 = self.interpreterData.PopDataStack()
        self.interpreterData.PushDataStack(argValue1 * argValue2)

# IDIVS
class IDivs(Instruction):
    def Execute(self):
        argValue2 = self.interpreterData.PopDataStack()
        argValue1 = self.interpreterData.PopDataStack()
        self.interpreterData.PushDataStack(argValue1 // argValue2)

# DIVS
class Divs(Instruction):
    def Execute(self):
        argValue2 = self.interpreterData.PopDataStack()
        argValue1 = self.interpreterData.PopDataStack()
        self.interpreterData.PushDataStack(argValue1 / argValue2)

# LTS
class Lts(Instruction):
    def Execute(self):
        argValue2 = self.interpreterData.PopDataStack()
        argValue1 = self.interpreterData.PopDataStack()
        self.interpreterData.PushDataStack(argValue1 < argValue2)


# GTS
class Gts(Instruction):
    def Execute(self):
        argValue2 = self.interpreterData.PopDataStack()
        argValue1 = self.interpreterData.PopDataStack()
        self.interpreterData.PushDataStack(argValue1 > argValue2)
# EQS
class Eqs(Instruction):
    def Execute(self):
        argValue2 = self.interpreterData.PopDataStack()
        argValue1 = self.interpreterData.PopDataStack()
        self.interpreterData.PushDataStack(argValue1 == argValue2)

# ANDS
class Ands(Instruction):
    def Execute(self):
        argValue2 = self.interpreterData.PopDataStack()
        argValue1 = self.interpreterData.PopDataStack()
        self.interpreterData.PushDataStack(argValue1 and argValue2)
# ORS
class Ors(Instruction):
    def Execute(self):
        argValue2 = self.interpreterData.PopDataStack()
        argValue1 = self.interpreterData.PopDataStack()
        self.interpreterData.PushDataStack(argValue1 or argValue2)

# NOTS
class Nots(Instruction):
    def Execute(self):
        argValue1 = self.interpreterData.PopDataStack()
        self.interpreterData.PushDataStack(IPPBool(not argValue1))

# INT2CHARS
class Int2Chars(Instruction):
    def Execute(self): 
        argValue1 = self.interpreterData.PopDataStack()
        if(not isinstance(argValue1, IPPInt)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        try:
            self.interpreterData.PushDataStack(IPPString(chr(argValue1)))
        except ValueError:
            raise StringOperationError("Chyba: Neplatny znak!")


# STRI2INTS
class Stri2Ints(Instruction):
    def Execute(self):
        pos = self.interpreterData.PopDataStack()
        string = self.interpreterData.PopDataStack()
        if(not isinstance(pos, IPPInt) or not isinstance(string, IPPString)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!") 
        if(pos > IPPInt(len(string)) - IPPInt(1)):
            raise StringOperationError("Chyba: Neplatny index!")
        self.interpreterData.PushDataStack(IPPInt(ord(string[pos]))) 

# INT2FLOATS
class Int2Floats(Instruction):
    def Execute(self):
        argValue1 = self.interpreterData.PopDataStack()
        if(not isinstance(argValue1, IPPInt)):
            print(type(argValue1))
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        self.interpreterData.PushDataStack(IPPFloat(float(argValue1)))
    
# JUMPIFEQS <label>
class Jumpifeqs(Instruction): 
    def Execute(self):
        argValue2 = self.interpreterData.PopDataStack()
        argValue1 = self.interpreterData.PopDataStack() 
        if(argValue1 != argValue2):
            return
        label = self.interpreterData.GetArgumentValue(self.args[0])
        if(label not in self.interpreterData.labels):
            raise UndefinedLabelError("Chyba: Neplatne navesti!")
        if(isinstance(label, IPPString)):
            self.interpreterData.SetInstructionPointer(self.interpreterData.GetJumpDestination(label))

# JUMIPFNEQS <label>
class Jumpifneqs(Instruction):
    def Execute(self):
        argValue2 = self.interpreterData.PopDataStack()
        argValue1 = self.interpreterData.PopDataStack() 
        if(argValue1 == argValue2):
            return
        label = self.interpreterData.GetArgumentValue(self.args[0])
        if(label not in self.interpreterData.labels):
            raise UndefinedLabelError("Chyba: Neplatne navesti!")
        if(isinstance(label, IPPString)):
            self.interpreterData.SetInstructionPointer(self.interpreterData.GetJumpDestination(label))
# DPRINT <symb> 
class Dprint(Instruction):
    def Execute(self):
        sys.stderr.write(str(self.interpreterData.GetArgumentValue(self.args[0])))
# BREAK
class Break(Instruction):
    def Execute(self):
        pass
# EXIT <symb>
class Exit(Instruction):
    # Vyvolává výjímku ExitInstruction, aby se interpret neukončil před posbíráním statistik
    def Execute(self):
        argValue1 = self.interpreterData.GetArgumentValue(self.args[0])
        if(not isinstance(argValue1, IPPInt)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        if(argValue1 < IPPInt(0) or argValue1 > IPPInt(49)):
            raise OperandValueError("Chyba: Hodnota argumentu instrukce exit je mimo meze <0,49>!")
        raise ExitInstruction(argValue1)

# FLOAT2INTS
class Float2Ints(Instruction):
    def Execute(self):
        argValue = self.interpreterData.PopDataStack()
        if(not isinstance(argValue, IPPFloat)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        result = IPPInt(int(argValue))
        self.interpreterData.PushDataStack(result)

# READ <var> <type>
class Write(Instruction):
    def Execute(self):
        print(self.interpreterData.GetArgumentValue(self.args[0]), end='')

# Statická tovární třída pro vytváření instancí instrukcí
class InstructionFactory:
    # Slovník jmen instrukcí s jejich příslušnými třídami a počtem a typem argumentů
    instructions: dict =  {   
        "MOVE": (Move, ["var", "symb"]),
        "CREATEFRAME": (CreateFrame, []),
        "PUSHFRAME": (PushFrame, []),
        "POPFRAME": (PopFrame, []),
        "DEFVAR": (Defvar, ["var"]),
        "CALL": (Call, ["label"]),
        "RETURN" : (Return, []),
        "PUSHS": (Pushs, ["symb"]),
        "POPS": (Pops, ["var"]),
        "CLEARS": (Clears, []),
        "ADD": (Add, ["var", "symb", "symb"]),
        "SUB": (Sub, ["var", "symb", "symb"]),
        "MUL": (Mul, ["var", "symb", "symb"]),
        "DIV": (Div, ["var", "symb", "symb"]),
        "IDIV": (IDiv, ["var", "symb", "symb"]),
        "ADDS": (Adds, []),
        "SUBS": (Subs, []),
        "MULS": (Muls, []),
        "DIVS": (Divs, []),
        "IDIVS": (IDivs, []),
        "LT": (Lt, ["var", "symb", "symb"]),
        "GT": (Gt, ["var", "symb", "symb"]),
        "EQ": (Eq, ["var", "symb", "symb"]),
        "LTS": (Lts, []),
        "GTS": (Gts, []),
        "EQS": (Eqs, []),
        "AND": (And, ["var", "symb", "symb"]),
        "OR": (Or, ["var", "symb", "symb"]),
        "NOT": (Not, ["var", "symb"]),
        "ANDS": (Ands, []),
        "ORS": (Ors, []),
        "NOTS": (Nots, []),
        "INT2FLOAT": (Int2Float, ["var", "symb"]),
        "FLOAT2INT": (Float2Int, ["var", "symb"]),
        "INT2CHAR": (Int2Char, ["var", "symb"]),
        "STRI2INT": (Stri2Int, ["var", "symb", "symb"]),
        "INT2FLOATS": (Int2Floats, []),
        "FLOAT2INTS": (Float2Ints, []),
        "INT2CHARS": (Int2Chars, []),
        "STRI2INTS": (Stri2Ints, []),
        "READ": (Read, ["var", "type"]),
        "WRITE": (Write, ["symb"]),
        "CONCAT": (Concat, ["var", "symb", "symb"]),
        "STRLEN": (Strlen, ["var", "symb"]),
        "GETCHAR": (Getchar, ["var", "symb", "symb"]),
        "SETCHAR": (Setchar, ["var", "symb", "symb"]),
        "TYPE": (Type, ["var", "symb"]),
        "LABEL": (Label, ["label"]),
        "JUMP": (Jump, ["label"]),
        "JUMPIFEQ": (Jumpifeq, ["label", "symb", "symb"]),
        "JUMPIFNEQ": (Jumpifneq, ["label", "symb", "symb"]),
        "JUMPIFEQS": (Jumpifeqs, ["label"]),
        "JUMPIFNEQS": (Jumpifneqs, ["label"]),
        "EXIT": (Exit, ["symb"]),
        "BREAK": (Break, []),
        "DPRINT": (Dprint, ["symb"]),
    }

    # Vytvoří instanci konkrétní instrukce z XML elementu a vrátí ji
    @staticmethod
    def CreateInstruction(xmlInstruction: et.Element, interpreterData: InterpreterData):
        opcode = xmlInstruction.attrib["opcode"].upper()
        if(opcode not in InstructionFactory.instructions):
            raise XMLInputError(f"Chyba: Neplatny operační kód '{opcode}'!")
        order = int(xmlInstruction.attrib["order"])
        args = InstructionFactory._getArgs(xmlInstruction)
        # Nalezeni instrukce ve slovníku a zavolání konstruktoru
        instClass = InstructionFactory.instructions.get(opcode)
        if(instClass is None):
            raise XMLInputError(f"Chyba: Neplatny operační kód '{opcode}'!")
        instClass[0](args, interpreterData, order)
        inst = InstructionFactory.instructions[opcode][0](args, interpreterData, order)
        return inst 

    # Získá argumenty instrukce z její XML reprezentace a zkontroluje zda jsou validní, vyvolá výjímku XMLInputError pokud najde chybu
    # Jinak vraci seznam objektů Argument
    @staticmethod
    def _getArgs(xmlInstruction: et.Element):
        opcode = xmlInstruction.attrib["opcode"].upper()
        args: List[Argument] = []
        argsElements = xmlInstruction.findall("*")
        correctArguments = InstructionFactory.instructions.get(opcode)
        if(correctArguments is None):
            raise XMLInputError(f"Chyba: Neplatny operační kód '{opcode}'!")
        correctArguments = correctArguments[1]
        if(len(argsElements) != len(correctArguments)):
            raise XMLInputError(f"Chyba: Nesprávný počet argumentů instrukce '{opcode}'!")
        for i in range (1, len(correctArguments) + 1):
            arg = xmlInstruction.find('arg' + str(i))
            if(arg is None):
                raise XMLInputError(f"Chyba: Chybí argument instrukce '{opcode}'!")
            argType = arg.get("type")
            if(argType is None):
                raise XMLInputError(f"Chyba: Chybí atribut 'type' argumentu instrukce '{opcode}'!")
            if(correctArguments[i - 1] == "symb"):
                if(argType not in ["var", "int", "bool", "string", "nil", "float"]):
                    raise XMLInputError(f"Chyba: Neplatný typ argumentu instrukce '{opcode}'!")
            else:
                if(argType != correctArguments[i - 1]):
                    raise XMLInputError(f"Chyba: Neplatný typ argumentu instrukce '{opcode}'!")            
            argObject = ArgumentFactory.Create(arg)
            if(argObject is None):
                raise XMLInputError(f"Chyba: Neplatný argument instrukce '{opcode}' - {arg}!")
            args.append(argObject)
        return args
         


