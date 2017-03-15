from br_exceptions.base import Base as _Base


class Base(_Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __str__(self):
        s = repr(self)
        s += "\n"
        s += self.context.error_info()
        return s


class NoBlockFunctionError(Base):
    def __repr__(self):
        return "В неблоковую функцию нельзя передать блок"


class BlockFunctionError(Base):
    def __repr__(self):
        return "В блоковую функицю обязательно нужно что-то передать"
