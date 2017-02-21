class ByteCode:
    PLUS = 0
    MOVE = 1
    PRINT = 2
    READ = 3
    CYCLE_IN = 4
    CYCLE_OUT = 5

    def __init__(self, op: int, arg=None):
        self.op = op
        self.arg = arg

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
