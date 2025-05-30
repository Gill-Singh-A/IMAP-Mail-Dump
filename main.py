#! /usr/bin/env python3

import sys, imaplib, email
from pathlib import Path
from datetime import date
from getpass import getpass
from email.parser import Parser
from optparse import OptionParser
from time import strftime, localtime
from colorama import Fore, Back, Style

status_color = {
    '+': Fore.GREEN,
    '-': Fore.RED,
    '*': Fore.YELLOW,
    ':': Fore.CYAN,
    ' ': Fore.WHITE
}

imap_port = 993

def display(status, data, start='', end='\n'):
    print(f"{start}{status_color[status]}[{status}] {Fore.BLUE}[{date.today()} {strftime('%H:%M:%S', localtime())}] {status_color[status]}{Style.BRIGHT}{data}{Fore.RESET}{Style.RESET_ALL}", end=end)

def get_arguments(*args):
    parser = OptionParser()
    for arg in args:
        parser.add_option(arg[0], arg[1], dest=arg[2], help=arg[3])
    return parser.parse_args()[0]

if __name__ == "__main__":
    arguments = get_arguments(('-u', "--user", "user", "Username of EMail"),
                              ('-s', "--server", "server", "Address of IMAP Server"),
                              ('-p', "--port", "port", f"Port of IMAP Server (Default={imap_port})"))
    if not arguments.user:
        display('-', f"Please Provide a {Back.YELLOW}User{Back.RESET}")
        exit(0)
    if not arguments.server:
        display('-', f"Please Provide a {Back.YELLOW}Server{Back.RESET}")
        exit(0)
    arguments.port = imap_port if not arguments.port else int(arguments.port)
    password = getpass(f"Enter password for {arguments.user}@{arguments.server}:{arguments.port} => ")

    display(':', f"Connecting to Server {Back.MAGENTA}{arguments.server}:{arguments.port}{Back.RESET}")
    try:
        Mailbox = imaplib.IMAP4_SSL(arguments.server, port=arguments.port)
    except:
        display('-', f"Can't Reach IMAP Server {Back.MAGENTA}{arguments.server}:{arguments.port}{Back.RESET}")
        exit(0)
    display(':', f"Authenticating User {Back.MAGENTA}{arguments.user}{Back.RESET}  @ IMAP Server {Back.MAGENTA}{arguments.server}:{arguments.port}{Back.RESET}")
    try:
        Mailbox.login(arguments.user, password)
    except:
        display('-', f"Authentication Failed for User {Back.MAGENTA}{arguments.user}{Back.RESET} @ IMAP Server {Back.MAGENTA}{arguments.server}:{arguments.port}{Back.RESET}")
        exit(0)
    display('+', f"User {Back.MAGENTA}{arguments.user}{Back.RESET} Authenticated @ {Back.MAGENTA}{arguments.server}:{arguments.port}{Back.RESET}")