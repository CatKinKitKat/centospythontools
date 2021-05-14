#!/bin/env python3

import sys
from os import path


def main(arguments: list):
    if len(arguments) != 2:
        if arguments[0] == "help":
            print("backup_util.py regular|encrypted /path/to/backup")
            exit()
        else:
            print("The only accepted types are regular|encrypted.")
            exit()

    if arguments[0] == "regular":
        backup(arguments[1])
    elif arguments[0] == "encrypted":
        encrypted_backup(arguments[1])
    else:
        print("There can be only 2 arguments:\nThe type and path of backup.")
        exit()


def backup(path: str):
    print(path)
    exit()


def encrypted_backup(path: str):

    print("encrypted " + path)
    exit()


if __name__ == "__main__":
    main(sys.argv[1:])
