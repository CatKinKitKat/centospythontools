#!/bin/env python3

import sys, os, shutil, subprocess


def main(arguments: list):
    if len(arguments) != 3:
        if arguments[0] == "help":
            print("nfs_util.py add|edit|stop|delete /path/to/nfs ip.ad.dr.ess")
            exit()
        else:
            print("The only accepted types are add|edit|stop|delete.")
            exit()

    if arguments[0] == "add":
        if not get_line(arguments[1]) != 0:
            print("That directory is already being shared.")
            exit()
        change_line(
            get_line_count(), build_line(arguments[1], arguments[2], get_options())
        )
        print("Added")
    elif arguments[0] == "edit":
        if get_line(arguments[1]) == 0:
            print("That directory is not being shared.")
            exit()
        change_line(
            get_line_count(), build_line(arguments[1], arguments[2], get_options())
        )
        print("Edited")
    elif arguments[0] == "stop":
        if get_line(arguments[1]) == 0:
            print("That directory is not being shared.")
            exit()
        change_line(
            get_line_count(),
            build_line(arguments[1], arguments[2], get_options(), enabled=False),
        )
        print("Stopped")
    elif arguments[0] == "delete":
        if get_line(arguments[1]) == 0:
            print("That directory is not being shared.")
            exit()
        change_line(get_line(arguments[1]), "")
        if (
            str(input("Removed\n Also Delete directory and contents? (yes/no): "))
            != "yes"
        ):
            print("Deleted")

    exit()


def build_line(path: str, destination: str, options: str, enabled: bool = True):
    char: chr = ""
    if not enabled:
        char = "#"

    return str(char + path + " " + destination + "(" + options + ")")


def change_line(index: int, newline: str):
    shutil.move("/etc/exports", "/etc/exports~")
    exports = open("/etc/exports~", "r")
    new = open("/etc/exports", "w")
    line = exports.readline()
    while line != "":
        if index == line.index:
            new.write(newline)
        else:
            new.write(line)
        line = exports.readline()
    exports.close()
    new.flush()
    new.close()
    os.remove("/etc/exports~")


def get_line(path: str):
    with open("/etc/exports", "r") as exports:
        line = exports.readline()
        while line != "":
            if path in line:
                return line.index
            line = exports.readline()
    return 0


def get_line_count():
    count: int = 0
    with open("/etc/exports", "r") as exports:
        line = exports.readline()
        while line != "":
            count += 1
            line = exports.readline()
    return count


def get_options():
    option: int = 0
    print(
        "Choose your NFS directory config:\n"
        + "1 - rw,nohide,sync\n"
        + "2 - ro,nohide,sync\n"
        + "3 - rw,hide,sync\n"
        + "4 - ro,hide,sync\n"
        + "5 - rw,nohide,async\n"
        + "6 - ro,nohide,async\n"
        + "7 - rw,hide,async\n"
        + "8 - ro,hide,async\n"
    )

    try:
        option = int(input("\nOption number: "))
    except Exception:
        option = 0

    condition: bool = (option >= 1) and (option <= 8)
    if not condition:
        while not condition:
            try:
                option = int(input("Option number: "))
            except Exception:
                option = 0

    return retrive_config(option)


def retrive_config(type: int):

    # Python 3 with version < 3.10 does NOT have switch/match
    if type == 1:
        return "rw,nohide,sync"
    elif type == 2:
        return "ro,nohide,sync"
    elif type == 3:
        return "rw,hide,sync"
    elif type == 4:
        return "ro,hide,sync"
    elif type == 5:
        return "rw,nohide,async"
    elif type == 6:
        return "ro,nohide,async"
    elif type == 7:
        return "rw,hide,async"
    elif type == 8:
        return "ro,hide,async"
    else:  # default
        return "rw,nohide,sync"


if __name__ == "__main__":
    main(sys.argv[1:])
