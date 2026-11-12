# Retention and disposal

The public repository contains source and documentation only. Downloaded Telegram media remains in
the folder chosen by the user; the program does not delete or expire those files.

Each Telegram authorisation session remains in the operating-system credential store until the user
removes the account with `telegram-dumper accounts remove ACCOUNT_ID` or deletes its credential-store
entry manually. The account list is kept in the local application configuration directory and can
be removed separately. API credentials are not removed when an account session is removed.

Do not store credentials, session exports, or downloaded user content in Git. Repository access,
archive, and deletion remain under the repository owner's control.
