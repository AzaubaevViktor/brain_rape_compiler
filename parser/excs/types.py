from .base import ParserException


class IntTypeError(ParserException):
    fmt_msg = "Ожидается число, передано {self.place.text}"


class AddressTypeError(ParserException):
    fmt_msg = "Ожидается адрес, в виде `:<int>`, передано `{self.place.text}`"
