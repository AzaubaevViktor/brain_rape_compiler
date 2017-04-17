from typing import List

from bytecode import ByteCode as B
from parser import Function, Argument, IntType, FunctionTypes, LifeTime


class Plus(Function):
    name = "__plus"
    arguments = [
        Argument("value", IntType)
    ]

    function_type = FunctionTypes.NOBLOCK
    lifetime = LifeTime.GLOBAL
    builtin = True

    @property
    def code(self) -> List[B]:
        value = self.variables['value'].value

        return [
            B("+", value)
        ]


class Minus(Plus):
    name = "__minus"

    @property
    def code(self) -> List[B]:
        value = self.variables['value'].value

        return [
            B("-", value)
        ]


class MoveAbs(Function):
    name = "__move_abs"
    arguments = [
        Argument("value", IntType)
    ]

    function_type = FunctionTypes.NOBLOCK
    lifetime = LifeTime.GLOBAL
    builtin = True

    @property
    def code(self) -> List[B]:
        value = self.variables['value'].value

        return [
            B(">", value)
        ]


class MoveAbsL(MoveAbs):
    name = "__move_abs_l"

    @property
    def code(self) -> List[B]:
        value = self.variables['value'].value

        return [
            B("<", value)
        ]