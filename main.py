#! /usr/bin/env python3

import imaplib, email
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
use_ssl = True

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
                              ('-p', "--port", "port", f"Port of IMAP Server (Default={imap_port})"),
                              ('-S', "--use-ssl", "use_ssl", f"Use SSL for Transfering Mail Data from IMAP Server (Default={use_ssl})"))
    if not arguments.user:
        display('-', f"Please Provide a {Back.YELLOW}User{Back.RESET}")
        exit(0)
    if not arguments.server:
        display('-', f"Please Provide a {Back.YELLOW}Server{Back.RESET}")
        exit(0)
    arguments.port = imap_port if not arguments.port else int(arguments.port)
    arguments.use_ssl = False if arguments.use_ssl != None and 't' not in arguments.use_ssl.lower() else use_ssl
    password = getpass(f"Enter password for [{arguments.user}@{arguments.server}:{arguments.port}] : ")

    display(':', f"Connecting to Server {Back.MAGENTA}{arguments.server}:{arguments.port}{Back.RESET}")
    try:
        Mailbox = imaplib.IMAP4_SSL(arguments.server, port=arguments.port) if arguments.use_ssl else imaplib.IMAP4(arguments.server, port=arguments.port)
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

    list_status, mailboxes = Mailbox.list()
    mailboxes = [str(mailbox).split('"')[-1].replace("'", '').strip() for mailbox in mailboxes]
    display(':', f"Total Mailboxes = {Back.MAGENTA}{len(mailboxes)}{Back.RESET}")
    for mailbox in mailboxes:
        display('+', f"\t* {mailbox}")
    print()

    cwd = Path.cwd()
    user_directory = cwd / f"{arguments.server}:{arguments.port}" / arguments.user
    user_directory.mkdir(exist_ok=True, parents=True)

    for mailbox in mailboxes:
        display(':', f"Fetching {Back.MAGENTA}{mailbox}{Back.RESET}")
        mailbox_directory = user_directory / mailbox
        mailbox_directory.mkdir(exist_ok=True)
        Mailbox.select(mailbox)
        search_status, mail_data = Mailbox.search(None, "ALL")
        try:
            mail_indexes = [mail_index for mail_index in str(mail_data[0]).replace('b', '').replace("'", '').split(' ') if mail_index != '']
            total_mails = len(mail_indexes)
            if total_mails == 0:
                display('+', f"No Mails Found")
                continue
            display('+', f"Mails Found = {Back.MAGENTA}{total_mails}{Back.RESET}")
        except ValueError:
            display('+', f"No Mails Found")
            continue
        for index, mail_index in enumerate(mail_indexes):
            display('*', f"Mails Retrieved = {index+1}/{total_mails}", start='\r', end='')
            mail_status, individual_mail_data = Mailbox.fetch(mail_index, "(RFC822)")
            mail_directory = mailbox_directory / f"{mail_index}"
            mail_directory.mkdir(exist_ok=True)
            with open(f"{arguments.server}:{arguments.port}/{arguments.user}/{mailbox}/{mail_index}/mail.eml", 'wb') as file:
                file.write(individual_mail_data[0][1])
            try:
                with open(f"{arguments.server}:{arguments.port}/{arguments.user}/{mailbox}/{mail_index}/mail.eml", 'r') as file:
                    mail_headers = Parser().parse(file)
                with open(f"{arguments.server}:{arguments.port}/{arguments.user}/{mailbox}/{mail_index}/headers.txt", 'wb') as file:
                    file.write(f"Date: {(mail_headers['date'])}\n".encode())
                    file.write(f"From: {mail_headers['from']}\n".encode())
                    file.write(f"To: {mail_headers['to']}\n".encode())
                    file.write(f"CC: {mail_headers['cc']}\n".encode())
                    file.write(f"BCC: {mail_headers['bcc']}\n".encode())
                    file.write('\n'.encode())
            except:
                pass
            mail_message = email.message_from_bytes(individual_mail_data[0][1])
            for part in mail_message.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                fileName = part.get_filename()
                if bool(fileName):
                    try:
                        attachments_directory = mail_directory / "attachments"
                        attachments_directory.mkdir(exist_ok=True)
                        with open(f"{arguments.server}:{arguments.port}/{arguments.user}/{mailbox}/{mail_index}/attachments/{fileName}", 'wb') as file:
                            file.write(part.get_payload(decode=True))
                    except TypeError:
                        pass
        print('\n')