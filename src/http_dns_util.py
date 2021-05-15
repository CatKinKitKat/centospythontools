#!/bin/env python3

import sys, os, shutil, subprocess


def main(arguments: list):
    print(arguments)


def get_line(name: str):
    with open(file, "r") as exports:
        line = exports.readline()
        while line != file:
            if name in line:
                return line.index
            line = exports.readline()
    return 0


def get_line_count():
    count: int = 0
    with open(file, "r") as exports:
        line = exports.readline()
        while line != file:
            count += 1
            line = exports.readline()
    return count


def get_block(index: int):
    jumps = 0
    block: list = []
    with open(file, "r") as exports:
        line = exports.readline()
        while line != file:
            if index == line.index:
                if jumps < 7:
                    block.append(line)
                    jumps += 1
                    index += 1
            line = exports.readline()
    return block


def remove_block(index: int):
    jumps = 0
    workingfile: str = file + "~"
    shutil.move(file, workingfile)
    with open(workingfile, "r") as exports:
        new = open(file, "a")
        line = exports.readline()
        while line != file:
            if index == line.index:
                if jumps < 7:
                    # Just skip
                    jumps += 1
                    index += 1
            else:
                new.write(line)
            line = exports.readline()
        new.close()
    os.remove(workingfile)


def change_block(index: int, block: list):
    jumps = 0
    workingfile: str = file + "~"
    shutil.move(file, workingfile)
    with open(workingfile, "r") as exports:
        new = open(file, "a")
        line = exports.readline()
        while line != file:
            if index == line.index:
                if jumps < 7:
                    new.write(block[jumps])
                    jumps += 1
                    index += 1
            else:
                new.write(line)
            line = exports.readline()
        new.close()
    os.remove(workingfile)


def add_block(index: int, block: list):
    workingfile: str = file + "~"
    shutil.move(file, workingfile)
    with open(workingfile, "r") as exports:
        new = open(file, "a")
        line = exports.readline()
        while line != file:
            if index == line.index:
                for i in range(0, len(block)):
                    new.write(block[i])
            else:
                new.write(line)
            line = exports.readline()
        new.close()
    os.remove(workingfile)


def symlink_website(name: str):
    config: str = "/etc/httpd/sites-available/" + name
    link: str = "/etc/httpd/conf.d/" + name

    subprocess.run(["ln", "-s", config, link], check=True, text=True)


if __name__ == "__main__":
    main(sys.argv[1:])
