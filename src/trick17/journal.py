# SPDX-FileCopyrightText: 2023-present Stefano Miccoli <stefano.miccoli@polimi.it>
#
# SPDX-License-Identifier: MIT

"""This module contains classes and functions for logging to the systemd journal,
using the Native Journal Protocol, see <https://systemd.io/JOURNAL_NATIVE_PROTOCOL/>
"""

import logging
import os
import stat
import struct
import sys
import syslog

import trick17
from trick17 import util


def stderr_is_journal() -> bool:
    stat = os.fstat(sys.stderr.fileno())
    return (
        os.environ.get(trick17.SD_JOURNAL_STREAM_ENV, "")
        == f"{stat.st_dev}:{stat.st_ino}"
    )


class JournalHandler(logging.Handler):
    """A handler class which writes structured logging records to the
    systemd journal using the Systemd Native Journal Protocol"""

    SADDR: str = trick17.SD_JOURNAL_SOCKET_PATH

    def __init__(self) -> None:
        """Initialize the handler."""

        super().__init__()

        # create socket for systemd protocol
        self.sock = util.make_socket()

        # we leave sock unconnected, but verify that SADDR is an accessible socket
        # in order to fail at handler instantiation
        if not os.access(self.SADDR, os.F_OK):
            msg = f"Nonexistent journal socket '{self.SADDR}'"
            raise RuntimeError(msg)
        elif not os.access(self.SADDR, os.W_OK):
            msg = f"Not writable journal socket '{self.SADDR}'"
            raise RuntimeError(msg)
        res = os.stat(self.SADDR)
        if not stat.S_ISSOCK(res.st_mode):
            msg = f"'{self.SADDR}' not a socket"
            raise RuntimeError(msg)

    def emit(self, record: logging.LogRecord) -> None:
        """emit record on journald socket"""

        try:
            # build journal entry
            lev: int = self._log_level(record.levelno)
            msg: str = self.format(record)
            j_entry: bytes = (
                self._serialize(b"MESSAGE", msg.encode())
                + f"PRIORITY={lev:d}\n"
                f"LOGGER={record.name}\n"
                f"THREAD_NAME={record.threadName}\n"
                f"PROCESS_NAME={record.processName}\n"
                f"CODE_FILE={record.pathname}\n"
                f"CODE_LINE={record.lineno}\n"
                f"CODE_FUNC={record.funcName}\n".encode()
            )
            util.send_dgram_or_fd(self.sock, j_entry, self.SADDR)
        except Exception:
            self.handleError(record)

    @staticmethod
    def _serialize(key: bytes, val: bytes) -> bytes:
        lkey = len(key)
        lval = len(val)
        fmt = f"<{lkey:d}ssQ{lval:d}ss"
        return struct.pack(fmt, key, b"\n", lval, val, b"\n")

    @staticmethod
    def _log_level(level: int) -> int:
        if level >= logging.CRITICAL:
            return syslog.LOG_CRIT
        elif level >= logging.ERROR:
            return syslog.LOG_ERR
        elif level >= logging.WARNING:
            return syslog.LOG_WARNING
        elif level >= logging.INFO:
            return syslog.LOG_INFO
        elif level > logging.NOTSET:
            return syslog.LOG_DEBUG

        msg = f"Invalid log level: {level}"
        raise ValueError(msg)
