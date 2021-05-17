#!/bin/env python3

import sys, os, subprocess


def main(arguments: list):
    if len(arguments) != 2:
        if arguments[0] == "help":
            print("backup_util.py regular|encrypted /path/to/backup")
            exit()
        else:
            print("The only accepted types are regular|encrypted.")
            exit()

    if arguments[0] == "regular":
        backup(arguments[1])
    elif arguments[0] == "encrypted":
        encrypted_backup(arguments[1])
    else:
        print("There can be only 2 arguments:\nThe type and path of backup.")
        exit()


def backup(path: str):

    if not os.path.exists(path):
        subprocess.run(["mkdir", "-p", path], check=True)

    backpath = "rsync -zavh /etc " + path
    subprocess.run(backpath.split(), check=True)

    print("RSync Backup at " + path)
    exit()


def encrypted_backup(path: str):

    if not os.path.exists("/crypt/rsynckey.key"):
        subprocess.run("mkdir -p /crypt".split(), check=True)
        subprocess.run(
            "openssl req -nodes -newkey rsa:1536 -x509 -keyout /crypt/rsynckey.key -out /crypt/rsynckey.crt".split(),
            check=True,
            text=True,
        )

    if not os.path.exists(path):
        subprocess.run(["mkdir", "-p", path], check=True)

    subprocess.run("mkdir -p /tmp/backup /tmp/encrypted".split(), check=True)
    subprocess.run("rsync -zrvh /etc /tmp/backup".split(), check=True)
    # --verbose --ne-nesting=2 --trim=2 --name-encrypt=/tmp/rsyncrypto-map --delete-keys --changed
    subprocess.run(
        "rsyncrypto --recurse /tmp/backup /tmp/encrypted/ /crypt/rsynckey.key /crypt/rsynckey.crt".split(),
        check=True,
        text=True,
    )
    subprocess.run("rm -rf /tmp/backup")
    backpath = "rsync -zrvh /tmp/encrypted " + path
    subprocess.run(backpath.split(), check=True)
    subprocess.run("rm -rf /tmp/encrypted".split(), check=True)

    print("Encrypted RSync Backup at " + path)
    exit()


if __name__ == "__main__":
    main(sys.argv[1:])
