import sys
import xml.etree.ElementTree as et
import argparse as ap
from typing import List, Optional, Any
from interpreter import *
from frame import *
from variable import *
from stack import *
from framemanager import *
from instruction import *
def getArguments() -> ap.Namespace:
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

if (__name__ == '__main__'):
    # parse command line arguments
    interpreter = Interpreter()
    args = getArguments()

    # Load the XML file
    try:
        tree = et.parse(args.source[0])
    except FileNotFoundError:
        print("Soubor nebyl nalezen!")
        exit(11)

    # Get the root element
    root = tree.getroot()

    # Sort the child elements by the "order" attribute
    instructionObjects = []
    sorted_elements = sorted(root, key=lambda e: int(e.attrib['order']))
    stack = Stack()
    for element in sorted_elements:
        if(element.tag == 'instruction'):
            instObj = Instruction.CreateInstruction(element)
            instructionObjects.append(instObj)
        

    # Interpret the program
    for instructionObj in instructionObjects:
        interpreter.execute_instruction(instructionObj)
        
