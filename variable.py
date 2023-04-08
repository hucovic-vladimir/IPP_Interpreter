from typing import Optional, Union

class Variable:
    def __init__(self, name: str, type: Optional[str], value: Union[int, bool, str, None]) -> None:
        self.name = name
        self.type = type
        self.value = value

    def __str__(self) -> str:
        if(self.value == None or self.type == "nil"):
            return self.name + " : " + "None" + " : " + str(self.type)
        return self.name + " : " + str(self.value) + " : " + str(self.type)

    def __repr__(self) -> str:
        return self.__str__()

    def SetValue(self, value: Union[int, str, bool, float], type: str) -> None:
        if(type == "nil"):
            self.value = "nil"
            self.type = "nil"
            return
        self.value = value
        self.type = type
    
    def IsInitialized(self) -> bool:
        return self.value != None and self.type != None
