from typing import Any, List

class Stack:
    def __init__(self) -> None:
        self.stack: List[Any] = []

    def __str__(self) -> str:
        stack_content = ""
        for i in range(len(self.stack), 0, -1):
            stack_content += str(self.stack[i - 1]) + " "
        return stack_content

    def __repr__(self) -> str:
        return self.__str__()

    def push(self, element) -> None:
        self.stack.append(element)

    def pop(self) -> Any:
        return self.stack.pop()

    def top(self) -> Any:
        return self.stack[-1]

    def empty(self) -> bool:
        return len(self.stack) == 0

