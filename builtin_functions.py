
from typing import List, Dict

from br_parser import Function, Argument, BrFunctionLifeTime, BrFunctionType
from br_types import AbstractBrType, IntBrType
from bytecode import ByteCode as B


class _BuiltinAddFunction(Function):
    def compile(self, variables: Dict[str, AbstractBrType]):
        addr = variables['addr'].value
        value = variables['value'].value
        return [
            B(B.MOVE, addr),
            B(B.PLUS, value),
            B(B.MOVE, -addr)
        ]

builtin_add_function = _BuiltinAddFunction(
    'add',
    [
        Argument('addr', IntBrType),
        Argument('value', IntBrType)
    ],
    BrFunctionType.NO_BLOCK,
    BrFunctionLifeTime.GLOBAL,
    [],
    builtin=True
)
