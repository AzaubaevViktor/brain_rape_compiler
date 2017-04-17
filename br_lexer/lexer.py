from typing import List, Iterator, Tuple

from .expressions import Line, Block
from .stream import Stream
import br_lexer.excs as lex_exc


class Lexer:
    @classmethod
    def get_block(cls, stream: Stream) -> Tuple[Block, List[Line]]:
        lines = []

        for line in stream.lines():
            lines.append(line)

        lines.append(Line(stream, -1, "end_line"))

        first_block = cur_block = Block(Line(stream, 0, "__main"))
        cur_iter = iter(lines)  # type: Iterator[Line]
        next_iter = iter(lines)  # type: Iterator[Line]
        next(next_iter)

        for (cur_line, next_line) in zip(cur_iter, next_iter):
            cl = cur_line.level
            nl = next_line.level

            if cl == nl:
                # eq level
                cur_block.push(cur_line)
            elif cl + 1 == nl:
                # level up
                child_block = Block(cur_line)
                cur_block.push(child_block)
                cur_block = child_block
            elif cl > nl:
                # level down
                cur_block.push(cur_line)
                for i in range(cl - nl):
                    cur_block = cur_block.parent
            elif cl + 1 < nl:
                # level up more than 2
                raise lex_exc.BlockLevelError(cur_line,
                                              under_start=cl * 4,
                                              under_len= (nl - cl) * 4)

        return first_block, lines

