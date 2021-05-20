#!/bin/env python3

import sys, os, subprocess, shutil


def main(arguments: list):
    if len(arguments) != 2:
        if arguments[0] == "help":
            print("backup_util.py regular|encrypted /path/to/backup")
            sys.exit()
        else:
            print("The only accepted types are regular|encrypted.")
            sys.exit()

    if arguments[0] == "regular":
        backup(arguments[1])
    elif arguments[0] == "encrypted":
        encrypted_backup(arguments[1])
    else:
        print("There can be only 2 arguments:\nThe type and path of backup.")
        sys.exit()


def backup(path: str):

    if not os.path.isdir(path):
        os.makedirs(path, mode=0o755, exist_ok=True)

    backpath = "rsync -zavh /etc " + path
    try:
        subprocess.run(backpath.split(), check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)
        sys.exit()

    print("RSync Backup at " + path)
    sys.exit()


def encrypted_backup(path: str):

    if not os.path.isdir("/crypt/rsynckey.key"):
        os.makedirs("/crypt", mode=0o755, exist_ok=True)
        try:
            subprocess.run(
                "openssl req -nodes -newkey rsa:1536 -x509 -keyout /crypt/rsynckey.key -out /crypt/rsynckey.crt".split(),
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(e.output)
            sys.exit()

    if not os.path.isdir(path):
        os.makedirs(path, mode=0o755, exist_ok=True)

    if not os.path.isdir("/tmp/backup"):
        os.makedirs("/tmp/backup", mode=0o755, exist_ok=True)
    if not os.path.isdir("/tmp/encrypted"):
        os.makedirs("/tmp/encrypted", mode=0o755, exist_ok=True)
    try:
        subprocess.run("rsync -zrvh /etc /tmp/backup".split(), check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)
        sys.exit()
    # --verbose --ne-nesting=2 --trim=2 --name-encrypt=/tmp/rsyncrypto-map --delete-keys --changed
    try:
        subprocess.run(
            "rsyncrypto --recurse /tmp/backup /tmp/encrypted/ /crypt/rsynckey.key /crypt/rsynckey.crt".split(),
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(e.output)
        sys.exit()
    shutil.rmtree("/tmp/backup")
    backpath = "rsync -zrvh /tmp/encrypted " + path
    try:
        subprocess.run(backpath.split(), check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)
        sys.exit()
    shutil.rmtree("/tmp/encrypted")

    print("Encrypted RSync Backup at " + path)
    sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])
