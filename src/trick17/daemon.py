# SPDX-FileCopyrightText: 2023-present Stefano Miccoli <stefano.miccoli@polimi.it>
#
# SPDX-License-Identifier: MIT

import os
from collections.abc import Iterator
from pathlib import Path

import trick17
from trick17 import util

__all__ = ["booted", "notify"]


def booted() -> bool:
    """booted() returns True is system was booted by systemd"""
    return Path(trick17.SD_BOOTED_PATH).is_dir()


def listen_fds() -> Iterator[tuple[int, str]]:
    """listen_fds() returns an iterator over (fd, name) tuples, where
    - fd is an open file descriptor intialized by systemd socket-activation
    - name is an optional name, '' if undefined.
    """

    # check pid
    if trick17.SD_LISTEN_FDS_PID_ENV not in os.environ:
        return iter(())
    try:
        pid = int(os.environ[trick17.SD_LISTEN_FDS_PID_ENV])
    except ValueError as err:
        msg = f"Unable to get pid from environment: {err}"
        raise RuntimeError(msg) from err
    if os.getpid() != pid:
        return iter(())

    # check FDS
    nfds: int
    try:
        nfds = int(os.environ[trick17.SD_LISTEN_FDS_ENV])
    except KeyError as err:
        msg = f"Unable to get number of fd's from environment: {err}"
        raise RuntimeError(msg) from err
    except ValueError as err:
        msg = f"Parsing of fd's from environment failed: {err}"
        raise RuntimeError(msg) from err
    if nfds < 1:
        msg = f"Invalid number of fd's in environment: {nfds:d}"
        raise RuntimeError(msg)
    fds = range(trick17.SD_LISTEN_FDS_START, trick17.SD_LISTEN_FDS_START + nfds)
    assert len(fds) == nfds

    # check names
    names: list[str]
    if trick17.SD_LISTEN_FDS_NAMES_ENV not in os.environ:
        names = [""] * nfds
    else:
        names = os.environ[trick17.SD_LISTEN_FDS_NAMES_ENV].split(os.pathsep)
        if len(names) > nfds:
            names = names[:nfds]
        elif len(names) < nfds:
            names.extend("" for _ in range(nfds - len(names)))
    assert len(names) == len(fds)

    return zip(fds, names, strict=True)


def notify(*msg: str) -> bool:
    """notify '*msg' messages to systemd;
    returns
    - True if notification sent to socket,
    - False if environment variable with notification socket is not set."""

    sock_path: str = os.getenv(trick17.SD_NOTIFY_SOCKET_ENV, "")
    if not sock_path:
        return False

    state = "\n".join(m.strip() for m in msg)

    match sock_path.split(":"):
        case [dest] if dest.startswith("/"):
            # AF_UNIX
            with util.make_socket() as sock:
                util.send_dgram_or_fd(sock, state.encode(), sock_path)
        case [dest] if dest.startswith("@"):
            # Linux abstract namespace socket
            errmsg = f"Abstract namespace sockets not implemented ('{sock_path}')"
            raise NotImplementedError(errmsg)
        case ["vsock", cid, port]:  # noqa: F841
            # AF_VSOCK
            errmsg = f"AF_VSOCK sockets not implemented ('{sock_path}')"
            raise NotImplementedError(errmsg)
        case _:
            errmsg = f"Unrecognized type of socket: {sock_path}"
            raise ValueError(errmsg)

    return True
