from typing import Optional, Union

class Variable:
    def __init__(self, name: str, type: Optional[str], value: Union[int, bool, str, None]) -> None:
        self.name = name
        self.type = type
        self.value = value

    def __str__(self) -> str:
        if(self.value == None):
            return self.name + " : " + "None"
        return self.name + " : " + str(self.value) + " : " + str(self.type)

    def __repr__(self) -> str:
        return self.__str__()

    def SetValue(self, value: Union[int, str, bool, None], type: Optional[str]):
        if(type == "nil"):
            self.value = None
            self.type = "nil"
        elif(type == "bool"):
            if(value == "true"):
                self.value = True
            elif(value == "false"):
                self.value = False
            else:
                print("Error: Invalid bool value!")
                exit(58)
            self.type = "bool"
        elif(type == "int"):
            try:
                if(value is None):
                    raise ValueError
                self.value = int(value)
                self.type = "int"
            except ValueError:
                print("Error: Invalid int value!")
                exit(58)
        
        elif(type == "string"):
            self.value = value
            self.type = "string"
