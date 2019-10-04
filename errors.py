import sys


class version_error(Exception):
    pass


class session_exipred(Exception):
    pass


class smtp_connection_fail(Exception):
    pass


class credentials_failed(Exception):
    pass


class failed_login(Exception):
    pass


class register_error(Exception):
    pass
