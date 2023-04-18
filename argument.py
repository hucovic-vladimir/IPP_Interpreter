# autor: Vladimír Hucovič
# login: xhucov00

import xml.etree.ElementTree as et
from typing import Union, Optional
from dataTypes import *

# Tato třída reprezentuje jméno proměnné
class VarName:
    def __init__(self, name: str) -> None:
        self.name:str  = name

    def __str__(self) -> str:
        return f"{self.name}"

# Tato třída reprezentuje argumenty instrukce
# atribut type určuje, zda jde o proměnnou nebo konstantu 
class Argument:
    def __init__(self, value: Union[IPPFloat, IPPInt, IPPString, IPPBool, Nil, VarName]) -> None:
        self.value = value

    def __str__(self) -> str:
        return f"{self.value}"

class ArgumentFactory:
    # Pokusí se vytvořit objekt Argument ze vstupního XML elementu. Pokud najde chybu, je vyhozena výjimka
    @staticmethod
    def Create(arg: et.Element) -> Optional[Argument]:
        type = arg.attrib.get("type")
        if(type is None):
            raise XMLInputError("Chyba: Chybejici typ argumentu!")
        if(type == "var"):
            if(arg.text is None):
                raise XMLInputError("Chyba: Chybejici hodnota argumentu!")
            return Argument(VarName(arg.text.strip()))
        elif (type == "int" or type == "float" or type == "bool" or type == "string" or type == "nil"):
            return ArgumentFactory.CreateConstantArgument(arg)
        # IPPString je použit pro uchování argumentů label a type
        elif (type == "type" or type == "label"):
            if(arg.text is None):
                raise XMLInputError(f"Chyba: chybejici hodnota argumentu!")
            return Argument(IPPString(arg.text.strip()))
        else:
            raise XMLInputError(f"Chyba: Neplatny typ argumentu! {type}")

    
    # Pokusí se vytvořit objekt Argument ze vstupního XML elementu s konstantní hodnotou příslušného typu
    # Pokud najde chybu, je vyhozena výjimka
    @staticmethod
    def CreateConstantArgument(arg: et.Element) -> Optional[Argument]:
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
                return Argument(IPPInt(text))
            except InvalidStringToIntError:
                raise XMLInputError(f"Pokus: o prevod neplatneho retezce na int! {text}")
        if(type == "float"):
            try:
                return Argument(IPPFloat(text))
            except InvalidStringToFloatError:
                raise XMLInputError(f"Pokus: o prevod neplatneho retezce na float! {text}")
        if (type == "type"):
            return Argument(IPPString(text))
        if (type == "label"):
            return Argument(IPPString(text))
        return None

