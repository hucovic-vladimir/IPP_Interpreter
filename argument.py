from framemanager import FrameManager
import xml.etree.ElementTree as et
import sys
# Tato třída reprezentuje argumenty instrukce
# atribut type určuje typ argumentu, tedy "var" u proměnných a 
# "int", "float", "bool", "string", "nil" u konstant, nebo "type" u typu, "label" u navesti
# atribut value obsahuje buď jméno proměnné nebo hodnotu konstanty
class Argument:
    def __init__(self, type, value):
        self.value = value
        self.type = type

    def __str__(self):
        return f"{self.value}" 
    
    def GetArgValue(self):
        if(self.type == 'var'):
            var = FrameManager.SearchVariable(self.value)
            if(var is None):
                print(f"Chyba: Promenna {self.value} neni definovana!", file=sys.stderr)
                exit(54)
            return var.value
        else:
            return self.value

    def GetArgDataType(self):
        if(self.type == 'var'):
            var = FrameManager.SearchVariable(self.value)
            if(var is None):
                print(f"Chyba: Promenna {self.value} neni definovana!", file=sys.stderr)
                exit(54)
            return var.type
        else:
            return self.type

    @classmethod
    def CreateArgument(cls, arg: et.Element):
        type = arg.attrib["type"]
        value = arg.text
        if(value is None):
            print("Chyba: Chybejici hodnota v argumentu instrukce!" , file=sys.stderr)
            exit(32)
        # pokud jde o promennou, vytvori se argument s hodnotou jmena promenne
        if(type == 'var'):
            return Argument(type, value)
        # pokud jde o konstantu, hodnota se prevede z retezce na odpovidajici typ
        else:
            if(type == "nil"):
                return Argument(type, "nil")
            if(type == "bool"):
                return Argument(type, value == "true")
            if(type == "int"):
                try:
                    # hexadecimalni cele cislo
                    if(value.startswith("-0x") or value.startswith("+0x") or value.startswith("0x")):
                        return Argument(type, int(value, 16))
                    # oktalove cele cislo
                    elif(value.startswith("-0") or value.startswith("+0") or value.startswith("0") and len(value) > 1):
                        return Argument(type, int(value[1:], 8))
                    # desitkove cele cislo
                    return Argument(type, int(value))
                except ValueError:
                    print(f"Chyba: Neplatna celociselna hodnota '{value}' v argumentu!", file=sys.stderr)
                    exit(32)
            if(type == "float"):
                try:
                    if(value.startswith("-0x") or value.startswith("0x") or value.startswith("+0x")):
                        return Argument(type, float.fromhex(value))
                    else:
                        return Argument(type, float(value)) 
                except ValueError:
                    print(f"Chyba: Neplatna float hodnota v argumentu! {value}!", file=sys.stderr)
                    exit(32)

            elif(type == "string" or type == "type" or type == "label" or type == "nil"):
                return Argument(type, value)
            else:
                print(f"Error: Invalid argument type {type}!", file=sys.stderr)
                exit(32)

