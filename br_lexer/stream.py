import abc
from typing import Iterator

from .expressions import Line


class Stream(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def lines(self) -> Iterator[Line]:
        pass


class FileStream(Stream):
    def __init__(self, name: str):
        self.name = name
        self._open()

    def _open(self):
        self._f = open(self.name, "rt")

    def lines(self) -> Iterator[Line]:
        number = 0
        prev_line = None  # type: Line
        for text in self._f.readlines():
            number += 1
            line = Line(self, number, text)
            if line:
                if prev_line:
                    line.prev_line = prev_line
                    prev_line.next_line = line
                yield line
                prev_line = line
            else:
                del line

        self._close()

    def _close(self):
        self._f.close()
