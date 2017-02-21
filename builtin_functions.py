
from typing import List, Dict

from br_parser import BrFunction, Argument, BrFunctionLifeTime, BrFunctionType
from br_types import AbstractBrType, IntBrType
from bytecode import ByteCode as B


class _Add(BrFunction):
    def compile(self, variables: Dict[str, AbstractBrType]):
        addr = variables['addr'].value
        value = variables['value'].value
        return [
            B(B.MOVE, addr),
            B(B.PLUS, value),
            B(B.MOVE, -addr)
        ]

add = _Add(
    '_add',
    [
        Argument('addr', IntBrType),
        Argument('value', IntBrType)
    ],
    BrFunctionType.NO_BLOCK,
    BrFunctionLifeTime.GLOBAL,
    [],
    builtin=True
)


class _Mov(BrFunction):
    def compile(self, variables: Dict[str, AbstractBrType]):
        to_addr = variables['to_addr'].value
        from_addr = variables['from_addr'].value
        return [
            B(B.MOVE, from_addr - 0),  # Move to from_addr
            B(B.CYCLE_IN, 0),  # While *from_addr not null, do
            B(B.PLUS, -1),  # *from_addr -= 1
            B(B.MOVE, to_addr - from_addr),  # go to to_addr
            B(B.PLUS, 1),  # *to_addr += 1
            B(B.MOVE, from_addr - to_addr),  # go to from_addr
            B(B.CYCLE_OUT, 0),  # if *from_addr == null then end
            B(B.MOVE, 0 - from_addr)  # move to 0
        ]

mov = _Mov(
    '_mov',
    [
        Argument('to_addr', IntBrType),
        Argument('from_addr', IntBrType)
    ],
    BrFunctionType.NO_BLOCK,
    BrFunctionLifeTime.GLOBAL,
    [],
    builtin=True
)


class _Mov2(BrFunction):
    def compile(self, variables: Dict[str, AbstractBrType]):
        to1_addr = variables['to1_addr'].value
        to2_addr = variables['to2_addr'].value
        from_addr = variables['from_addr'].value
        return [
            B(B.MOVE, from_addr - 0),  # Move to from_addr
            B(B.CYCLE_IN),  # While *from_addr not null, do
            B(B.PLUS, -1),  # *from_addr -= 1
            B(B.MOVE, to1_addr - from_addr),  # go to to1_addr
            B(B.PLUS, 1),  # *to1_addr += 1
            B(B.MOVE, to2_addr - to1_addr),  # goto to2_addr
            B(B.PLUS, 1),  # *to2_addr += 1
            B(B.MOVE, from_addr - to2_addr),  # go to from_addr
            B(B.CYCLE_OUT),  # if *from_addr == null then end
            B(B.MOVE, 0 - from_addr)  # move to 0
        ]

mov2 = _Mov2(
    '_mov2',
    [
        Argument('to1_addr', IntBrType),
        Argument('to2_addr', IntBrType),
        Argument('from_addr', IntBrType)
    ],
    BrFunctionType.NO_BLOCK,
    BrFunctionLifeTime.GLOBAL,
    [],
    builtin=True
)


class _Null(BrFunction):
    def compile(self, variables: Dict[str, AbstractBrType]):
        addr = variables['addr'].value
        return [
            B(B.MOVE, addr - 0),   # goto addr
            B(B.CYCLE_IN),   # [
            B(B.PLUS, -1),     # -
            B(B.CYCLE_OUT),  # ]
            B(B.MOVE, 0 - addr)   # goto 0
        ]

null = _Null(
    '_null',
    [
        Argument('addr', IntBrType)
    ],
    BrFunctionType.NO_BLOCK,
    BrFunctionLifeTime.GLOBAL,
    [],
    builtin=True
)


class _Print(BrFunction):
    def compile(self, variables: Dict[str, AbstractBrType]):
        addr = variables['addr'].value
        return [
            B(B.MOVE, addr - 0),    # goto addr
            B(B.PRINT),           # print from addr
            B(B.MOVE, 0 - addr)     # goto 0
        ]

_print = _Print(
    '_print',
    [
        Argument('addr', IntBrType)
    ],
    BrFunctionType.NO_BLOCK,
    BrFunctionLifeTime.GLOBAL,
    [],
    builtin=True
)


class _Read(BrFunction):
    def compile(self, variables: Dict[str, AbstractBrType]):
        addr = variables['addr'].value
        return [
            B(B.MOVE, addr - 0),
            B(B.READ),
            B(B.MOVE, 0 - addr)
        ]


_read = _Read(
    '_read',
    [
        Argument('addr', IntBrType)
    ],
    BrFunctionType.NO_BLOCK,
    BrFunctionLifeTime.GLOBAL,
    [],
    builtin=True
)


builtin_functions = [
    add,
    mov,
    mov2,
    null,
    _print,
    _read
]
