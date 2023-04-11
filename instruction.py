from typing import List
from variable import *
from xml.etree.ElementTree import Element, tostring
import xml.etree.ElementTree as et
from argument import *
from InterpreterData import *
from exceptions import *

class Instruction:
    _opcodeArgcount = {
        "MOVE": 2, "CREATEFRAME": 0, "PUSHFRAME": 0, "POPFRAME": 0, "DEFVAR": 1, "CALL": 1, "RETURN": 0, "PUSHS": 1, "POPS": 1, "WRITE": 1,
        "LABEL": 1, "JUMP": 1, "JUMPIFEQ": 3, "JUMPIFNEQ": 3, "EXIT": 1, "DPRINT": 1, "BREAK": 0, "ADD": 3, "SUB": 3, "MUL": 3, "IDIV": 3,
        "DIV": 3, "LT": 3, "GT": 3, "EQ": 3, "AND": 3, "OR": 3, "NOT": 2, "INT2CHAR": 2, "STRI2INT": 3, "READ": 2, "STRLEN": 2, "TYPE": 2,
        "CONCAT": 3, "GETCHAR": 3, "SETCHAR": 3, "ADDS": 0, "SUBS": 0, "MULS": 0, "IDIVS": 0, "DIVS": 0, "LTS": 0, "GTS": 0, "EQS": 0,
        "ANDS": 0, "ORS": 0, "NOTS": 0, "INT2CHARS": 0, "STRI2INTS": 0, "JUMPIFEQS": 1, "JUMPIFNEQS": 1, "CLEARS": 0, "INT2FLOAT": 2,
        "FLOAT2INT": 2, "INT2FLOATS": 0, "FLOAT2INTS": 0 
    }

    def __init__(self, opcode, args: List[Argument], order: int) -> None:
        self.opcode = opcode
        self.args = args
        self.order = order

    def __str__(self) -> str:
        string = f"{self.order} {self.opcode} "
        for arg in self.args:
            string += f"{arg} "
        return string

    def _getArgumentType(self, arg: Argument, interpreterData: InterpreterData) -> str:
        if(isinstance(arg.value, VarName)):
            return interpreterData.GetVariableType(arg.value.name)
        else:
            if(isinstance(arg.value, IPPInt)):
                return "int"
            elif(isinstance(arg.value, IPPFloat)):
                return "float"
            elif(isinstance(arg.value, IPPString)):
                return "string"
            elif(isinstance(arg.value, IPPBool)):
                return "bool"
            elif(isinstance(arg.value, Nil)):
                return "nil"
            else:
                raise InterpreterInternalError("Chyba: Neznama chyba pri ziskavani typu argumentu!")

    def _getArgumentValue(self, arg: Argument, interpreterData: InterpreterData) -> Union[IPPInt, IPPFloat, IPPBool, IPPString, Nil]:
        if(isinstance(arg.value, VarName)):
            return self._getVarValue(arg.value.name, interpreterData)
        else:
            return arg.value

    def _getVarValue(self, varName: str, interpreterData: InterpreterData) -> Union[IPPInt, IPPFloat, IPPBool, IPPString, Nil]:
        if(interpreterData.GetVariableValue(varName) is None):
            raise MissingVariableError(f"Chyba: Promenna {varName} neni definovana!")
        return interpreterData.GetVariableValue(varName)

    def Execute(self, interpreterData: InterpreterData):
        if(self.opcode == "MOVE"):
            interpreterData.UpdateVariable(str(self.args[0].value), self._getArgumentValue(self.args[1], interpreterData)) 
        elif(self.opcode == "CREATEFRAME"):
            interpreterData.CreateFrame()
        elif(self.opcode == "PUSHFRAME"):
            interpreterData.PushFrame()
        elif(self.opcode == "POPFRAME"):
            interpreterData.PopFrame()
        elif(self.opcode == "DEFVAR"):
            interpreterData.AddVariable(str(self.args[0].value))
        elif(self.opcode == "CALL"):
            interpreterData.PushCallStack(interpreterData.GetInstructionPointer())
            newInstrPointer = interpreterData.GetJumpDestination(str(self.args[0].value))
            interpreterData.SetInstructionPointer(newInstrPointer)
        elif(self.opcode == "RETURN"):
            interpreterData.SetInstructionPointer(interpreterData.PopCallStack())
        elif(self.opcode == "PUSHS"):
            interpreterData.PushDataStack(self._getArgumentValue(self.args[0], interpreterData))
        elif(self.opcode == "POPS"):
            interpreterData.UpdateVariable(str(self.args[0]), interpreterData.PopDataStack())
        elif(self.opcode == "WRITE"):
            argValue = self._getArgumentValue(self.args[0], interpreterData)
            print(argValue, end='')
        elif(self.opcode == "ADD"):
            result = self._getArgumentValue(self.args[1], interpreterData) + self._getArgumentValue(self.args[2], interpreterData)
            interpreterData.UpdateVariable(str(self.args[0].value), result)
        elif(self.opcode == "SUB"):
            result = self._getArgumentValue(self.args[1], interpreterData) - self._getArgumentValue(self.args[2], interpreterData)
            interpreterData.UpdateVariable(str(self.args[0].value), result)
        elif(self.opcode == "MUL"):
            result = self._getArgumentValue(self.args[1], interpreterData) * self._getArgumentValue(self.args[2], interpreterData)
            interpreterData.UpdateVariable(str(self.args[0].value), result)
        elif(self.opcode == "IDIV"):
            result = self._getArgumentValue(self.args[1], interpreterData) // self._getArgumentValue(self.args[2], interpreterData)
            interpreterData.UpdateVariable(str(self.args[0].value), result)
        elif(self.opcode == "DIV"):
            result = self._getArgumentValue(self.args[1], interpreterData) / self._getArgumentValue(self.args[2], interpreterData)
            interpreterData.UpdateVariable(str(self.args[0].value), result)
        elif(self.opcode == "LT"):
            result = self._getArgumentValue(self.args[1], interpreterData) < self._getArgumentValue(self.args[2], interpreterData)
            interpreterData.UpdateVariable(str(self.args[0].value), result)
        elif(self.opcode == "GT"):
            result = self._getArgumentValue(self.args[1], interpreterData) > self._getArgumentValue(self.args[2], interpreterData)
            interpreterData.UpdateVariable(str(self.args[0].value), result)
        elif(self.opcode == "EQ"):
            result = self._getArgumentValue(self.args[1], interpreterData) == self._getArgumentValue(self.args[2], interpreterData)
            interpreterData.UpdateVariable(str(self.args[0].value), result)
        elif(self.opcode == "AND"):
            arg1 = self._getArgumentValue(self.args[1], interpreterData)
            arg2 = self._getArgumentValue(self.args[2], interpreterData)
            # Pri beznem "and" dojde ke zkracenemu vyhodnoceni a nenastane vyjimka pri porovnani nepodporovanych typu
            result = arg1.__and__(arg2)
            interpreterData.UpdateVariable(str(self.args[0].value), result)
        elif(self.opcode == "OR"):
            arg1 = self._getArgumentValue(self.args[1], interpreterData)
            arg2 = self._getArgumentValue(self.args[2], interpreterData)
            # Pri beznem "or" dojde ke zkracenemu vyhodnoceni a nenastane vyjimka pri porovnani nepodporovanych typu
            result = arg1.__or__(arg2)
            interpreterData.UpdateVariable(str(self.args[0].value), result) 
        elif(self.opcode == "NOT"):
            result = not self._getArgumentValue(self.args[1], interpreterData)
            interpreterData.UpdateVariable(str(self.args[0].value), IPPBool(result))
        elif(self.opcode == "INT2CHAR"):
            argValue = self._getArgumentValue(self.args[1], interpreterData)
            if(not isinstance(argValue, IPPInt)):
                raise OperandTypeError("Chyba: Neplatny typ argumentu!")
            try:
                result = IPPString(chr(argValue))
                interpreterData.UpdateVariable(str(self.args[0].value), result)
            except ValueError:
                raise StringOperationError("Chyba: Neplatny kod znaku!")

        elif(self.opcode == "STRI2INT"):
            string = self._getArgumentValue(self.args[1], interpreterData)
            index = self._getArgumentValue(self.args[2], interpreterData)
            if(not isinstance(string, IPPString)):
                raise OperandTypeError("Chyba: Neplatny typ argumentu!")
            if(not isinstance(index, IPPInt)):
                raise OperandTypeError("Chyba: Neplatny typ argumentu!")
            if(index > IPPInt(len(string) - 1) or index < IPPInt(0)):
                raise StringOperationError("Chyba: Neplatny index!")
            result = IPPInt(ord(string[index]))
            interpreterData.UpdateVariable(str(self.args[0].value), result)
        
        elif(self.opcode == "CLEARS"):
            interpreterData.ClearDataStack()

        elif(self.opcode == "READ"):
            argValue = self._getArgumentValue(self.args[1], interpreterData)
            userInput = interpreterData.GetUserInputStream().readline()
            # kontrola jestli se nenarazilo na EOF
            if(userInput == ""):
                interpreterData.UpdateVariable(str(self.args[0].value), Nil())
                return
            # odstrani znak noveho radku
            userInput = userInput[:-1]
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
            interpreterData.UpdateVariable(str(self.args[0].value), result)

        elif(self.opcode == "FLOAT2INT"):
            argValue = self._getArgumentValue(self.args[1], interpreterData)
            if(not isinstance(argValue, IPPFloat)):
                raise OperandTypeError("Chyba: Neplatny typ argumentu!")
            result = IPPInt(int(argValue))
            interpreterData.UpdateVariable(str(self.args[0].value), result)

        elif(self.opcode == "INT2FLOAT"):
            argValue = self._getArgumentValue(self.args[1], interpreterData)
            if(not isinstance(argValue, IPPInt)):
                raise OperandTypeError("Chyba: Neplatny typ argumentu!")
            result = IPPFloat(float(argValue))
            interpreterData.UpdateVariable(str(self.args[0].value), result)

        elif(self.opcode == "CONCAT"):
            string1 = self._getArgumentValue(self.args[1], interpreterData)
            string2 = self._getArgumentValue(self.args[2], interpreterData)
            if(not isinstance(string1, IPPString)):
                raise OperandTypeError("Chyba: Neplatny typ argumentu!")
            if(not isinstance(string2, IPPString)):
                raise OperandTypeError("Chyba: Neplatny typ argumentu!")
            result = string1.Concat(string2)
            interpreterData.UpdateVariable(str(self.args[0].value), result)

        elif(self.opcode == "STRLEN"):
            string = self._getArgumentValue(self.args[1], interpreterData)
            if(not isinstance(string, IPPString)):
                raise OperandTypeError("Chyba: Neplatny typ argumentu!")
            result = IPPInt(len(string))
            interpreterData.UpdateVariable(str(self.args[0].value), result)

        elif(self.opcode == "GETCHAR"):
            string = self._getArgumentValue(self.args[1], interpreterData)
            index = self._getArgumentValue(self.args[2], interpreterData)
            if(not isinstance(string, IPPString)):
                raise OperandTypeError("Chyba: Neplatny typ argumentu!")
            if(not isinstance(index, IPPInt)):
                raise OperandTypeError("Chyba: Neplatny typ argumentu!")
            if(index > IPPInt(len(string) - 1) or index < IPPInt(0)):
                raise StringOperationError("Chyba: Neplatny index!")
            result = IPPString(string[index])
            interpreterData.UpdateVariable(str(self.args[0].value), result)

        elif(self.opcode == "SETCHAR"):
            string = self._getArgumentValue(self.args[0], interpreterData)
            index = self._getArgumentValue(self.args[1], interpreterData)
            char = self._getArgumentValue(self.args[2], interpreterData)
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
            interpreterData.UpdateVariable(str(self.args[0].value), result)

        elif(self.opcode == "TYPE"):
            argType = self._getArgumentType(self.args[1], interpreterData)
            interpreterData.UpdateVariable(str(self.args[0].value), IPPString(argType))

        elif(self.opcode == "LABEL"):
            pass

        elif(self.opcode == "JUMP"):
            argValue = self._getArgumentValue(self.args[0], interpreterData)
            if(not isinstance(argValue, IPPString)):
                raise OperandTypeError("Chyba: Neplatny typ argumentu!")
            if(argValue not in interpreterData.labels):
                raise UndefinedLabelError("Chyba: Neplatne navesti!")
            interpreterData.SetInstructionPointer(interpreterData.labels[argValue])

        elif(self.opcode == "JUMPIFEQ"):
            argValue1 = self._getArgumentValue(self.args[1], interpreterData)
            argValue2 = self._getArgumentValue(self.args[2], interpreterData)
            label = self._getArgumentValue(self.args[0], interpreterData)
            if(isinstance(label, IPPString)):
                if(argValue1 == argValue2):
                    interpreterData.SetInstructionPointer(interpreterData.GetJumpDestination(label))
            else:
                raise XMLInputError("Chyba: Neplatny typ pro instrukci JUMPIFEQ, ocekavan label!")

        elif(self.opcode == "JUMPIFNEQ"):
            argValue1 = self._getArgumentValue(self.args[1], interpreterData)
            argValue2 = self._getArgumentValue(self.args[2], interpreterData)
            label = self._getArgumentValue(self.args[0], interpreterData)
            if(isinstance(label, IPPString)):
                if(argValue1 != argValue2):
                    interpreterData.SetInstructionPointer(interpreterData.GetJumpDestination(label))
            else:
                raise XMLInputError("Chyba: Neplatny typ pro instrukci JUMPIFNEQ, ocekavan label!")

        elif (self.opcode == "ADDS"):
            argValue2 = interpreterData.PopDataStack()
            argValue1 = interpreterData.PopDataStack()
            interpreterData.PushDataStack(argValue1 + argValue2)

        elif (self.opcode == "SUBS"):
            argValue2 = interpreterData.PopDataStack()
            argValue1 = interpreterData.PopDataStack()
            interpreterData.PushDataStack(argValue1 - argValue2)

        elif (self.opcode == "MULS"):
            argValue2 = interpreterData.PopDataStack()
            argValue1 = interpreterData.PopDataStack()
            interpreterData.PushDataStack(argValue1 * argValue2)

        elif (self.opcode == "IDIVS"):
            argValue2 = interpreterData.PopDataStack()
            argValue1 = interpreterData.PopDataStack()
            interpreterData.PushDataStack(argValue1 // argValue2)

        elif (self.opcode == "DIVS"):
            argValue2 = interpreterData.PopDataStack()
            argValue1 = interpreterData.PopDataStack()
            interpreterData.PushDataStack(argValue1 / argValue2)

        elif (self.opcode == "LTS"):
            argValue2 = interpreterData.PopDataStack()
            argValue1 = interpreterData.PopDataStack()
            interpreterData.PushDataStack(argValue1 < argValue2)

        elif (self.opcode == "GTS"):
            argValue2 = interpreterData.PopDataStack()
            argValue1 = interpreterData.PopDataStack()
            interpreterData.PushDataStack(argValue1 > argValue2)

        elif (self.opcode == "EQS"):
            argValue2 = interpreterData.PopDataStack()
            argValue1 = interpreterData.PopDataStack()
            interpreterData.PushDataStack(argValue1 == argValue2)

        elif (self.opcode == "ANDS"):
            argValue2 = interpreterData.PopDataStack()
            argValue1 = interpreterData.PopDataStack()
            interpreterData.PushDataStack(argValue1 and argValue2)

        elif (self.opcode == "ORS"):
            argValue2 = interpreterData.PopDataStack()
            argValue1 = interpreterData.PopDataStack()
            interpreterData.PushDataStack(argValue1 or argValue2)

        elif (self.opcode == "NOTS"):
            argValue1 = interpreterData.PopDataStack()
            interpreterData.PushDataStack(IPPBool(not argValue1))

        elif (self.opcode == "INT2CHARS"):
            argValue1 = interpreterData.PopDataStack()
            if(not isinstance(argValue1, IPPInt)):
                raise OperandTypeError("Chyba: Neplatny typ argumentu!")
            try:
                interpreterData.PushDataStack(IPPString(chr(argValue1)))
            except ValueError:
                raise StringOperationError("Chyba: Neplatny znak!")

        elif (self.opcode == "STRI2INTS"):
            pos = interpreterData.PopDataStack()
            string = interpreterData.PopDataStack()
            if(not isinstance(pos, IPPInt) or not isinstance(string, IPPString)):
                raise OperandTypeError("Chyba: Neplatny typ argumentu!") 
            try:
                interpreterData.PushDataStack(IPPInt(ord(string[pos])))
            except IndexError:
                raise StringOperationError("Chyba: Neplatny index!")

        elif (self.opcode == "INT2FLOATS"):
            argValue1 = interpreterData.PopDataStack()
            if(not isinstance(argValue1, IPPInt)):
                raise StringOperationError("Chyba: Neplatny typ argumentu!")
            interpreterData.PushDataStack(IPPFloat(float(argValue1)))


        elif(self.opcode == "JUMPIFEQS"):
            argValue2 = interpreterData.PopDataStack()
            argValue1 = interpreterData.PopDataStack() 
            if(argValue1 != argValue2):
                return
            label = self._getArgumentValue(self.args[0], interpreterData)
            if(label not in interpreterData.labels):
                raise UndefinedLabelError("Chyba: Neplatne navesti!")
            if(isinstance(label, IPPString)):
                interpreterData.SetInstructionPointer(interpreterData.GetJumpDestination(label))


        elif(self.opcode == "JUMPIFNEQS"):
            argValue2 = interpreterData.PopDataStack()
            argValue1 = interpreterData.PopDataStack() 
            if(argValue1 == argValue2):
                return
            label = self._getArgumentValue(self.args[0], interpreterData)
            if(label not in interpreterData.labels):
                raise UndefinedLabelError("Chyba: Neplatne navesti!")
            if(isinstance(label, IPPString)):
                interpreterData.SetInstructionPointer(interpreterData.GetJumpDestination(label))

        elif (self.opcode == "DPRINT"):
            pass
        elif (self.opcode == "BREAK"):
            pass

        elif (self.opcode == "EXIT"):
            argValue1 = self._getArgumentValue(self.args[0], interpreterData)
            if(not isinstance(argValue1, IPPInt)):
                raise OperandTypeError("Chyba: Neplatny typ argumentu!")
            if(argValue1 < IPPInt(0) or argValue1 > IPPInt(49)):
                raise OperandValueError("Chyba: Hodnota argumentu instrukce exit je mimo meze <0,49>!")
            exit(argValue1)
        

    @classmethod
    def CreateInstruction(cls, instruction: Element):
        if(instruction.attrib.get("opcode") is None):
            raise XMLInputError("Chyba: Chybejici operační kód instrukce!")
        opcode = instruction.attrib["opcode"].upper()
        if(opcode not in cls._opcodeArgcount):
            raise XMLInputError(f"Chyba: Neplatny operační kód '{opcode}'!")
        args = cls._getArguments(instruction)
        if(len(args) != cls._opcodeArgcount[opcode]):
            raise XMLInputError(f"Chyba: Nesprávný počet argumentů instrukce '{opcode}'!")
        order = int(instruction.attrib["order"])
        return Instruction(opcode, args, order)

    @classmethod 
    def _getArguments(cls, instruction: Element):
        args: List[Argument] = []
        argsElements = instruction.findall("*")
        for i in range (1, len(argsElements) + 1):
            arg = instruction.find('arg' + str(i))
            if(arg is None):
                print("Chyba: Chybejici argument instrukce!", file=sys.stderr)
                exit(32)

            argObject = ArgumentFactory.Create(arg)
            if(argObject is None):
                print("Chyba: Chyby argument instrukce!", file=sys.stderr)
                exit(32)
            args.append(argObject)
        return args

    
