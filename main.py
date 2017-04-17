import argparse
import os

from br_lexer import FileStream, Lexer
from utils import fill_str

parser = argparse.ArgumentParser(description="BrainRape compiler")
parser.add_argument("filename", help='File to compile')

ns = parser.parse_args()

print("Working directory: `{}`".format(os.getcwd()))
filename = ns.filename
print("File to compile: `{}`".format(filename))

stream = FileStream(ns.filename)

block, lines = Lexer.get_block(stream)

print(fill_str("STRUCTURE", "=", 50))
print(block.debug_print())

