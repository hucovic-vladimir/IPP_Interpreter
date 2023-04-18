# Autor: Vladimír Hucovič
# Login: xhucov00

import sys
import xml.etree.ElementTree as et
import argparse as ap
from typing import List
from interpreter import *
from instruction import *


# FIXME doplnit jmeno, login, odstranit zbytecne importy, upravit Interpreter

# argparse akce pro zpracování argumentů z rozšíření STATI
class GetStatsArgs(ap.Action):
    def __call__(self, parser, namespace, values, optionString):
        if(optionString=="--stats"):
            if(hasattr(namespace, "statsFile")):
                print("Nalezeno více výskytů argumentu '--stats'!", file=sys.stderr)
                exit(10)
            setattr(namespace, "statsFile", values[0])
            setattr(namespace, "stats", [])
        else:
            if(not hasattr(namespace, "statsFile")):
                print(f"Nalezen argument pro statistiku {optionString} bez přechozího '--stats'!", file=sys.stderr)
                exit(10)
            # Vytvoří v jmenném prostoru seznam pro požadované statistiky 
            if(not hasattr(namespace, "stats")):
                setattr(namespace, "stats", [])
            if(optionString=="--print"):
                namespace.stats.append("--print")
                namespace.stats.append(values[0])
            else:
                namespace.stats.append(optionString)

# Získá argumenty příkazové řádky
def getArguments() -> ap.Namespace:
    help = """
Skript načte XML reprezentaci programu v jazyce IPPCode23 a tento program s využitím vstupu dle parametrů
příkazové řádky interpretuje a generuje výstup.
použití: interpret.py [--input <file>] [--source <file>] [--help] [--print <string>] [--stats <file>] [--hot] [--insts] [--vars] [--frequent] [--eol]

Volitelné argumenty:
  --input <file>    Cesta k souboru se vstupy pro program (Výchozí je standardní vstup)
  --source <file>   Cesta ke vstupnímu souboru s XML reprezentací programu (Výchozí je standardní vstup)
  --help            Vypíše tuto nápovědu
  --stats <file>    Jmeno souboru, do ktereho budou zapsany statistiky
  --print <string>  Vypíše do souboru se statistikami řetězec <string>
  --hot             Vypíše do souboru se statistikami nejčastěji používané instrukce
  --insts           Vypíše do souboru se statistikami počet provedených instrukcí
  --vars            Vypíše do souboru nejvyšší počet definovaných proměnných ve všech rámcích
  --frequent        Vypíše do souboru se statistikami nejčastěji se vyskytující operační kód v programu
  --eol             Vypíše do souboru se statistikami odřádkování
    """

    parser = ap.ArgumentParser(add_help=False, allow_abbrev=False)
    optionalArgs = parser.add_argument_group("Volitelné argumenty")
    optionalArgs.add_argument("--input", nargs=1, type=str, metavar="<file>",
                  help="Cesta k souboru se vstupy pro program (Výchozí je standardní vstup)")
    optionalArgs.add_argument("--source", nargs=1, type=str, metavar="<file>", 
                  help="Cesta ke vstupnímu souboru s XML reprezentací programu (Výchozí je standardní vstup)")
    optionalArgs.add_argument("--help", action="store_true",
                        help="Vypíše tuto nápovědu")

    #STATI
    optionalArgs.add_argument("--print", metavar="<string>", action=GetStatsArgs, nargs=1, help="Vypíše do souboru se statistikami řetězec <string>")
    optionalArgs.add_argument("--stats", metavar="<file>", action=GetStatsArgs, nargs=1, help="Jmeno souboru, do ktereho budou zapsany statistiky")
    optionalArgs.add_argument("--hot", action=GetStatsArgs, nargs=0, help="Vypíše do souboru se statistikami nejčastěji používané instrukce")
    optionalArgs.add_argument("--insts", action=GetStatsArgs, nargs=0, help="Vypíše do souboru se statistikami počet provedených instrukcí")
    optionalArgs.add_argument("--vars", action=GetStatsArgs, nargs=0, help="Vypíše do souboru nejvyšší počet definovaných proměnných ve všech rámcích")
    optionalArgs.add_argument("--frequent", action=GetStatsArgs, nargs=0, help="Vypíše do souboru se statistikami nejčastěji používané instrukce")
    optionalArgs.add_argument("--eol", action=GetStatsArgs, nargs=0, help="Vypíše do souboru se statistikami odřádkování")
    
    # Zpracování argumentů
    try:
        args = parser.parse_args()
    except ap.ArgumentError:
        print("Chybný formát argumentů!", file=sys.stderr)
        exit(10)
    except SystemExit as e:
        exit(10)
      
    # Kontrola jestli není --help zadán s jinými argumenty
    if args.help and len([value for value in vars(args).values() if value]) > 1:
        print("Parametr --help nelze použít s jinými parametry!", file=sys.stderr)
        exit(10)

    if (not args.input and not args.source and not args.help):
        print("Alespoň jeden z parametrů --input nebo --source musí být zadán!", file=sys.stderr)
        exit(10)

    if (args.help):
        print(help)
        exit(0)
    return args


   
# Kontrola struktury XML
def checkXML(root: et.Element) -> bool:
    # Chybný kořenový element
    if(root.tag != "program"):
        raise XMLInputError(f"Neočekávaný element: {root.tag}, očekáván '<program>!'")
    # Chybi language atribut
    if("language" not in root.attrib):
        raise XMLInputError("Chyba: Element 'program' neobsahuje atribut 'language'!")

    # Chybná hodnota language atributu
    if(root.attrib["language"].lower() != "ippcode23"):
        raise XMLInputError("Chyba: Element 'program' obsahuje chybný atribut 'language'!")

    order = set()
    for element in root:
        # Jiny element nez instrukce
        if(element.tag != "instruction"):
            raise XMLInputError(f"Neočekávaný element: {element.tag}, očekáván '<instruction>!'")
        else:
            # Chybný atribut order
            if("order" not in element.attrib):
                raise XMLInputError("Chyba: Instrukce neobsahuje atribut 'order'!")
            if(not element.attrib["order"].strip().isdigit()):
                raise XMLInputError("Chyba: Atribut 'order' není celé číslo!")
            if(int(element.attrib["order"]) in order):
                raise XMLInputError("Chyba: Duplicitní pořadí instrukce!")
            if(int(element.attrib["order"]) < 1):
                raise XMLInputError("Chyba: Nalezeno záporné nebo nulové pořadí instrukce!")
            order.add(int(element.attrib["order"]))
        if("opcode" not in element.attrib):
            raise XMLInputError("Chyba: Instrukce neobsahuje atribut 'opcode'!")
    return True



if __name__ == "__main__":
    # Zpracování argumentů příkazové řádky
    args = getArguments()
    if(args.source):
        sourceXMLFile = args.source[0]
    else:
        sourceXMLFile = sys.stdin
    if(args.input):
        try:
            inputFile = open(args.input[0])
        except FileNotFoundError:
            print(f"Soubor {args.input[0]} nebyl nalezen!", file=sys.stderr)
            exit(11)
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

    instructions = root.findall("instruction")
    # Seřezení instrukcí podle pořadí
    sortedInstructions = sorted(instructions, key=lambda e: int(e.attrib["order"]))        

    # Vytvoření objektu interpretu
    if(hasattr(args, "statsFile")):
        interpreter = StatisticsCollectingInterpreter(inputFile)
    else:
        interpreter = Interpreter(inputFile)

    # Vytvorení objektů instrukcí
    instructionObjects: List[Instruction] = []
    for element in sortedInstructions:
        try:
            instObj = InstructionFactory.CreateInstruction(element, interpreter.interpreterData)
            instructionObjects.append(instObj)
        except XMLInputError as e:
            print(f"{e.message}", file=sys.stderr)
            exit(32) 


    interpreter.AddInstructions(instructionObjects)
    # Interpretace
    result = interpreter.Interpret()
    if(result == False):
        if(interpreter.errorMessage is not None):
            print(interpreter.errorMessage, file=sys.stderr)
            exit(interpreter.errorCode)

    # Případné výpisy statistik 
    if(hasattr(args, "statsFile")):
        try:
            file = open(args.statsFile, "w")
        except PermissionError:
            print(f"Chyba při zápisu do souboru {args.statsFile}! - Nedostatečná práva", file=sys.stderr)
            exit(11)
        if(hasattr(args, "stats")):
            if(isinstance(interpreter, StatisticsCollectingInterpreter)):
                for i in range (len(args.stats)):
                    if(args.stats[i] == "--insts"):
                        file.write(str(interpreter.GetTotalInstExecuted()) + "\n")
                    elif(args.stats[i] == "--vars"):
                        file.write(str(interpreter.GetMaxInitVars()) + "\n")
                    elif(args.stats[i] == "--frequent"):
                        file.write(str(interpreter.GetMaxOpcodes()) + "\n")
                    elif(args.stats[i] == "--hot"):
                        file.write(str(interpreter.GetHotInstructionOrder()) + "\n")
                    elif(args.stats[i] == "--eol"):
                        file.write("\n")
                    elif (args.stats[i] == "--print"):
                        file.write(args.stats[i+1])
                        i += 1
                    else:
                        pass

    if(interpreter.errorCode is not None):
        exit(interpreter.errorCode)
    else:
        exit(0)
