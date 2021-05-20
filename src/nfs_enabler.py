#!/bin/env python3

import sys, subprocess


def main(arguments: list):
    if len(arguments) != 1:
        print("nfs_enabler.py install|uninstal|start|stop|enable|disable|restart")
        sys.exit()

    if arguments[0] == "help":
        print("nfs_enabler.py install|uninstal|start|stop|enable|disable|restart")
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

    sys.exit()


def sysctl(action: str):
    try:
        subprocess.run(["systemctl", action, "nfs"], check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)
        sys.exit()


def yum(action: str):
    try:
        subprocess.run(["yum", action, "nfs-util", "-y"], check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)
        sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])
