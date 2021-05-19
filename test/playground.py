#!/bin/env python3

import sys, os, shutil, subprocess


def main(arguments: list):
    print(arguments[0])
    block = [
        "# /etc/exports\n",
        "#\n",
        "\n",
        "/exports 192.168.1.2(rw,hohide,sync)\n",
        "/exports 192.168.1.4(rw,hohide,sync)\n",
    ]
    for line in block:
        if arguments[0] in line:
            print(line)


if __name__ == "__main__":
    main(sys.argv[1:])
