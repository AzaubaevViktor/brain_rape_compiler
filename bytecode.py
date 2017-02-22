class ByteCode:
    PLUS = 0
    MOVE = 1
    PRINT = 2
    READ = 3
    CYCLE_IN = 4
    CYCLE_OUT = 5

    _associate = {
        "+": (PLUS, 1),
        "-": (PLUS, -1),
        ">": (MOVE, 1),
        "<": (MOVE, -1),
        ".": (PRINT, 1),
        ",": (READ, 1),
        "[": (CYCLE_IN, 1),
        "]": (CYCLE_OUT, 1)
    }

    def __init__(self, op: int or str, arg=None):
        assert type(op) is int or type(op) is str
        self.op = op
        self.arg = arg
        if isinstance(self.op, str):
            assoc = self._associate[self.op]
            self.op = assoc[0]
            if self.arg:
                self.arg *= assoc[1]

    def compile(self) -> str:
        if self.PLUS == self.op:
            if self.arg >= 0:
                return "+" * self.arg
            else:
                return "-" * (-self.arg)
        elif self.MOVE == self.op:
            if self.arg >= 0:
                return ">" * self.arg
            else:
                return "<" * -self.arg
        elif self.PRINT == self.op:
            return "."
        elif self.READ == self.op:
            return ","
        elif self.CYCLE_IN == self.op:
            return "["
        elif self.CYCLE_OUT == self.op:
            return "]"
        else:
            return ""

    def __str__(self):
        if self.PLUS == self.op:
            if self.arg >= 0:
                return "BC(+, {})".format(self.arg)
            else:
                return "BC(-, {})".format(-self.arg)
        elif self.MOVE == self.op:
            if self.arg >= 0:
                return "BC(>, {})".format(self.arg)
            else:
                return "BC(<, {})".format(-self.arg)
        elif self.PRINT == self.op:
            return "BC(.)"
        elif self.READ == self.op:
            return "BC(,)"
        elif self.CYCLE_IN == self.op:
            return "BC([)"
        elif self.CYCLE_OUT == self.op:
            return "BC(])"
        else:
            return "BC(UNKNOWN)"
