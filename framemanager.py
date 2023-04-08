from frame import *
from stack import *
from variable import *
from typing import List, Any, Optional
import argparse as ap
import sys

class FrameManager:
    globalFrame = Frame("GF")
    tempFrame: Optional[Frame] = None
    frameStack = Stack()

    # Odstrani lokalni ramec z vrcholu zasobniku ramcu a ulozi ho do docasneho ramce
    @classmethod
    def PopFrame(cls) -> None:
        cls.tempFrame = cls.frameStack.pop()
   
    @classmethod
    def PushFrame(cls) -> None:
        if(cls.tempFrame is None):
            print("Chyba: Pokus o umisteni neexistujiciho ramce na zasobnik!", file=sys.stderr)
            exit(55)
        cls.frameStack.push(cls.tempFrame)
        cls.tempFrame = None

    @classmethod
    def CreateTempFrame(cls) -> None:
        cls.tempFrame = Frame("TF")

    @classmethod
    def AddToFrame(cls, frame_type: str, variable: Variable) -> None:
        frame = cls.GetFrame(frame_type)
        if(frame is None):
            print(f"Chyba: Ramec {frame_type} neni definovan!", file=sys.stderr)
            exit(55)
        frame.AddVariable(variable)

    @classmethod
    def GetFrame(cls, frame_type: str) -> Optional[Frame]:
        if (frame_type == 'GF'):
            return cls.globalFrame
        elif (frame_type == 'LF'):
            return cls.frameStack.top()
        elif (frame_type == 'TF'):
            return cls.tempFrame
        else:
            print("Chyba: Neznamy typ ramce!", file=sys.stderr)
            exit(32)
  
    @classmethod
    def SearchVariable(cls, var: str)-> Optional[Variable]:
        frame = var.split('@')[0]
        name = var.split('@')[1]
        if (frame == 'GF'):
            return cls.globalFrame.GetVariable(name)
        elif (frame == 'LF'):
            return cls.frameStack.top().GetVariable(name)
        elif (frame == 'TF'):
            if(cls.tempFrame is None):
                print("Chyba: Docasny ramec neni definovan!", file=sys.stderr)
                exit(55)
            return cls.tempFrame.GetVariable(name)
    
    @classmethod
    def UpdateVariable(cls, var: str, value: Any) -> None:
        frame = var.split('@')[0]
        name = var.split('@')[1]
        if (frame == 'GF'):
            cls.globalFrame.UpdateVariable(name, value)
        elif (frame == 'LF'):
            cls.frameStack.top().UpdateVariable(name, value)
        elif (frame == 'TF'):
            if(cls.tempFrame is None):
                print("Chyba: Docasny ramec neni definovan!", file=sys.stderr)
                exit(55)
            cls.tempFrame.UpdateVariable(name, value)
