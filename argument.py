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
            return Argument(VarName(arg.text.strip()))
        elif (type == "int" or type == "float" or type == "bool" or type == "string" or type == "nil"):
            return ArgumentFactory.CreateConstantArgument(arg)
        elif (type == "type" or type == "label"):
            if(arg.text is None):
                return None
            return Argument(IPPString(arg.text.strip()))
        else:
            return None

    @classmethod
    def CreateConstantArgument(cls, arg: et.Element) -> Optional[Argument]:
        type = arg.attrib["type"]
        if(type == "string"):
            if(arg.text is None):
                return Argument(IPPString(""))
            return Argument(IPPString(arg.text.strip()))
        if(arg.text is None):
            return None
        text = arg.text.strip()
        if(type == "nil"):
            return Argument(Nil()) 
        if(type == "bool"):
            return Argument(IPPBool(text == "true"))
        if(type == "int"):
            try:
                return Argument(IPPInt(int(text)))
            except ValueError:
                print(f"Chyba: Neplatna celociselna hodnota '{arg.text}' v argumentu!", file=sys.stderr)
                exit(32)
        if(type == "float"):
            try:
                return Argument(IPPFloat(float(text)))
            except ValueError:
                print(f"Chyba: Neplatne desetinne cislo '{arg.text}' v argumentu!", file=sys.stderr)
                exit(32)
        if (type == "type"):
            return Argument(IPPString(text))
        if (type == "label"):
            return Argument(IPPString(text))
        return None

