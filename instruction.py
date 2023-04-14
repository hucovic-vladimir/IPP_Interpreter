from typing import List
from xml.etree.ElementTree import Element, tostring
import xml.etree.ElementTree as et
from argument import *
from InterpreterData import *
from exceptions import *

class Instruction:

    def __init__(self, args: List[Argument], interpreterData: InterpreterData, order: int) -> None:
        self.args = args
        self.interpreterData = interpreterData
        self.order = order

    def __str__(self):
        return f"{self.__class__.__name__} Order: {self.order} Arguments: {(' '.join(str(arg) for arg in self.args))} "

    def Execute(self, interpreterData: InterpreterData):
       pass 

# Instruction classes in order as in InstructonFactory dictionary 
class Move(Instruction):
    def Execute(self):
        argValue = self.interpreterData.GetArgumentValue(self.args[1])
        self.interpreterData.UpdateVariable(str(self.args[0]), argValue)

class CreateFrame(Instruction):
    def Execute(self):
        self.interpreterData.CreateFrame()

class PushFrame(Instruction):
    def Execute(self) -> None:
        self.interpreterData.PushFrame()

class PopFrame(Instruction):
    def Execute(self):
        self.interpreterData.PopFrame()


class Defvar(Instruction):
    def Execute(self):
        self.interpreterData.AddVariable(str(self.args[0])) 


class Call(Instruction):
    def Execute(self):
        self.interpreterData.PushCallStack(self.interpreterData.GetInstructionPointer())
        newInstrPointer = self.interpreterData.GetJumpDestination(str(self.args[0].value))
        self.interpreterData.SetInstructionPointer(newInstrPointer)


class Return(Instruction):
    def Execute(self):
        self.interpreterData.SetInstructionPointer(self.interpreterData.PopCallStack())

class Pushs(Instruction):
    def Execute(self):
        self.interpreterData.PushDataStack(self.interpreterData.GetArgumentValue(self.args[0]))

class Pops(Instruction):
    def Execute(self):
        self.interpreterData.UpdateVariable(str(self.args[0]), self.interpreterData.PopDataStack())


class Add(Instruction):
    def Execute(self):
        result = self.interpreterData.GetArgumentValue(self.args[1]) + self.interpreterData.GetArgumentValue(self.args[2]) 
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)



class Sub(Instruction):
    def Execute(self): 
        result = self.interpreterData.GetArgumentValue(self.args[1]) - self.interpreterData.GetArgumentValue(self.args[2])
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)


class Mul(Instruction):
    def Execute(self):
        result = self.interpreterData.GetArgumentValue(self.args[1]) * self.interpreterData.GetArgumentValue(self.args[2])
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)


class IDiv(Instruction):
    def Execute(self):
        result = self.interpreterData.GetArgumentValue(self.args[1]) // self.interpreterData.GetArgumentValue(self.args[2])
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)


class Div(Instruction):
    def Execute(self):
        result = self.interpreterData.GetArgumentValue(self.args[1]) / self.interpreterData.GetArgumentValue(self.args[2])
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)


class Lt(Instruction):
    def Execute(self):
        result = self.interpreterData.GetArgumentValue(self.args[1]) < self.interpreterData.GetArgumentValue(self.args[2])
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)


class Gt(Instruction):
    def Execute(self):
        result = self.interpreterData.GetArgumentValue(self.args[1]) > self.interpreterData.GetArgumentValue(self.args[2])
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)


class Eq(Instruction):
    def Execute(self):
        result = self.interpreterData.GetArgumentValue(self.args[1]) == self.interpreterData.GetArgumentValue(self.args[2])
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)


class And(Instruction):
    def Execute(self):
        arg1 = self.interpreterData.GetArgumentValue(self.args[1])
        arg2 = self.interpreterData.GetArgumentValue(self.args[2])
        result = arg1.__and__(arg2)
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)


class Or(Instruction):
    def Execute(self):
        arg1 = self.interpreterData.GetArgumentValue(self.args[1])
        arg2 = self.interpreterData.GetArgumentValue(self.args[2])
        result = arg1.__or__(arg2)
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)


class Not(Instruction):
    def Execute(self):
        result = not self.interpreterData.GetArgumentValue(self.args[1])
        self.interpreterData.UpdateVariable(str(self.args[0].value), IPPBool(result))


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


class Clears(Instruction):
    def Execute(self):
        self.interpreterData.ClearDataStack()


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


class Float2Int(Instruction):
    def Execute(self):
        argValue = self.interpreterData.GetArgumentValue(self.args[1])
        if(not isinstance(argValue, IPPFloat)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        result = IPPInt(int(argValue))
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)


class Int2Float(Instruction):
    def Execute(self):
        argValue = self.interpreterData.GetArgumentValue(self.args[1])
        if(not isinstance(argValue, IPPInt)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        result = IPPFloat(float(argValue))
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)


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


class Strlen(Instruction):
    def Execute(self):
        string = self.interpreterData.GetArgumentValue(self.args[1])
        if(not isinstance(string, IPPString)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        result = IPPInt(len(string))
        self.interpreterData.UpdateVariable(str(self.args[0].value), result)


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


class Type(Instruction):
    def Execute(self):
        argType = self.interpreterData.GetArgumentType(self.args[1])
        self.interpreterData.UpdateVariable(str(self.args[0].value), IPPString(argType))
    
class Label(Instruction):
    def Execute(self):
         pass


class Jump(Instruction):
    def Execute(self):
        argValue = self.interpreterData.GetArgumentValue(self.args[0])
        if(not isinstance(argValue, IPPString)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        if(argValue not in self.interpreterData.labels):
            raise UndefinedLabelError("Chyba: Neplatne navesti!")
        self.interpreterData.SetInstructionPointer(self.interpreterData.labels[argValue])

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


class Adds(Instruction):
    def Execute(self):
        argValue2 = self.interpreterData.PopDataStack()
        argValue1 = self.interpreterData.PopDataStack()
        self.interpreterData.PushDataStack(argValue1 + argValue2)


class Subs(Instruction):
    def Execute(self):
            argValue2 = self.interpreterData.PopDataStack()
            argValue1 = self.interpreterData.PopDataStack()
            self.interpreterData.PushDataStack(argValue1 - argValue2)


class Muls(Instruction):
    def Execute(self):
        argValue2 = self.interpreterData.PopDataStack()
        argValue1 = self.interpreterData.PopDataStack()
        self.interpreterData.PushDataStack(argValue1 * argValue2)


class IDivs(Instruction):
    def Execute(self):
        argValue2 = self.interpreterData.PopDataStack()
        argValue1 = self.interpreterData.PopDataStack()
        self.interpreterData.PushDataStack(argValue1 // argValue2)


class Divs(Instruction):
    def Execute(self):
        argValue2 = self.interpreterData.PopDataStack()
        argValue1 = self.interpreterData.PopDataStack()
        self.interpreterData.PushDataStack(argValue1 / argValue2)


class Lts(Instruction):
    def Execute(self):
        argValue2 = self.interpreterData.PopDataStack()
        argValue1 = self.interpreterData.PopDataStack()
        self.interpreterData.PushDataStack(argValue1 < argValue2)



class Gts(Instruction):
    def Execute(self):
        argValue2 = self.interpreterData.PopDataStack()
        argValue1 = self.interpreterData.PopDataStack()
        self.interpreterData.PushDataStack(argValue1 > argValue2)

class Eqs(Instruction):
    def Execute(self):
        argValue2 = self.interpreterData.PopDataStack()
        argValue1 = self.interpreterData.PopDataStack()
        self.interpreterData.PushDataStack(argValue1 == argValue2)


class Ands(Instruction):
    def Execute(self):
        argValue2 = self.interpreterData.PopDataStack()
        argValue1 = self.interpreterData.PopDataStack()
        self.interpreterData.PushDataStack(argValue1 and argValue2)

class Ors(Instruction):
    def Execute(self):
        argValue2 = self.interpreterData.PopDataStack()
        argValue1 = self.interpreterData.PopDataStack()
        self.interpreterData.PushDataStack(argValue1 or argValue2)


class Nots(Instruction):
    def Execute(self):
        argValue1 = self.interpreterData.PopDataStack()
        self.interpreterData.PushDataStack(IPPBool(not argValue1))


class Int2Chars(Instruction):
    def Execute(self): 
        argValue1 = self.interpreterData.PopDataStack()
        if(not isinstance(argValue1, IPPInt)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        try:
            self.interpreterData.PushDataStack(IPPString(chr(argValue1)))
        except ValueError:
            raise StringOperationError("Chyba: Neplatny znak!")



class Stri2Ints(Instruction):
    def Execute(self):
        pos = self.interpreterData.PopDataStack()
        string = self.interpreterData.PopDataStack()
        if(not isinstance(pos, IPPInt) or not isinstance(string, IPPString)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!") 
        if(pos > IPPInt(len(string)) - IPPInt(1)):
            raise StringOperationError("Chyba: Neplatny index!")
        self.interpreterData.PushDataStack(IPPInt(ord(string[pos]))) 


class Int2Floats(Instruction):
    def Execute(self):
        argValue1 = self.interpreterData.PopDataStack()
        if(not isinstance(argValue1, IPPInt)):
            print(type(argValue1))
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        self.interpreterData.PushDataStack(IPPFloat(float(argValue1)))
    

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
   
class Dprint(Instruction):
    def Execute(self):
        sys.stderr.write(str(self.interpreterData.GetArgumentValue(self.args[0])))

class Break(Instruction):
    def Execute(self):
        pass

class Exit(Instruction):
    def Execute(self):
        argValue1 = self.interpreterData.GetArgumentValue(self.args[0])
        if(not isinstance(argValue1, IPPInt)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        if(argValue1 < IPPInt(0) or argValue1 > IPPInt(49)):
            raise OperandValueError("Chyba: Hodnota argumentu instrukce exit je mimo meze <0,49>!")
        raise ExitInstruction(argValue1)

class Float2Ints(Instruction):
    def Execute(self):
        argValue = self.interpreterData.PopDataStack()
        if(not isinstance(argValue, IPPFloat)):
            raise OperandTypeError("Chyba: Neplatny typ argumentu!")
        result = IPPInt(int(argValue))
        self.interpreterData.PushDataStack(result)

class Write(Instruction):
    def Execute(self):
        print(self.interpreterData.GetArgumentValue(self.args[0]), end='')


class InstructionFactory:
    instructions =  {   
        # instrukce IPPCode23
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

 
    @staticmethod
    def CreateInstruction(xmlInstruction: et.Element, interpreterData: InterpreterData):
        opcode = xmlInstruction.attrib["opcode"].upper()
        if(opcode not in InstructionFactory.instructions):
            raise XMLInputError(f"Chyba: Neplatny operační kód '{opcode}'!")
        order = int(xmlInstruction.attrib["order"])
        args = InstructionFactory.GetArgs(xmlInstruction)
        inst = InstructionFactory.instructions[opcode][0](args, interpreterData, order)
        return inst 

    # Ziska argumenty instrukce a zkontroluje zda jsou validni, vyvola vyjimku XMLInputError pokud najde chybu
    # Jinak vraci seznam objektů Argument
    @staticmethod
    def GetArgs(xmlInstruction: et.Element):
        opcode = xmlInstruction.attrib["opcode"].upper()
        args: List[Argument] = []
        argsElements = xmlInstruction.findall("*")
        correctArguments = InstructionFactory.instructions[opcode][1]
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
         


