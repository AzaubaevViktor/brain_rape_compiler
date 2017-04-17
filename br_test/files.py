import os


def get_all_files(path="."):
    for name, catalogs, files in os.walk(path):
         for file in files:
             if "br" == file.split(".")[-1]:
                 yield name + "/" + file
