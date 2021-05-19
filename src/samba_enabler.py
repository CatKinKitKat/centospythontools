#!/bin/env python3

import sys, subprocess


def main(arguments: list):
    if len(arguments) != 1:
        print("samba_enabler.py install|uninstal|start|stop|enable|disable|restart")
        exit()

    if arguments[0] == "help":
        print("samba_enabler.py install|uninstal|start|stop|enable|disable|restart")
    elif arguments[0] == "install":
        yum("install")
    elif arguments[0] == "uninstall":
        sysctl("stop")
        sysctl("disable")
        yum("remove")
    elif arguments[0] == "start":
        sysctl("start")
    elif arguments[0] == "stop":
        sysctl("stop")
    elif arguments[0] == "enable":
        sysctl("start")
        sysctl("enable")
    elif arguments[0] == "disable":
        sysctl("stop")
        sysctl("disable")
    elif arguments[0] == "restart":
        sysctl("restart")

    exit()


def sysctl(action: str):
    try:
        subprocess.run(["systemctl", action, "smb"], check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)

    try:
        subprocess.run(["systemctl", action, "nmb"], check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)


def yum(action: str):
    try:
        subprocess.run(["yum", action, "samba", "-y"], check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)


if __name__ == "__main__":
    main(sys.argv[1:])
