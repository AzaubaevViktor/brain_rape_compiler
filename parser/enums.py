from enum import Enum


class FunctionTypes(Enum):
    NOBLOCK = 0
    BLOCK = 1


class LifeTime(Enum):
    GLOBAL = 0
    LOCAL = 1
