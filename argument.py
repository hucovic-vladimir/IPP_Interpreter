import xml.etree.ElementTree as et
import sys
from typing import Union, Optional, List
from dataTypes import *

# Tato třída reprezentuje jméno proměnné
class VarName:
    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return f"{self.name}"

# Tato třída reprezentuje argumenty instrukce
# atribut type určuje, zda jde o proměnnou nebo konstantu 
class Argument:
    def __init__(self, value: Union[IPPFloat, IPPInt, IPPString, IPPBool, Nil, VarName]):
        self.value = value

    def __str__(self) -> str:
        return f"{self.value}"

class ArgumentFactory:
    @classmethod
    def Create(cls, arg: et.Element) -> Optional[Argument]:
        type = arg.attrib["type"]
        if(type == "var"):
            if(arg.text is None):
                return None
            return Argument(VarName(arg.text))
        elif (type == "int" or type == "float" or type == "bool" or type == "string" or type == "nil"):
            return ArgumentFactory.CreateConstantArgument(arg)
        elif (type == "type" or type == "label"):
            if(arg.text is None):
                return None
            return Argument(IPPString(arg.text))
        else:
            return None

    @classmethod
    def CreateConstantArgument(cls, arg: et.Element) -> Optional[Argument]:
        type = arg.attrib["type"]
        if(type == "string"):
            if(arg.text is None):
                return Argument(IPPString(""))
            return Argument(IPPString(arg.text))
        if(arg.text is None):
            return None
        if(type == "nil"):
            return Argument(Nil()) 
        if(type == "bool"):
            return Argument(IPPBool(arg.text == "true"))
        if(type == "int"):
            try:
                # hexadecimalni cele cislo
                if(arg.text.startswith("-0x") or arg.text.startswith("+0x") or arg.text.startswith("0x")):
                    return Argument(IPPInt(int(arg.text, 16)))
                # oktalove cele cislo
                elif(arg.text.startswith("-0") or arg.text.startswith("+0") or arg.text.startswith("0") and len(arg.text) > 1):
                    return Argument(IPPInt(int(arg.text[1:], 8)))
                # desitkove cele cislo
                return Argument(IPPInt(int(arg.text)))
            except ValueError:
                print(f"Chyba: Neplatna celociselna hodnota '{arg.text}' v argumentu!", file=sys.stderr)
                exit(32)
        if(type == "float"):
            if(arg.text is None):
                print("Chyba: Chybejici hodnota v argumentu instrukce!" , file=sys.stderr)
                exit(32)
            try:
                # hexadecimalni floating point cislo
                if(arg.text.startswith("-0x") or arg.text.startswith("0x") or arg.text.startswith("+0x")
                   or arg.text.endswith("p-") or arg.text.endswith("p+") or arg.text.endswith("p")):
                    return Argument(IPPFloat(float.fromhex(arg.text)))
                # dekadicke floating point cislo
                return Argument(IPPFloat(float(arg.text)))
            except ValueError:
                print(f"Chyba: Neplatne desetinne cislo '{arg.text}' v argumentu!", file=sys.stderr)
                exit(32)
        if (type == "type"):
            return Argument(IPPString(arg.text))
        if (type == "label"):
            return Argument(IPPString(arg.text))
        return None

