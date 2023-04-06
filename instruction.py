from typing import List
from variable import *
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as et
from argument import *

class Instruction:
    def __init__(self, opcode, args: List) -> None:
        self.opcode = opcode
        self.args = args

    def __str__(self) -> str:
        return f"{self.opcode} {self.args}"

    @classmethod
    def CreateInstruction(cls, instruction: Element):
        opcode = instruction.attrib['opcode']
        args: List[Argument] = []
        for arg in instruction.findall("*"):
            args.append(Argument(arg.attrib["type"], arg.text))
        instr = Instruction(opcode, args)
        return instr


