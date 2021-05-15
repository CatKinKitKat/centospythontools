#!/bin/env python3

import sys, subprocess


def main(arguments: list):
    if len(arguments) != 1:
        print("http_dns_enabler.py install|uninstal|start|stop|enable|disable|restart")
        exit()

    if arguments[0] == "help":
        print("http_dns_enabler.py install|uninstal|start|stop|enable|disable|restart")
    elif arguments[0] == "install":
        yum("install")
        pass
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
    subprocess.run(["systemctl", action, "named"], check=True, text=True)
    subprocess.run(["systemctl", action, "httpd"], check=True, text=True)


def yum(action: str):
    subprocess.run(["yum", action, "samba", "-y"], check=True, text=True)


if __name__ == "__main__":
    main(sys.argv[1:])