from variable import *
from framemanager import *
from stack import *
from xml.etree import ElementTree as et
from instruction import *

# Interpreter class
class Interpreter:
    # vytvoří dočasný rámec
    def _createframe(self, instruction: Instruction):
        FrameManager.CreateTempFrame()

    def _defvar(self, instruction: Instruction):
        arg = instruction.args[0]
        if(arg.type == 'var'):
            varFrame = arg.value.split('@')[0]
            name = arg.value.split('@')[1]
            frame = FrameManager.GetFrame(varFrame)
            if(frame is None):
                print(f"Error: {frame} not defined!")
                exit(55)
            if(frame.GetVariable(name) is not None):
                print(f"Error: {name} already defined!")
                exit(52)
            frame.AddVariable(Variable(name, None, None))


    def _pushframe(self, instruction):
        FrameManager.PushFrame()

    def _write(self, instruction):
       for arg in instruction.args:
            if(arg.type == 'var'):
                varFrame = arg.value.split('@')[0]
                name = arg.value.split('@')[1]
                frame = FrameManager.GetFrame(varFrame)
                if(frame is None):
                    print(f"Error: {frame} not defined!")
                    exit(55)
                var = frame.GetVariable(name)
                if(var is None):
                    print(f"Error: {name} not defined!")
                    exit(54)
                print(var.value, end='')
            else:
                print(arg.value, end='')



    def _popframe(self, instruction):
        try:
            FrameManager.PopFrame()
        except IndexError:
            print("Error: LF not defined!")
            exit(55)

    def _call(self, instruction):
        print("call")

    def _return(self, instruction):
        print("return")
    
    def _pushs(self, instruction):
        print("pushs")

    def _pops(self, instruction):
        print("pops")
    
    def _add(self, instruction):
        dest = instruction.args[0]
        op1 = instruction.args[1]
        op2 = instruction.args[2]
        destVar = FrameManager.SearchVariable(dest.value) 
        try:
            result = op1.GetArgValue() + op2.GetArgValue()
        except TypeError:
            print(f"Chyba: Nekompatibilni operandy pro instrukci {instruction.opcode} {op1.type} {op2.type}!")
            exit(53)
        if(destVar is None):
            print(f"Error: {dest.value} not defined!")
            exit(54)
        destVar.SetValue(result, "int")


    def _sub(self, instruction):
        print("sub")

    def _mul(self, instruction):
        print("mul")

    def _idiv(self, instruction):
        print("idiv")

    def _lt(self, instruction):
        print("lt")

    def _gt(self, instruction):
        print("gt")

    def _eq(self, instruction):
        print("eq")

    def _and(self, instruction):
        print("and")

    def _or(self, instruction):
        print("or")

    def _not(self, instruction):
        print("not")

    def _int2char(self, instruction):
        print("int2char")

    def _stri2int(self, instruction):
        print("stri2int")

    def _read(self, instruction):
        print("read")

    def _concat(self, instruction):
        print("concat")

    def _move(self, instruction):
        dest = instruction.args[0]
        src = instruction.args[1]
        varDest = FrameManager.SearchVariable(dest.value)
        if(dest.type == 'var' and src.type == 'var'):
            varSrc = FrameManager.SearchVariable(src.value)
            try:
                if(varSrc is None or varDest is None):
                    raise AttributeError
                varDest.SetValue(varSrc.value, varSrc.type)
            except AttributeError:
                print(f"Error: {dest.value} not defined!")
                exit(54)
        else:
            try:
                if(varDest is None):
                    raise AttributeError
                varDest.SetValue(src. value, src.type)
            except AttributeError:
                print(f"Error: {dest.value} not defined!")
                exit(54) 

    def execute_instruction(self, instruction: Instruction) -> None:
        opcode = instruction.opcode
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
        elif(opcode == 'ADD'):
            self._add(instruction)
        elif(opcode == 'SUB'):
            self._sub(instruction)
        elif(opcode == 'MUL'):
            self._mul(instruction)
        elif(opcode == 'IDIV'):
            self._idiv(instruction)
        elif(opcode == 'LT'):
            self._lt(instruction)
        elif(opcode == 'GT'):
            self._gt(instruction)
        elif(opcode == 'EQ'):
            self._eq(instruction)
        elif(opcode == 'AND'):
            self._and(instruction)
        elif(opcode == 'OR'):
            self._or(instruction)
        elif(opcode == 'NOT'):
            self._not(instruction)
        elif(opcode == 'INT2CHAR'):
            self._int2char(instruction)
        elif(opcode == 'STRI2INT'):
            self._stri2int(instruction)
        elif(opcode == 'READ'):
            self._read(instruction)
        elif(opcode == 'WRITE'):
            self._write(instruction)
        elif(opcode == 'CONCAT'):
            self._concat(instruction)
        elif(opcode == 'MOVE'):
            self._move(instruction)
