# Chyba pri konverzi retezce na floating point cislo
class InvalidStringToFloatError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

# Chyba pri konverzi retezce na cele cislo
class InvalidStringToIntError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

# Chyba 32 - Chyba ve vstupnim XML
class XMLInputError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

# Chyba 52 - Chybejici navesti
class UndefinedLabelError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

# Chyba 52 - Redefinice promenne
class VariableRedefenitionError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

# Chyba 53 - Spatne typy operandu
class OperandTypeError(Exception):
       def __init__(self, message):
            self.message = message
            super().__init__(self.message)

# Chyba 54 - Pristup k neexistujici promenne
class MissingVariableError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

# Chyba 55 - Pristup k neexistujicimu ramci
class MissingFrameError(Exception):
       def __init__(self, message):
            self.message = message
            super().__init__(self.message)

# Chyba 56 - Chybejici hodnota v promenne nebo zasobniku
class MissingValueError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

# Chyba 57 - Spatna hodnota operandu
class OperandValueError(Exception):
       def __init__(self, message):
            self.message = message
            super().__init__(self.message)

# Chyba 58 - Chybna prace s retezcem
class StringOperationError(Exception):
       def __init__(self, message):
            self.message = message
            super().__init__(self.message)

# Chyba 99 - Interni chyba interpretu
class InterpreterInternalError(Exception):
       def __init__(self, message):
            self.message = message
            super().__init__(self.message)

# Vyvolana pri provedeni instrukce EXIT
class ExitInstruction(Exception):
    def __init__(self, code):
        self.code = code

