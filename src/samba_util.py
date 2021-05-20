#!/bin/env python3

import sys, os, shutil, subprocess


def main(arguments: list):
    if len(arguments) != 1:
        print("samba_enabler.py sysprep|config")
        sys.exit()

    main_menu(arguments[0])


def main_menu(arg: str):
    if arg == "sysprep":
        sysprep()
    elif arg == "config":
        config()
    else:
        print("samba_enabler.py sysprep|config")

    sys.exit()


def sysprep():
    answer: str = str(input("Is this the first configuration (yes/no): "))
    while answer != "yes":
        answer = str(input("Is this the first configuration (yes/no): "))

    if truefalse(answer):
        path: str = str(
            input("Please type where do you want to SAMBA (pun intended): ")
        )
        create_dir(path)
        create_group()
        change_group(path)
        change_permissions(path)

    main_menu("config")


def config():
    option: int = 0
    print(
        "What do you want to config:\n"
        + "1 - Add a user\n"
        + "2 - Add a share\n"
        + "3 - Change a share\n"
        + "4 - Delete a share\n"
        + "5 - Delete a User\n"
        + "6 - Exit\n"
    )

    try:
        option = int(input("\nOption number: "))
    except Exception:
        option = 0

    condition: bool = (option >= 1) and (option <= 6)
    if not condition:
        while not condition:
            try:
                option = int(input("Option number: "))
            except Exception:
                option = 0

    switch(option)


def switch(type: int):

    # Python 3 with version < 3.10 does NOT have switch/match
    if type == 1:
        add_user()
    elif type == 2:
        add_share()
    elif type == 3:
        edit_share()
    elif type == 4:
        del_share()
    elif type == 5:
        del_user()
    elif type == 6:
        sys.exit()
    else:  # default
        main_menu("config")


def add_user():
    user: str = str(input("Username: "))
    passwd: str = str(input("Password: "))
    path: str = str(input("SAMBA share / user directory: "))

    create_user(user, path)
    add_passwd(passwd, user)

    if not os.path.isdir(path):
        create_dir(path)
        change_ownership(user, path)
        change_permissions(path)

    main_menu("config")


def del_user():
    user: str = str(input("user: "))
    answer: str = str(input("Are you sure (yes/no): "))
    if answer != "yes":
        main_menu("config")
    disable_user(user)
    delete_user(user)

    main_menu("config")


def add_share():
    name: str = str(input("Share name: "))
    user: str = str(input("For which user: "))
    users: str = str(input("Who else?"))
    path: str = str(input("Where: "))

    if not os.path.isdir(path):
        create_dir(path=path)
        change_ownership(user, path)
        change_permissions(path=path)

    browseable: str = str(input("Browseable (yes/no): "))
    if browseable != "yes":
        browseable = "no"
    readonly: str = str(input("Read only (yes/no): "))
    if readonly != "yes":
        readonly = "no"

    add_block(
        get_line_count(),
        build_block(
            name, user, users, path, truefalse(browseable), truefalse(readonly)
        ),
    )

    main_menu("config")


def edit_share():
    name: str = str(input("Share name: "))
    user: str = str(input("For which user: "))
    users: str = str(input("Who else?"))
    path: str = str(input("Where: "))

    browseable: str = str(input("Browseable (yes/no): "))
    if browseable != "yes":
        browseable = "no"
    readonly: str = str(input("Read only (yes/no): "))
    if readonly != "yes":
        readonly = "no"

    line_n = get_line(str("[" + name + "]"))
    if line_n < 0:
        line_n = get_line_count()

    change_block(
        line_n,
        build_block(
            name, user, users, path, truefalse(browseable), truefalse(readonly)
        ),
    )

    main_menu("config")


def del_share():
    name: str = str(input("Share name: "))

    remove_block(get_line(str("[" + name + "]")))

    main_menu("config")


def build_block(
    name: str = "sambauser",
    user: str = "sambauser",
    users: str = "@sambashare",
    path: str = "/samba",
    browseable: bool = True,
    readonly: bool = False,
):
    block: list = [
        str("[" + name + "]"),
        str("        path = " + path),
        str("        browseable = " + yesno(browseable)),
        str("        read only = " + yesno(readonly)),
        "        force create mode = 0660",
        "        force directory mode = 2770",
        str("        valid users = " + user + " " + users),
    ]
    return block


def yesno(polarity: bool):
    if polarity:
        return "yes"
    return "no"


def truefalse(polarity: str):
    if polarity == "yes":
        return True
    return False


def fix_file():
    shutil.move("/etc/samba/smb.conf", "/etc/samba/smb.conf~")
    with open("/etc/samba/smb.conf~", "r") as exports:
        data = exports.read().replace("\r\n", "\n")
        new = open("/etc/samba/smb.conf", "a")
        new.write(data)
        new.flush()
        new.truncate()
        new.close()
    os.remove("/etc/samba/smb.conf~")


def get_line(share: str):
    fix_file()
    i: int = 0
    with open("/etc/samba/smb.conf", "r") as exports:
        data: list = exports.read().split("\n")
        for line in data:
            if line.__contains__(share):
                return i
            i += 1
    return -1


def get_line_count():
    fix_file()
    count: int = -1
    with open("/etc/samba/smb.conf", "r") as exports:
        data: list = exports.read().split("\n")
        for line in data:
            count += 1
    return count


def get_block(index: int):
    fix_file()
    i: int = 0
    jumps: int = 0
    block: list = []
    with open("/etc/samba/smb.conf", "r") as exports:
        data: list = exports.read().split("\n")
        for line in data:
            if index == i:
                if jumps < 7:
                    block.append(line)
                    jumps += 1
                    index += 1
            i += 1
    return block


def remove_block(index: int):
    fix_file()
    i: int = 0
    jumps: int = 0
    shutil.move("/etc/samba/smb.conf", "/etc/samba/smb.conf~")
    with open("/etc/samba/smb.conf~", "r") as exports:
        new = open("/etc/samba/smb.conf", "a")
        data: list = exports.read().split("\n")
        for line in data:
            if index == i:
                if jumps < 7:
                    # Just skip
                    jumps += 1
                    index += 1
            else:
                new.write(line + "\n")
            i += 1
        new.write("")
        new.flush()
        new.truncate()
        new.close()
    os.remove("/etc/samba/smb.conf~")


def change_block(index: int, block: list):
    fix_file()
    i: int = 0
    jumps: int = 0
    shutil.move("/etc/samba/smb.conf", "/etc/samba/smb.conf~")
    with open("/etc/samba/smb.conf~", "r") as exports:
        new = open("/etc/samba/smb.conf", "a")
        data: list = exports.read().split("\n")
        for line in data:
            if index == i:
                if jumps < 7:
                    new.write(block[jumps] + "\n")
                    jumps += 1
                    index += 1
            else:
                new.write(line + "\n")
            i += 1
        new.write("")
        new.flush()
        new.truncate()
        new.close()
    os.remove("/etc/samba/smb.conf~")


def add_block(index: int, block: list):
    fix_file()
    i: int = 0
    shutil.move("/etc/samba/smb.conf", "/etc/samba/smb.conf~")
    with open("/etc/samba/smb.conf~", "r") as exports:
        new = open("/etc/samba/smb.conf", "a")
        data: list = exports.read().split("\n")
        for line in data:
            if index == i:
                for j in range(0, len(block)):
                    i += 1
                    new.write(block[j] + "\n")
            else:
                new.write(line + "\n")
            i += 1
        new.write("")
        new.flush()
        new.truncate()
        new.close()
    os.remove("/etc/samba/smb.conf~")


def change_ownership(
    user: str = "sambauser", path: str = "/samba", group: str = "sambashare"
):
    ownership: str = user + ":" + group
    try:
        subprocess.run(["chown", ownership, path], check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)
        sys.exit()


def change_permissions(path: str = "/samba"):
    try:
        subprocess.run(["chmod", "2770", path], check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)
        sys.exit()


def create_dir(path: str = "/samba"):
    if not os.path.isdir(path):
        os.makedirs(path, mode=0o770, exist_ok=True)


def create_group(groupname: str = "sambashare"):
    try:
        subprocess.run(["groupadd", groupname], check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)
        # sys.exit()


def change_group(path: str = "/samba", group: str = "sambashare"):
    try:
        subprocess.run(["chgrp", group, path], check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)
        sys.exit()


def create_user(
    username: str = "sambauser", path: str = "/samba", groupname: str = "sambashare"
):
    command: str = (
        "useradd -M -d "
        + path
        + "/"
        + username
        + " -s /usr/sbin/nologin -G "
        + groupname
        + " "
        + username
    )
    try:
        subprocess.run(command.split(), check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)


def add_passwd(passwd: str, user: str = "sambauser"):
    try:
        proc = subprocess.Popen(["smbpasswd", "-a", "-s", user], stdin=subprocess.PIPE)
        proc.communicate(input=(passwd + "\n" + passwd + "\n").encode("big5"))
        proc.communicate()
    except subprocess.CalledProcessError as e:
        print(e.output)
        sys.exit()

    try:
        subprocess.run(["smbpasswd", "-e", user], check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)
        sys.exit()


def disable_user(user: str = "sambauser"):
    try:
        subprocess.run(["smbpasswd", "-d", user], check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)
        sys.exit()


def delete_user(user: str = "sambauser"):
    try:
        subprocess.run(["userdel", "-r", user], check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)
        sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])
