from typing import List
from variable import *
from xml.etree.ElementTree import Element, tostring
import xml.etree.ElementTree as et
from argument import *

class Instruction:
    def __init__(self, opcode, args: List, order: int) -> None:
        self.opcode = opcode
        self.args = args
        self.order = order

    def __str__(self) -> str:
        return f"{self.opcode} {self.args}"

    @classmethod
    def Create(cls, instruction: Element):
        opcode = instruction.attrib['opcode']
        args: List[Argument] = []
        argsElements = instruction.findall("*")
        for i in range (1, len(argsElements) + 1):
            arg = instruction.find('arg' + str(i))
            if(arg is None):
                print("Chyba: Chybejici argument instrukce!", file=sys.stderr)
                exit(32)

            args.append(Argument.CreateArgument(arg))
        order = int(instruction.attrib['order'])
        instr = Instruction(opcode, args, order)
        return instr


