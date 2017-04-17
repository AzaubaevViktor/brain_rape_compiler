from excs import BrException


class LevelError(BrException):
    fmt_msg = "Количество пробелов должно быть кратно 4-м"


class BlockLevelError(BrException):
    fmt_msg = "Переход более чем на два уровня вверх"
