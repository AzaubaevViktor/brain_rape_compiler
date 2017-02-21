from br_lexer import Token


class AbstractBrType:
    type_name = None

    def __init__(self, raw: Token):
        self.token = raw
        self.value = self._parse()

    def _parse(self):
        raise NotImplemented()

    def __str__(self):
        return "Type<{}>:{}".format(self.type_name, self.value)


class IntBrType(AbstractBrType):
    type_name = "int"

    def _parse(self):
        return int(self.token.text)
