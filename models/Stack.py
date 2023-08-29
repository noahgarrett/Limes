from models.Object import Object
from models.Frame import Frame

class VMStack:
    def __init__(self) -> None:
        self.STACK_SIZE: int = 2048

        self.items: list[Object] = [None] * self.STACK_SIZE
        self.sp = 0

        self.last_popped_elem: Object = None
    
    def push(self, item: Object) -> str | None:
        if len(self.items) > self.STACK_SIZE:
            return "Stack Overflow."
        self.items[self.sp] = item
        self.sp += 1
        return None

    def pop(self) -> Object | None:
        if not self.is_empty():
            self.last_popped_elem = self.items[self.sp - 1]
            self.items[self.sp - 1] = None
            self.sp -= 1
            return self.last_popped_elem
        
        print("POPPING WHEN EMPTY")
        return None

    def is_empty(self) -> bool:
        return self.sp == -1
    
    def size(self) -> int:
        return self.sp + 1
    
    def top(self) -> Object:
        if self.sp == 0:
            return None
        return self.items[self.sp - 1]
    
class FrameStack:
    def __init__(self) -> None:
        self.MAX_FRAMES: int = 1024

        self.items: list[Frame] = [None] * self.MAX_FRAMES
        self.fp = 0

        self.last_popped_frame: Frame = None
    
    def push(self, item: Frame) -> str | None:
        self.items[self.fp] = item
        self.fp += 1
        return None

    def pop(self) -> Frame | None:
        if not self.is_empty():
            self.last_popped_frame = self.items[self.fp - 1]
            self.items[self.fp - 1] = None
            self.fp -= 1
            return self.last_popped_frame
        return None

    def is_empty(self) -> bool:
        return self.fp == -1
    
    def size(self) -> int:
        return self.fp + 1