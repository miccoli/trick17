# SPDX-FileCopyrightText: 2023-present Stefano Miccoli <stefano.miccoli@polimi.it>
#
# SPDX-License-Identifier: MIT

"""internal utility functions"""

import array
import errno
import fcntl
import os
import socket


def make_socket() -> socket.socket:
    """return a SOCK_DGRAM socket for communication with systemd"""
    return socket.socket(family=socket.AF_UNIX, type=socket.SOCK_DGRAM)


def send_dgram_or_fd(sock: socket.socket, payload: bytes, address: str) -> None:
    """implement systemd logic: first try to send payload as a datagram,
    if failed, retry sending as a mem_fd.
    """
    retry_fd: bool
    try:
        nsent = sock.sendto(payload, address)
        assert nsent == len(payload), f"Boundary broken? {nsent} != {len(payload)}"
        retry_fd = False
    except OSError as err:
        if err.errno == errno.EMSGSIZE:
            retry_fd = True
        else:
            raise
    if retry_fd:
        # send big payload as a memfd
        fd = os.memfd_create(
            "journal_entry", flags=os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING
        )
        nwr = os.write(fd, payload)
        assert nwr == len(
            payload
        ), f"Unable to write to memfd: {nwr} != {len(payload)}"
        # see https://github.com/systemd/systemd/issues/27608
        fcntl.fcntl(
            fd,
            fcntl.F_ADD_SEALS,
            fcntl.F_SEAL_SHRINK
            | fcntl.F_SEAL_GROW
            | fcntl.F_SEAL_WRITE
            | fcntl.F_SEAL_SEAL,
        )
        _send_fds(sock=sock, buffers=[], fds=[fd], address=address)


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
