from typing import Iterator

from br_lexer import Line


class FileTest:
    commands = ["desc", "exception"]

    def __init__(self, lines: Iterator[str]):
        self.lines = lines

        self.exception = None  # type: Exception
        self._desc = []

        self._get_tests()

    def _get_tests(self):
        number = 0
        for line in self.lines:
            number += 1

            if "#~" == line[:2]:
                cmd, *args = [s.strip() for s in line[2:].split(" ") if s.strip()]
                assert cmd in self.commands, \
                    "Неизвестная команда: `{}`. Доступные команды: ({})\n" \
                    "{}: {}".format(
                        cmd,
                        ", ".join(self.commands),
                        number, line
                    )
                getattr(self, "_cmd_{}".format(cmd))(line, number, args)

    def _cmd_desc(self, line, number, args):
        self._desc.append(" ".join(args))

    @property
    def desc(self) -> str:
        return "\n".join(self._desc)

    def _cmd_exception(self, line, number, args):
        assert len(args) == 1, \
            "Должен быть только один Exception\n" \
            "{}: {}".format(number, line)
        self.exception = args[0]
