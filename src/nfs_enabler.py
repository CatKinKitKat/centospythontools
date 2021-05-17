#!/bin/env python3

import sys, subprocess


def main(arguments: list):
    if len(arguments) != 1:
        print("nfs_enabler.py install|uninstal|start|stop|enable|disable|restart")
        exit()

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

    exit()


def sysctl(action: str):
    subprocess.run(["systemctl", action, "nfs"], check=True)


def yum(action: str):
    subprocess.run(["yum", action, "nfs-util", "-y"], check=True)


if __name__ == "__main__":
    main(sys.argv[1:])
