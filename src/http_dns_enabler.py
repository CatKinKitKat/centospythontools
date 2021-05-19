#!/bin/env python3

import os, sys, subprocess


def main(arguments: list):
    if len(arguments) != 1:
        print("http_dns_enabler.py install|uninstal|start|stop|enable|disable|restart")
        exit()

    if arguments[0] == "help":
        print("http_dns_enabler.py install|uninstal|start|stop|enable|disable|restart")
    elif arguments[0] == "install":
        yum("install")
        create_vhosts_directory()
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


def create_vhosts_directory():
    os.makedirs("/etc/httpd/sites-available", mode=0o755, exist_ok=True)


def sysctl(action: str):
    try:
        subprocess.run(["systemctl", action, "named"], check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)

    try:
        subprocess.run(["systemctl", action, "httpd"], check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)


def yum(action: str):
    try:
        subprocess.run(["yum", action, "bind", "bind-utils", "httpd", "-y"], check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)


if __name__ == "__main__":
    main(sys.argv[1:])
