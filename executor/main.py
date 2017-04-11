from typing import List
from typing import Tuple

import sys

from bytecode import ByteCode as B


class Memory:
    CHUNK = 64
    DEFAULT = 0

    class MemoryIterator:
        def __init__(self, memory: 'Memory'):
            self.cur = 0
            self.memory = memory

        def __next__(self):
            val = self.memory[self.cur]
            self.cur += 1
            return val

    def __init__(self):
        self.cur_len = 0
        self.data = []

    def _last_not_null_index(self):
        for v in range(1, len(self.data) + 1):
            if self.data[-v]:
                return len(self.data) - v
        return 0


    def __iter__(self):
        return self.MemoryIterator(self)

    def __getitem__(self, item: int) -> int:
        if item >= self.cur_len:
            return self.DEFAULT
        return self.data[item]

    def __setitem__(self, key: int, value: int):
        while key >= self.cur_len:
            self.cur_len += self.CHUNK
            self.data += [self.DEFAULT] * self.CHUNK
        self.data[key] = value % 256

    def __eq__(self, other: dict):
        for k, v in other.items():
            assert self[k] == v
        return True

    def get_items(self):
        d = {}
        for k in range(self.cur_len):
            v = self[k]
            if v != 0:
                d[k] = v
        return d

    def __repr__(self):
        return repr(self.data)

    def __str__(self):
        s = "Memory:\n"
        indexes = []
        values = []

        for i, v in enumerate(self.data[:self._last_not_null_index() + 1]):
            i = str(i)
            v = str(v)
            ml = max(len(i), len(v))
            indexes.append(i.ljust(ml))
            values.append(v.ljust(ml))

        s += "V: " + ", ".join(values) + "\n"
        s += "#: " + "  ".join(indexes)
        return s




class Interpreter:
    def __init__(self, bytecode: List[B],
                 output=sys.stdout,
                 inp=sys.stdin
                 ):
        self.memory = Memory()
        self.bytecode = bytecode
        self._pre_calc()
        self.output = output
        self.input = inp
        self.MP = 0
        self.PC = 0

    def _pre_calc(self):
        stack = []  # type: List[Tuple[int, B]]
        bytecode = []
        for i, b in zip(
                range(len(self.bytecode)),
                self.bytecode
        ):
            if B.CYCLE_IN == b.op:
                stack.append((i, b))
            elif B.CYCLE_OUT == b.op:
                ip, bp = stack.pop()
                bp.arg = i
                b.arg = ip

            bytecode.append(b)
        self.bytecode = bytecode

    def step(self):
        b = self.bytecode[self.PC]

        if b.PLUS == b.op:
            self.memory[self.MP] += b.arg
        elif b.MOVE == b.op:
            self.MP += b.arg
        elif b.PRINT == b.op:
            print(chr(self.memory[self.MP]), end='', file=self.output)
        elif b.READ == b.op:
            cache = self.input.read(1)
            self.memory[self.MP] = ord(cache[0])
        elif b.CYCLE_IN == b.op:
            if 0 == self.memory[self.MP]:
                self.PC = b.arg
        elif b.CYCLE_OUT == b.op:
            if 0 != self.memory[self.MP]:
                self.PC = b.arg

        self.PC += 1

        if self.PC >= len(self.bytecode):
            raise EOFError()
