# Autor: Vladimír Hucovič
# Login: xhucov00

from exceptions import *
from typing import Union

# Typ nil@nil v IPPCode23
class Nil:
    def __init__(self):
        pass

    def __str__(self):
        return ""

    def __add__(self, other):
        raise OperandTypeError("Chyba: Pokus o scitani s nil!")

    def __eq__(self, other):
        return IPPBool(isinstance(other, Nil))

    def __ne__(self, other):
        return IPPBool(not isinstance(other, Nil))
    
    def __gt__(self, other):
        raise OperandTypeError("Chyba: Pokus o porovnani s nil!")

    def __lt__(self, other):
        raise OperandTypeError("Chyba: Pokus o porovnani s nil!")

    def __bool__(self):
        raise OperandTypeError("Chyba: Pokus o konverzi nil na bool!")
    
    def __div__(self, other):
        raise OperandTypeError("Chyba: Pokus o deleni s nil!")

    def __mul__(self, other):
        raise OperandTypeError("Chyba: Pokus o nasobeni s nil!")
    
    def __sub__(self, other):
        raise OperandTypeError("Chyba: Pokus o odecitani s nil!")
    
    def __truediv__(self, other):
        raise OperandTypeError("Chyba: Pokus o deleni s nil!")

    def __floordiv__(self, other):
        raise OperandTypeError("Chyba: Pokus o deleni s nil!")

    def __or__(self, other):
        raise OperandTypeError("Chyba: Pokus o OR s nil!")

    def __and__(self, other):
        raise OperandTypeError("Chyba: Pokus o AND s nil!")

# Typ bool v IPPCode23
class IPPBool:
    def __init__(self, value: bool):
        self.value = value

    def __bool__(self):
        return self.value == True

    def __str__(self):
        return str(self.value).lower()

    def __add__(self, other):
        raise OperandTypeError(f"Chyba: Pokus o scitani hodnoty typu {self.__class__.__name__}")

    def __eq__(self, other):
        if(isinstance(other, bool)):
            return IPPBool(self.value is other)
        if(isinstance(other, IPPBool)):
            return IPPBool(self.value == other.value)
        if(isinstance(other, Nil)):
            return IPPBool(False)
        raise OperandTypeError(f"Chyba: Nelze porovnat typ IPPBool s typem {other.__class__.__name__}")

    def __ne__(self, other):
        return IPPBool(not self.__eq__(other))

    def __gt__(self, other):
        if(not isinstance (other, IPPBool)):
            raise OperandTypeError(f"Chyba: Nelze porovnat typ IPPBool s typem {other.__class__.__name__}")
        return IPPBool(self.value > other.value)

    def __lt__(self, other):
        if(not isinstance (other, IPPBool)):
            raise OperandTypeError(f"Chyba: Nelze porovnat typ IPPBool s typem {other.__class__.__name__}")
        return IPPBool(self.value < other.value)
    
    def __truediv__(self, other):
        raise OperandTypeError(f"Chyba: Nelze delit typ {self.__class__.__name__}")

    def __floordiv__(self, other):
        raise OperandTypeError(f"Chyba: Nelze delit typ {self.__class__.__name__}")

    def __mul__(self, other):
        raise OperandTypeError(f"Chyba: Nelze nasobit typ {self.__class__.__name__}")

    def __sub__(self, other):
        raise OperandTypeError(f"Chyba: Nelze odecitat typ {self.__class__.__name__}")

    def __and__(self, other):
        if(not isinstance (other, IPPBool)):
            raise OperandTypeError(f"Chyba: Nelze pouzit logicky AND na typ IPPBool a typ {other.__class__.__name__}")
        return IPPBool(self.value and other.value)

    def __or__(self, other):
        if(not isinstance (other, IPPBool)):
            raise OperandTypeError(f"Chyba: Nelze pouzit logicky OR na typ IPPBool a typ {other.__class__.__name__}")
        return IPPBool(self.value or other.value)

# Typ string v IPPCode23
class IPPString(str):
    # IPPString vytvořený přes tuto metodu nenahradí escape sekvence - používá se při načítání řetězce ze vstupu od uživatele
    @classmethod
    def CreateFromRead(cls, string: str):
        return super().__new__(cls, string)

    def __new__(cls, value: str):
        value = IPPString.replaceEscapeSequences(value)
        return super().__new__(cls, value)

    def Concat(self, other):
        if(not isinstance(other, IPPString)):
            raise OperandTypeError(f"Chyba: Nelze spojovat typ IPPString s typem {other.__class__.__name__}")
        return IPPString(super().__add__(other))

    def __getitem__(self, key):
        return super().__getitem__(key)

    def __len__(self):
        return super().__len__()
    
    def __str__(self):
        return self

    def __add__(self, other):
        raise OperandTypeError(f"Chyba: Nelze scitat typ IPPString s typem {other.__class__.__name__}") 
    
    def __and__(self, other):
        raise OperandTypeError(f"Chyba: Nelze pouzit logicky AND na typ IPPString a typ {other.__class__.__name__}")

    def __or__(self, other):
        raise OperandTypeError(f"Chyba: Nelze pouzit logicky OR na typ IPPString a typ {other.__class__.__name__}")

    def __ne__(self, other):
        return IPPBool(not self.__eq__(other))

    def __eq__(self, other):
        if(isinstance(other, Nil)):
            return IPPBool(False)
        if(not isinstance (other, IPPString)):
            raise OperandTypeError(f"Chyba: Nelze porovnat typ IPPString s typem {other.__class__.__name__}")
        return IPPBool(super().__eq__(other))

    def __gt__(self, other):
        if(not isinstance (other, IPPString)):
            raise OperandTypeError(f"Chyba: Nelze porovnat typ IPPString s typem {other.__class__.__name__}")
        return IPPBool(super().__gt__(other))

    def __lt__(self, other):
        if(not isinstance (other, IPPString)):
            raise OperandTypeError(f"Chyba: Nelze porovnat typ IPPString s typem {other.__class__.__name__}")
        return IPPBool(super().__lt__(other))

    def __truediv__(self, other):
        raise OperandTypeError(f"Chyba: Nelze delit typ {self.__class__.__name__}")

    def __floordiv__(self, other):
        raise OperandTypeError(f"Chyba: Nelze delit typ {self.__class__.__name__}")

    def __mul__(self, other):
        raise OperandTypeError(f"Chyba: Nelze nasobit typ {self.__class__.__name__}")

    def __sub__(self, other):
        raise OperandTypeError(f"Chyba: Nelze odecitat typ {self.__class__.__name__}")

    def __hash__(self):
        return super().__hash__()

    def __bool__(self):
        raise OperandTypeError(f"Chyba: Nelze konvertovat typ {self.__class__.__name__} na bool!")
   
    # Nahradí escape sekvence v IPPCode23 řetězci - metoda je volána při vytváření IPPStringu
    @staticmethod
    def replaceEscapeSequences(string: str):
        outputString = ""
        i = 0
        while i < len(string):
            if(string[i] == '\\'):
                try:
                    asciiCode = int(string[i+1:i+4])
                except ValueError:
                    raise XMLInputError(f"Chyba: Neplatna escape sekvence {string[i+1:i+4]}")
                outputString += chr(asciiCode)
                i += 3
            else:
                outputString += string[i]
            i += 1
        return outputString

# Typ float v IPPCode23
class IPPFloat(float):
    def __new__(cls, value: Union[float, str]):
        if(isinstance(value, str)):
            try:
                # hexadecimalni float zapis
                if(value.startswith("-0x") or value.startswith("0x") or value.startswith("+0x")):
                    return super().__new__(cls, float.fromhex(value)) 
                # dekadicky float zapis
                return super().__new__(cls, float(value))
            except ValueError:
                raise InvalidStringToFloatError(f"Chyba: Pokus o konverzi neplatneho retezce '{value}' na float!")
        else:
            return super().__new__(cls, float(value))

    def __str__(self):
        return float.hex(self)

    def __add__(self, other):
        if(not isinstance (other, IPPFloat)):
            raise OperandTypeError(f"Chyba: Pokus o scitani hodnoty typu IPPFloat s typem {other.__class__.__name__}")
        return IPPFloat(super().__add__(other))

    def __sub__(self, other):
        if(not isinstance (other, IPPFloat)):
            raise OperandTypeError(f"Chyba: Pokus o odecitani hodnoty typu IPPFloat s typem {other.__class__.__name__}")
        return IPPFloat(super().__sub__(other))

    def __mul__(self, other):
        if(not isinstance (other, IPPFloat)):
            raise OperandTypeError(f"Chyba: Pokus o nasobeni hodnoty IPPFloat typem {other.__class__.__name__}")
        return IPPFloat(super().__mul__(other))

    def __truediv__(self, other):
        if(not isinstance (other, IPPFloat)):
            raise OperandTypeError(f"Chyba: Pokus o deleni hodnoty IPPFloat typem {other.__class__.__name__}")
        try:
            return IPPFloat(super().__truediv__(other))
        except ZeroDivisionError:
            raise OperandValueError(f"Chyba: Deleni nulou!")    # ...

    def __floordiv__(self, other):
        raise OperandTypeError("Chyba: Nelze celociselne delit cislo typu float!")

    def __eq__(self, other):
        if(isinstance(other, Nil)):
            return IPPBool(False)
        if(not isinstance (other, IPPFloat)):
            raise OperandTypeError(f"Chyba: Nelze porovnat typ IPPFloat s typem {other.__class__.__name__}")
        return IPPBool(super().__eq__(other))

    def __ne__(self, other):
        if(not isinstance (other, IPPFloat)):
            raise OperandTypeError(f"Chyba: Nelze porovnat typ IPPFloat s typem {other.__class__.__name__}")
        return IPPBool(not self.__eq__(other))

    def __gt__(self, other):
        if(not isinstance (other, IPPFloat)):
            raise OperandTypeError(f"Chyba: Nelze porovnat typ IPPFloat s typem {other.__class__.__name__}")
        return IPPBool(super().__gt__(other))

    def __lt__(self, other):
        if(not isinstance (other, IPPFloat)):
            raise OperandTypeError(f"Chyba: Nelze porovnat typ IPPFloat s typem {other.__class__.__name__}")
        return IPPBool(super().__lt__(other))
    
    def __bool__(self):
        raise OperandTypeError("Chyba: Nelze konvertovat float na bool!")

    def __or__(self, other):
        raise OperandTypeError("Chyba: Nelze porovnavat typ float s typem bool!")

    def __and__(self, other):
        raise OperandTypeError("Chyba: Nelze porovnavat typ float s typem bool!")
# Typ int v IPPCode23    
class IPPInt(int):
    def __new__(cls, value: Union[int, str]):
        if(isinstance(value, str)):
            try:
                # hexadecimalni int zapis
                if(value.startswith("-0x") or value.startswith("0x") or value.startswith("+0x")):
                    return super().__new__(cls, value, 16)
                # oktalovy int zapis
                if(value.startswith("-0") or value.startswith("0") or value.startswith("+0")):
                    return super().__new__(cls, value, 8)
                # dekadicky int zapis
                return super().__new__(cls, value)
            except ValueError:
                raise InvalidStringToIntError(f"Chyba: Pokus o konverzi neplatneho retezce '{value}' na int!")
        else:
            return super().__new__(cls, value)


    def __add__(self, other):
        if(not isinstance (other, IPPInt)):
            raise OperandTypeError(f"Chyba: Pokus o scitani hodnoty typu IPPInt s typem {other.__class__.__name__}")
        return IPPInt(super().__add__(other))

    def __sub__(self, other):
        if(not isinstance (other, IPPInt)):
            raise OperandTypeError(f"Chyba: Pokus o odecitani hodnoty typu IPPInt s typem {other.__class__.__name__}")
        return IPPInt(super().__sub__(other)) 

    def __mul__(self, other):
        if(not isinstance (other, IPPInt)):
            raise OperandTypeError(f"Chyba: Pokus o nasobeni hodnoty IPPInt typem {other.__class__.__name__}")
        return IPPInt(super().__mul__(other)) 

    def __truediv__(self, other):
        raise OperandTypeError(f"Chyba: Pokus o deleni hodnoty IPPInt typem {other.__class__.__name__}")

    def __floordiv__(self, other):
        if(not isinstance (other, IPPInt)):
            raise OperandTypeError(f"Chyba: Pokus o celociselne deleni hodnoty IPPInt typem {other.__class__.__name__}")
        try:
            return IPPInt(super().__floordiv__(other))
        except ZeroDivisionError:
            raise OperandValueError(f"Chyba: Deleni nulou!")

    def __str__(self):
        return super().__str__()


    def __ne__(self, other):
        return IPPBool(not self.__eq__(other))
    
    def __eq__(self, other):
        if(isinstance(other, Nil)):
            return IPPBool(False)
        if(not isinstance (other, IPPInt)):
            raise OperandTypeError(f"Chyba: Nelze porovnat typ IPPInt s typem {other.__class__.__name__}")
        return IPPBool(super().__eq__(other))

    def __not__(self, other):    
        if(not isinstance (other, IPPInt)):
            raise OperandTypeError(f"Chyba: Nelze porovnat typ IPPInt s typem {other.__class__.__name__}")
        return IPPBool(not self.__eq__(other))

    def __gt__(self, other):
        if(not isinstance (other, IPPInt)):
            raise OperandTypeError(f"Chyba: Nelze porovnat typ IPPInt s typem {other.__class__.__name__}")
        return IPPBool(super().__gt__(other)) 

    def __lt__(self, other):
        if(not isinstance (other, IPPInt)):
            raise OperandTypeError(f"Chyba: Nelze porovnat typ IPPInt s typem {other.__class__.__name__}")
        return IPPBool(super().__lt__(other))

    def __bool__(self):
        raise OperandTypeError("Chyba: Nelze konvertovat IPPInt na bool!")

    def __or__(self, other):
        raise OperandTypeError(f"Chyba: Nelze provest logicky OR typu IPPInt s typem {other.__class__.__name__}")

    def __and__(self, other):
        raise OperandTypeError(f"Chyba: Nelze provest logicky AND typu IPPInt s typem {other.__class__.__name__}")
