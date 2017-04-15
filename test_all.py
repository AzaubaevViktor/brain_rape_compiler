import glob
import io

import pytest

from br_compiler import FileCompiler, Lexer
from executor import Interpreter
from test_utils import BrTests, get_tests


def file_execute(file_name, test: BrTests):
    print(file_name)

    interpreter = None
    block = None

    try:
        with open(file_name, 'rt') as f:
            l = Lexer(file_name, f.readlines())

            block = l.block

        compiler = FileCompiler(file_name, block)

        compiler.compile()

        bytecode = compiler.context.full_bytecode()

        program_out = io.StringIO()
        interpreter = Interpreter(bytecode,
                                  output=program_out,
                                  inp=test.inp)

        try:
            while True:
                interpreter.step()
        except EOFError:
            pass

    except Exception as e:
        assert e.__class__.__name__ == test.exc_name
        assert str(e) is not None
        print("Exception '{test.exc_name}' catched".format(test=test))
        print(" ====== ")
        return

    # tests
    mt_count = 0
    for value in test.memory:
        for tv, mv in zip(value, interpreter.memory):
            if -1 != tv:
                assert tv == mv
                mt_count += 1

    print("Memory Tested {} cells, OK".format(mt_count))

    assert interpreter.memory == test.memory_dict

    print("Memory Dict Tested {} cells, OK".format(len(test.memory_dict)))

    if test.out:
        po_v = program_out.getvalue()
        o_v = test.out.getvalue()
        assert po_v == o_v
        print("Output test OK, len: {}".format(len(o_v)))

    print(" ====== ")


def test_files():
    file_names = sorted(glob.glob("./test/*/*.br", recursive=True))

    for file_name in file_names:
        test = get_tests(file_name)
        file_execute(file_name, test)
