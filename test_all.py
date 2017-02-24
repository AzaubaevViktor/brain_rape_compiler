import glob
import io

import pytest

from br_compiler import BrCompiler
from executor import Interpreter
from utils import get_tests


def file_execute(file_name, *args):
    print(file_name)
    memory_tests, memory_dict_test, inp, out = args
    compiler = BrCompiler(file_name)
    bytecode_raw = compiler.compile()
    bytecode = []
    for bytecode_line in bytecode_raw:
        bytecode += bytecode_line[0]
    program_out = io.StringIO()
    interpreter = Interpreter(bytecode,
                              output=program_out,
                              inp=inp)

    try:
        while True:
            interpreter.step()
    except EOFError:
        pass

    # tests
    for test in memory_tests:
        for tv, mv in zip(test, interpreter.memory):
            assert -1 != tv and tv == mv

    assert interpreter.memory == memory_dict_test

    if out:
        assert program_out.getvalue() == out.getvalue()


def test_files():
    file_names = glob.glob("./test_files/*.br")

    for file_name in file_names:
        args = get_tests(file_name)
        file_execute(file_name, *args)
