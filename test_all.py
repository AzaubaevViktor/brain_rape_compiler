import glob
import io

import pytest

from br_compiler import FileCompiler, Lexer
from executor import Interpreter
from utils import get_tests


def file_execute(file_name, *args):
    print(file_name)
    memory_tests, memory_dict_test, inp, out = args

    block = None
    with open(file_name, 'rt') as f:
        l = Lexer(f.readlines())

        block = l.block

    compiler = FileCompiler(file_name, block)

    compiler.compile()

    bytecode = compiler.context.full_bytecode()

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
    mt_count = 0
    for test in memory_tests:
        for tv, mv in zip(test, interpreter.memory):
            if -1 != tv:
                assert tv == mv
                mt_count += 1

    print("Memory Tested {} cells, OK".format(mt_count))

    assert interpreter.memory == memory_dict_test

    print("Memory Dict Tested {} cells, OK".format(len(memory_dict_test)))

    if out:
        po_v = program_out.getvalue()
        o_v = out.getvalue()
        assert po_v == o_v
        print("Output test OK, len: {}".format(len(o_v)))

    print(" ====== ")


def test_files():
    file_names = sorted(glob.glob("./test_files/*/*.br", recursive=True))

    for file_name in file_names:
        args = get_tests(file_name)
        file_execute(file_name, *args)
