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
import re 
from dataTypes import *
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
        print('Chybný formát argumentů!', file=sys.stderr)
        parser.print_help()
        exit(10)

    if (unknown_args):
        print("Neznáme argumenty: " + str(unknown_args), file=sys.stderr)
        parser.print_help()
        exit(10)
        
    if args.help and len([value for value in vars(args).values() if value]) > 1:
        print('Parametr --help nelze použít s jinými parametry!', file=sys.stderr)
        exit(10)

    if (not args.input and not args.source):
        print('Alespoň jeden z parametrů --input nebo --source musí být zadán!', file=sys.stderr)
        exit(10)

    if (args.help):
        parser.print_help()
        exit(0)
    return args


   
# Kontrola struktury XML
def checkXML(root: et.Element) -> bool:
    # Chybny korenovy element
    if(root.tag != 'program'):
        raise XMLInputError(f"Neočekávaný element: {root.tag}, očekáván '<program>!'")
    # Chybi language atribut
    if('language' not in root.attrib):
        raise XMLInputError("Chyba: Element 'program' neobsahuje atribut 'language'!")

    # Chybna hodnota language atributu
    if(root.attrib['language'].lower() != 'ippcode23'):
        raise XMLInputError("Chyba: Element 'program' obsahuje chybný atribut 'language'!")

    order = set()
    for element in root:
        # Jiny element nez instrukce
        if(element.tag != 'instruction'):
            raise XMLInputError(f"Neočekávaný element: {element.tag}, očekáván '<instruction>!'")
        else:
            if('order' not in element.attrib):
                raise XMLInputError("Chyba: Instrukce neobsahuje atribut 'order'!")
            if(not element.attrib['order'].isdigit()):
                raise XMLInputError("Chyba: Atribut 'order' není celé číslo!")
            if(int(element.attrib['order']) in order):
                raise XMLInputError("Chyba: Duplicitní pořadí instrukce!")
            if(int(element.attrib['order']) < 1):
                raise XMLInputError("Chyba: Nalezeno záporné nebo nulové pořadí instrukce!")
            order.add(int(element.attrib['order']))
    return True



if (__name__ == '__main__'):
    # Zpracovani argumentu prikazove radky
    args = getArguments()
    if(args.source):
        sourceXMLFile = args.source[0]
    else:
        sourceXMLFile = sys.stdin
    if(args.input):
        inputFile = open(args.input[0])
    else:
        inputFile = sys.stdin
    stack = Stack()
    # Nacteni obsahu XML souboru
    try:
        tree = et.parse(sourceXMLFile)
    except FileNotFoundError:
        print(f"Soubor {args.source[0]} nebyl nalezen!", file=sys.stderr)
        exit(11)
    except et.ParseError:
        print("XML soubor není dobře formovaný!", file=sys.stderr)
        exit(31)

    # Ziskani korene a kontrola struktury
    root = tree.getroot()
    try:
        checkXML(root)
    except XMLInputError as e:
        print(e, file=sys.stderr)
        exit(32)

    instructions = root.findall('instruction')
    # Serazeni instrukci podle poradi
    sorted_instructions = sorted(instructions, key=lambda e: int(e.attrib['order']))        

    # Vytvoreni objektu instrukci
    instructionObjects: List[Instruction] = []
    for element in sorted_instructions:
        try:
            instObj = Instruction.CreateInstruction(element)
            instructionObjects.append(instObj)
        except XMLInputError as e:
            print(e, file=sys.stderr)
            exit(32) 
  
    interpreter = Interpreter(instructionObjects, inputFile)
    interpreter.Interpret()
  

