# IMAP Mail Dump
A Simple Python Program that uses imaplib for dumping Mails from an IMAP Server
## Requirements
Langauge Used = Python3<br />
Modules/Packages used:
* imaplib
* email
* pathlib
* datetime
* getpass
* optparse
* time
* colorama
<!-- -->
Install the dependencies:
```bash
pip install -r requirements.txt
```
## Output
The emails are saved in a structured directory format based on the server, user, mailbox, and individual email index. The directory layout is as follows:
```
server:port/
└── user/
    ├── INBOX/
    │   ├── 1/
    │   │   ├── mail.eml
    │   │   ├── headers.txt
    │   │   └── attachments/
    │   │       └── <filename1>
    │   ├── 2/
    │   │   └── ...
    │   └── ...
    ├── Sent/
    │   └── ...
    └── <Other Mailboxes>/
        └── ...
```
### File Details:
* `mail.eml`: The full raw email file.
* `headers.txt`: Parsed headers including Date, From, To, CC, BCC.
* `attachments/`: A directory containing all file attachments for that email, if present.