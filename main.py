from br_compiler import BrCompiler


if __name__ == "__main__":
    compiler = BrCompiler('test_files/builtin/add.br')
    print("==== LINES: ====")
    for expr in compiler.lines:
        print(expr)

    print(compiler.block)

    print(
        "\n".join(
            compiler.block.debug_print()
        )
    )

    bytecode = compiler.compile()
    print()
    print("==== BYTECODE: ====")
    for code, func, expr in bytecode:
        for act in code:
            print(act, end=" ")
        print()
        print(func)
        print(expr)
        print("------")

    print()
    print("==== BRAINFUCK ====")
    for code, *_ in bytecode:
        for act in code:
            print(act.compile(), end="")
        print()
    print()

