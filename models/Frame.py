from models.Object import ClosureObject
from models.Code import Instructions


class Frame:
    def __init__(self, cl: ClosureObject, base_pointer: int, ip: int = None) -> None:
        self.cl = cl
        self.ip = -1 if ip is None else ip
        self.base_pointer = base_pointer

    def instructions(self) -> Instructions:
        return self.cl.fn.instructions
