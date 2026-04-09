#! /usr/bin/env python3

import imaplib, email, string
from tqdm import tqdm
from pathlib import Path
from datetime import date
from random import choice
from getpass import getpass
from email.parser import Parser
from argparse import ArgumentParser
from time import strftime, localtime
from colorama import Fore, Style

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
    description = "Mail Dumping using IMAP"
    parser = ArgumentParser(description=description)
    parser.add_argument('-u', "--user", type=str, required=True, help="Username of EMail")
    parser.add_argument('-s', "--server", type=str, required=True, help="Address of IMAP Server")
    parser.add_argument('-p', "--port", type=int, help=f"Port of IMAP Server (Default={imap_port})", default=imap_port)
    parser.add_argument('-S', "--use-ssl", action="store_true", help=f"Use SSL for Transfering Mail Data from IMAP Server (Default={use_ssl})", default=True)
    parser.add_argument('-d', "--delete", action="store_true", help="Delete Mails from the server after Backup")
    return parser.parse_args()

if __name__ == "__main__":
    arguments = get_arguments()
    password = getpass(f"Enter password for [{arguments.user}@{arguments.server}:{arguments.port}] : ")

    display(':', f"Connecting to Server {Fore.LIGHTBLUE_EX}{arguments.server}:{arguments.port}{Fore.RESET}")
    try:
        Mailbox = imaplib.IMAP4_SSL(arguments.server, port=arguments.port) if arguments.use_ssl else imaplib.IMAP4(arguments.server, port=arguments.port)
    except:
        display('-', f"Can't Reach IMAP Server {Fore.LIGHTBLUE_EX}{arguments.server}:{arguments.port}{Fore.RESET}")
        exit(0)
    display(':', f"Authenticating User {Fore.MAGENTA}{arguments.user}{Fore.CYAN}  @ IMAP Server {Fore.LIGHTBLUE_EX}{arguments.server}:{arguments.port}{Fore.RESET}")
    try:
        Mailbox.login(arguments.user, password)
    except:
        display('-', f"Authentication Failed for User {Fore.MAGENTA}{arguments.user}{Fore.RED} @ IMAP Server {Fore.LIGHTBLUE_EX}{arguments.server}:{arguments.port}{Fore.RESET}")
        exit(0)
    display('+', f"User {Fore.MAGENTA}{arguments.user}{Fore.GREEN} Authenticated @ {Fore.LIGHTBLUE_EX}{arguments.server}:{arguments.port}{Fore.RESET}")

    list_status, mailboxes = Mailbox.list()
    mailboxes = [str(mailbox)[str(mailbox).index('"." ')+4:].replace('"', '').replace("'", '') for mailbox in mailboxes]
    display(':', f"Total Mailboxes = {len(mailboxes)}")
    for mailbox in mailboxes:
        display('+', f"\t* {mailbox}")
    print()

    cwd = Path.cwd()
    user_directory = cwd / f"{arguments.server}:{arguments.port}" / arguments.user
    user_directory.mkdir(exist_ok=True, parents=True)

    for mailbox in mailboxes:
        mailbox_directory = user_directory / mailbox
        mailbox_directory.mkdir(exist_ok=True)
        Mailbox.select(f'"{mailbox}"')
        search_status, mail_data = Mailbox.search(None, "ALL")
        try:
            mail_indexes = [mail_index for mail_index in str(mail_data[0]).replace('b', '').replace("'", '').split(' ') if mail_index != '']
            total_mails = len(mail_indexes)
            if total_mails == 0:
                display('+', f"No Mails Found in {Fore.MAGENTA}{mailbox}{Fore.RESET}", end='\n\n')
                continue
        except ValueError:
            display('+', f"No Mails Found in {Fore.MAGENTA}{mailbox}{Fore.RESET}", end='\n\n')
            continue
        for index, mail_index in enumerate(tqdm(mail_indexes, desc=f"Fetching Mails from {mailbox}", unit="mail", colour="green")):
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
                        try:
                            with open(f"{arguments.server}:{arguments.port}/{arguments.user}/{mailbox}/{mail_index}/attachments/{fileName}", 'wb') as file:
                                file.write(part.get_payload(decode=True))
                        except Exception as error:
                            with open(f"{arguments.server}:{arguments.port}/{arguments.user}/{mailbox}/{mail_index}/attachments/{''.join(choice(string.ascii_letters) for _ in range(10))}", 'wb') as file:
                                file.write(part.get_payload(decode=True))
                    except TypeError:
                        pass
            if arguments.delete:
                Mailbox.store(mail_index, "+FLAGS", "\\Deleted")
        print('\n')
    if arguments.delete:
        Mailbox.expunge()
    Mailbox.close()
    Mailbox.logout()