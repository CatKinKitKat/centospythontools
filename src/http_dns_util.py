#!/bin/env python3

import sys, os, shutil, subprocess


def main(arguments: list):
    print(arguments)


def symlink_website(name: str):
    config: str = "/etc/httpd/sites-available/" + name
    link: str = "/etc/httpd/conf.d/" + name

    subprocess.run(["ln", "-s", config, link], check=True, text=True)


if __name__ == "__main__":
    main(sys.argv[1:])
