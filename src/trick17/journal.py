# SPDX-FileCopyrightText: 2023-present Stefano Miccoli <stefano.miccoli@polimi.it>
#
# SPDX-License-Identifier: MIT

import array
import errno
import fcntl
import logging
import os
import socket
import stat
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
        # check if SADDR is accessible and a socket
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
                self._serialize(b"MESSAGE", msg.encode()) + f"PRIORITY={lev:d}\n"
                f"LOGGER={record.name}\n"
                f"THREAD_NAME={record.threadName}\n"
                f"PROCESS_NAME={record.processName}\n"
                f"CODE_FILE={record.pathname}\n"
                f"CODE_LINE={record.lineno}\n"
                f"CODE_FUNC={record.funcName}\n".encode()
            )
            # try sending j_entry as a datagram payload
            try:
                nsent = self.soxx.sendto(j_entry, self.SADDR)
                assert nsent == len(
                    j_entry
                ), f"Boundary broken? {nsent} != {len(j_entry)}"
                retry_fd = False
            except OSError as err:
                if err.errno == errno.EMSGSIZE:
                    retry_fd = True
                else:
                    raise
            if retry_fd:
                # send big message as a memfd
                fd = os.memfd_create(
                    "journal_entry", flags=os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING
                )
                nwr = os.write(fd, j_entry)
                assert nwr == len(
                    j_entry
                ), f"Unable to write to memfd: {nwr} != {len(j_entry)}"
                # see https://github.com/systemd/systemd/issues/27608
                fcntl.fcntl(
                    fd,
                    fcntl.F_ADD_SEALS,
                    fcntl.F_SEAL_SHRINK
                    | fcntl.F_SEAL_GROW
                    | fcntl.F_SEAL_WRITE
                    | fcntl.F_SEAL_SEAL,
                )
                _send_fds(sock=self.soxx, buffers=[], fds=[fd], address=self.SADDR)
        except Exception:
            self.handleError(record)


def _send_fds(sock, buffers, fds, flags=0, address=None):
    """send_fds(sock, buffers, fds[, flags[, address]]) -> integer

    Send the list of file descriptors fds over an AF_UNIX socket.

    *** Patch to fix cpython bug GH-107898 ***
    """
    return sock.sendmsg(
        buffers,
        [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array("i", fds))],
        flags,
        address,
    )
