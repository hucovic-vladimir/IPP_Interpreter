from framemanager import FrameManager
# Represents instruction arguments: type can be var or const
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
                print(f"Error: {self.value} not defined!")
                exit(54)
            return var.value
        else:
            return self.value

