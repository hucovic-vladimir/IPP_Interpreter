from frame import *
from stack import *
from variable import *
from typing import List, Any, Optional
import argparse as ap

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
        cls.frameStack.push(cls.tempFrame)
        cls.tempFrame = None

    @classmethod
    def CreateTempFrame(cls) -> None:
        cls.tempFrame = Frame("TF")

    @classmethod
    def AddToFrame(cls, frame_type: str, variable: Variable) -> None:
        if (frame_type == 'GF'):
            cls.globalFrame.variables.append(variable)
        elif (frame_type == 'LF'):
            try:
                cls.frameStack.top().variables.append(variable)
            except IndexError:
                print("Error: LF not defined!")
                exit(55)
        elif (frame_type == 'TF'):
            if(cls.tempFrame is None):
                print("Error: TF not defined!")
                exit(55)
            cls.tempFrame.variables.append(variable)

    @classmethod
    def GetFrame(cls, frame_type: str) -> Optional[Frame]:
        if (frame_type == 'GF'):
            return cls.globalFrame
        elif (frame_type == 'LF'):
            return cls.frameStack.top()
        elif (frame_type == 'TF'):
            return cls.tempFrame
        else:
            print("Error: Unknown frame type!")
            exit(55)
  
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
                print("Error: TF not defined!")
                exit(55)
            return cls.tempFrame.GetVariable(name)

def GetArguments():
    parser = ap.ArgumentParser(add_help=False)
    parser.add_argument('--help', action='store_true',
                        help='Vypíše tuto nápovědu')
    parser.add_argument('--input', nargs=1, type=str,
                        help='Cesta k souboru se vstupy pro program (Výchozí je standardní vstup)')
    parser.add_argument('--source', nargs=1, type=str,
                        help='Cesta ke vstupnímu souboru s XML reprezentací programu (Výchozí je standardní vstup)')

    try:
        args, unknown_args = parser.parse_known_args()
    except ap.ArgumentError:
        exit(10)

    if (unknown_args):
        print("Neznáme argumenty: " + str(unknown_args))
        parser.print_help()
        exit(10)

    if args.help and len([value for value in vars(args).values() if value]) > 1:
        print('Parametr --help nelze použít s jinými parametry!')
        exit(10)

    if (not args.input and not args.source):
        print('Alespoň jeden z parametrů --input nebo --source musí být zadán!')
        exit(10)

    if (args.help):
        parser.print_help()
        exit(0)

    return args




