# Retention and disposal

The private repository contains source and documentation only. Downloaded Telegram media remains in
the folder chosen by the user; the program does not delete or expire those files.

The Telegram authorisation session remains in the operating-system credential store until the user
removes the `telegram-dumper` entry there. The application does not currently expose a logout
command.

Do not store credentials, session exports, or downloaded user content in Git. Repository access,
archive, and deletion remain under the repository owner's control.
