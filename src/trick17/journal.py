# SPDX-FileCopyrightText: 2023-present Stefano Miccoli <stefano.miccoli@polimi.it>
#
# SPDX-License-Identifier: MIT

import errno
import logging
import os
import socket
import struct
import sys
import syslog


def stderr_is_journal() -> bool:
    stat = os.fstat(sys.stderr.fileno())
    return os.environ.get("JOURNAL_STREAM", "") == f"{stat.st_dev}:{stat.st_ino}"


class JournalHandler(logging.Handler):
    """Simple logger for the Systemd Native Journal Protocol"""

    SADDR: str = "/run/systemd/journal/socket"

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

    def __init__(self) -> None:
        super().__init__()
        self.soxx = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_DGRAM)
        self.soxx.settimeout(None)

    def emit(self, record: logging.LogRecord) -> None:
        """emit record on journald socket"""

        lev = self._log_level(record.levelno)
        msg = self.format(record)
        dg: bytes = (
            self._serialize(b"MESSAGE", msg.encode()) + f"PRIORITY={lev:d}\n"
            f"LOGGER={record.name}\n"
            f"THREAD_NAME={record.threadName}\n"
            f"PROCESS_NAME={record.processName}\n"
            f"CODE_FILE={record.pathname}\n"
            f"CODE_LINE={record.lineno}\n"
            f"CODE_FUNC={record.funcName}\n".encode()
        )
        try:
            nsent = self.soxx.sendto(dg, self.SADDR)
        except OSError as err:
            if err.errno == errno.EMSGSIZE:
                # FIXME: implement alternative protocol
                errmsg = "Log record to long, but fd logging not implemented"
                raise NotImplementedError(errmsg) from err
            else:
                raise
        assert nsent == len(dg), f"Boundary broken? {nsent} != {len(dg)}"
