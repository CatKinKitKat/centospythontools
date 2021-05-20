#!/bin/env python3

import sys, os, shutil, subprocess


def main(arguments: list):
    if len(arguments) != 5:
        if arguments[0] == "help":
            print(
                "nfs_util.py add all alias.com ip.ad.dr.ess port\n"
                "nfs_util.py add vhost alias.com ip.ad.dr.ess port\n"
                "nfs_util.py add forward alias.com ip.ad.dr.ess\n"
                "nfs_util.py add reverse alias.com ip.ad.dr.ess\n"
                "nfs_util.py remove all alias.com ip.ad.dr.ess port\n"
                "nfs_util.py remove vhost alias.com\n"
                "nfs_util.py remove forward alias.com\n"
                "nfs_util.py remove reverse alias.com ip.ad.dr.ess\n"
            )
            sys.exit()
        elif arguments[0] == "add":
            if arguments[1] == "all":
                add_vhost(arguments[2], arguments[4])
                add_forward(arguments[2], arguments[3])
                add_reverse(arguments[2], arguments[3])
            elif arguments[1] == "vhost":
                add_vhost(arguments[2], arguments[4])
            elif arguments[1] == "forward":
                add_forward(arguments[2], arguments[3])
            elif arguments[1] == "reverse":
                add_reverse(arguments[2], arguments[3])
        elif arguments[0] == "remove":
            if arguments[1] == "all":
                remove_vhost(arguments[2])
                remove_forward(arguments[2])
                remove_reverse(arguments[2], arguments[3])
            elif arguments[1] == "vhost":
                remove_vhost(arguments[2])
            elif arguments[1] == "forward":
                remove_forward(arguments[2])
            elif arguments[1] == "reverse":
                remove_reverse(arguments[2], arguments[3])

    print("The only accepted types are add|remove all|vhost|forward|reverse.")
    sys.exit()


def add_forward(alias: str, ip: str):
    index = get_line(alias, "/etc/named.conf")
    if index < 0:
        add_block(
            get_line_count("/etc/named.conf"),
            "/etc/named.conf",
            build_zone_forward_block(alias),
        )
    file = "/var/named/" + alias + ".hosts"
    if not os.path.isfile(file):
        try:
            subprocess.run(["touch", file], check=True)
        except subprocess.CalledProcessError as e:
            print(e.output)
            sys.exit()
        add_block(get_line_count(file), file, build_table_forward_block(alias, ip))


def remove_forward(alias: str):
    index = get_line(alias, "/etc/named.conf")
    if index < 0:
        remove_block(index, "/etc/named.conf", 5)
    file = "/var/named/" + alias + ".hosts"
    if os.path.isfile(file):
        os.remove(file)


def add_reverse(alias: str, ip: str):
    index = get_line(alias, "/etc/named.conf")
    if index >= 0:
        add_block(
            get_line_count("/etc/named.conf"),
            "/etc/named.conf",
            build_zone_reverse_block(alias, ip_spliter(ip, True)),
        )
    file = "/var/named/reverse." + alias + ".hosts"
    if not os.path.isfile(file):
        try:
            subprocess.run(["touch", file], check=True)
        except subprocess.CalledProcessError as e:
            print(e.output)
            sys.exit()
        add_block(
            get_line_count(file), file, build_table_reverse_block(alias, ip_spliter(ip))
        )


def remove_reverse(alias: str, ip: str):
    index = get_line(alias, "/etc/named.conf")
    if index >= 0:
        remove_block(index, "/etc/named.conf", 5)
    file = "/var/named/reverse." + alias + ".hosts"
    if os.path.isfile(file):
        os.remove(file)


def ip_spliter(ip: str, option: bool = False):
    ip_blocks = ip.split(".")
    if option:
        return str(ip_blocks[0] + "." + ip_blocks[1] + "." + ip_blocks[2])

    return str(ip_blocks[3])


def add_vhost(alias: str, port: str):
    file: str = "/etc/httpd/conf.d/" + alias + ".conf"
    path: str = "/var/www/" + alias
    subprocess.run(["touch", file], check=True)
    add_example_page(path)
    add_block(
        get_line_count(file),
        file,
        build_vhost_block(port, str("www." + alias), path, alias),
    )
    sysctl()


def remove_vhost(alias: str):
    file: str = "/etc/httpd/conf.d/" + alias + ".conf"
    path: str = "/var/www/" + alias
    shutil.rmtree(path)
    os.remove(file)
    sysctl()


def build_zone_forward_block(alias: str):
    block: list = [
        str('zone "' + alias + '" IN {'),
        "        type master;",
        str('        file "/var/named/' + alias + '.hosts";'),
        "        allow-update { none; };",
        "};\n",
    ]
    return block


def build_zone_reverse_block(alias: str, first: str):
    block: list = [
        str('zone "' + first + '.in-addr-arpa" IN {'),
        "        type master;",
        str('        file "/var/named/reverse.' + alias + '.hosts";'),
        "};\n",
    ]
    return block


def build_table_forward_block(alias: str, ip: str):
    block: list = [
        "$TTL 86400",
        str("@    IN SOA localhost.localdomain. root." + alias + ". ("),
        "     2011071001 ;Serial",
        "     3600 ;Refresh",
        "     1800 ;Retry",
        "     604800 ;Expire",
        "     86400 ;Minimum TTL",
        ")",
        "@    IN NS  localhost.localdomain.",
        str("@    IN A   " + ip),
        str("www  IN A   " + ip),
        str("mail IN A   " + ip),
    ]
    return block


def build_table_reverse_block(alias: str, last: str):
    block: list = [
        "$TTL 86400",
        str("@    IN SOA localhost.localdomain. root." + alias + ". ("),
        "     2011071001 ;Serial",
        "     3600 ;Refresh",
        "     1800 ;Retry",
        "     604800 ;Expire",
        "     86400 ;Minimum TTL",
        ")",
        "@    IN NS  localhost.localdomain.",
        str(last + "   IN PTR   " + alias + "."),
        str(last + "   IN PTR   www." + alias + "."),
        str(last + "   IN MX    mail." + alias + "."),
    ]
    return block


def build_vhost_block(port: int, name: str, path: str, alias: str):
    block: list = [
        str("<VirtualHost *:" + port + ">"),
        str("    ServerName " + name),
        str("    DocumentRoot " + path + "/public_html"),
        str("    ServerAlias " + alias),
        str("    ErrorLog " + path + "/error.log"),
        str("    CustomLog " + path + "/requests.log combined"),
        "</VirtualHost>",
    ]
    return block


def fix_file(file: str):
    workingfile: str = file + "~"
    shutil.move(file, workingfile)
    with open(workingfile, "r") as exports:
        data = exports.read().replace("\r\n", "\n")
        new = open(file, "a")
        new.write(data)
        new.truncate()
        new.close()
    os.remove(workingfile)


def get_line(conf: str, file: str):
    fix_file(file)
    i: int = 0
    with open(file, "r") as exports:
        data: list = exports.read().split("\n")
        for line in data:
            if line.__contains__(conf):
                return i
            i += 1
    return -1


def get_line_count(file: str):
    fix_file(file)
    count: int = -1
    with open(file, "r") as exports:
        data: list = exports.read().split("\n")
        for line in data:
            count += 1
    return count


def get_block(index: int, file: str):
    fix_file(file)
    i: int = 0
    jumps: int = 0
    block: list = []
    with open(file, "r") as exports:
        data: list = exports.read().split("\n")
        for line in data:
            if index == i:
                if jumps < 7:
                    block.append(line)
                    jumps += 1
                    index += 1
                i += 1
    return block


def remove_block(index: int, file: str, size: int):
    fix_file(file)
    i: int = 0
    jumps: int = 0
    workingfile: str = file + "~"
    shutil.move(file, workingfile)
    with open(workingfile, "r") as exports:
        new = open(file, "a")
        data: list = exports.read().split("\n")
        for line in data:
            if index == i:
                if jumps < size:
                    # Just skip
                    jumps += 1
                    index += 1
            else:
                new.write(line + "\n")
            i += 1
        new.write("")
        new.truncate()
        new.close()
    os.remove(workingfile)


def change_block(index: int, file: str, block: list):
    fix_file(file)
    i: int = 0
    jumps: int = 0
    workingfile: str = file + "~"
    shutil.move(file, workingfile)
    with open(workingfile, "r") as exports:
        new = open(file, "a")
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
        new.truncate()
        new.close()
    os.remove(workingfile)


def add_block(index: int, file: str, block: list):
    fix_file(file)
    i: int = 0
    workingfile: str = file + "~"
    shutil.move(file, workingfile)
    with open(workingfile, "r") as exports:
        new = open(file, "a")
        data: list = exports.read().split("\n")
        for line in data:
            if index == i:
                for i in range(0, len(block)):
                    i += 1
                    new.write(block[i] + "\n")
            else:
                new.write(line + "\n")
            i += 1
        new.write("")
        new.truncate()
        new.close()
    os.remove(workingfile)


def symlink_website(name: str):
    config: str = "/etc/httpd/sites-available/" + name
    link: str = "/etc/httpd/conf.d/" + name

    try:
        subprocess.run(["ln", "-s", config, link], check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)
        sys.exit()


def create_vhost_directory(path: str):
    path = path + "/public_html"
    if not os.path.isdir(path):
        os.makedirs(path, mode=0o770, exist_ok=True)


def create_directory(path: str):
    if not os.path.isdir(path):
        os.makedirs(path, mode=0o770, exist_ok=True)


def add_example_page(path: str):
    if not os.path.isdir(path):
        create_vhost_directory(path)

    command: str = 'echo "<h1>Welcome!</h1>" >> ' + path + "/public_html/index.html"
    try:
        subprocess.run(command.split(), check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)
        sys.exit()


def sysctl():
    try:
        subprocess.run(["systemctl", "restart", "httpd"], check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)
        sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])
