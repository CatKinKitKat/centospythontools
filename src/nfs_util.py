#!/bin/env python3

import sys, os, shutil, subprocess


def main(arguments: list):
    if len(arguments) != 3:
        if arguments[0] == "help":
            print("nfs_util.py add|edit|stop|delete /path/to/nfs ip.ad.dr.ess")
            sys.exit()
        else:
            print("The only accepted types are add|edit|stop|delete.")
            sys.exit()

    line_n: int = get_line(arguments[1], arguments[2])
    if arguments[0] == "add":
        if line_n >= 0:
            print("That directory is already being shared.")
            sys.exit()
        create_dir(arguments[1])
        change_ownership(arguments[1])
        change_line(
            get_line_count(), build_line(arguments[1], arguments[2], set_options())
        )
        print("Added")
    elif arguments[0] == "edit":
        if line_n < 0:
            print("That directory is not being shared.")
            sys.exit()
        change_line(
            line_n,
            build_line(arguments[1], arguments[2], set_options()),
        )
        print("Edited")
    elif arguments[0] == "stop":
        if line_n < 0:
            print("That directory is not being shared.")
            sys.exit()
        change_line(
            line_n,
            build_line(arguments[1], arguments[2], set_options(), enabled=False),
        )

        print("Stopped")
    elif arguments[0] == "delete":
        if line_n < 0:
            print("That directory is not being shared.")
            sys.exit()
        remove_line(line_n)
        if (
            str(input("Removed\n Also Delete directory and contents? (yes/no): "))
            != "yes"
        ):
            remove_dir(arguments[1])
            print("Deleted")

    sys.exit()


def build_line(path: str, destination: str, options: str, enabled: bool = True):
    char: chr = ""
    if not enabled:
        char = "#"

    return str(char + path + " " + destination + "(" + options + ")\n")


def fix_file():
    shutil.move("/etc/exports", "/etc/exports~")
    with open("/etc/exports~", "r") as exports:
        data = exports.read().replace("\r\n", "\n")
        new = open("/etc/exports", "a")
        new.write(data)
        new.flush()
        new.truncate()
        new.close()
    os.remove("/etc/exports~")


def get_line(path: str, ip: str):
    fix_file()
    i: int = 0
    with open("/etc/exports", "r") as exports:
        data: list = exports.read().split("\n")
        for line in data:
            if line.__contains__(path) and line.__contains__(ip):
                return i
            i += 1
    return -1


def get_line_count():
    fix_file()
    count: int = -1
    with open("/etc/exports", "r") as exports:
        data: list = exports.read().split("\n")
        for line in data:
            count += 1
    return count


def change_line(index: int, newline: str):
    fix_file()
    shutil.move("/etc/exports", "/etc/exports~")
    i: int = 0
    with open("/etc/exports~", "r") as exports:
        data: list = exports.read().split("\n")
        new = open("/etc/exports", "a")
        for line in data:
            print(str(i) + " " + str(index))
            if index == i:
                new.write(newline + "\n")
            else:
                new.write(line + "\n")
            i += 1
        new.write("")
        new.flush()
        new.truncate()
        new.close()
    os.remove("/etc/exports~")


def remove_line(index: int):
    fix_file()
    shutil.move("/etc/exports", "/etc/exports~")
    i: int = 0
    with open("/etc/exports~", "r") as exports:
        data: list = exports.read().split("\n")
        new = open("/etc/exports", "a")
        for line in data:
            if index == i:
                i += 1
            else:
                new.write(line + "\n")
            i += 1
        new.write("")
        new.flush()
        new.truncate()
        new.close()
    os.remove("/etc/exports~")


def set_options():
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


def change_ownership(path: str):
    try:
        subprocess.run(["chown", "nobody:nobody", path], check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)
        sys.exit()


def create_dir(path: str):
    if not os.path.isdir(path):
        os.makedirs(path, mode=0o770, exist_ok=True)


def remove_dir(path: str):
    shutil.rmtree(path)


if __name__ == "__main__":
    main(sys.argv[1:])
