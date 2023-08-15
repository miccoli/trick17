# SPDX-FileCopyrightText: 2023-present Stefano Miccoli <stefano.miccoli@polimi.it>
#
# SPDX-License-Identifier: MIT

import os
from pathlib import Path

import trick17
from trick17 import util

__all__ = ["booted", "notify"]


def booted() -> bool:
    """booted() returns True is system was booted by systemd"""
    return Path(trick17.SD_BOOTED_PATH).is_dir()


def notify(state: str) -> bool:
    """notify 'state' to systemd; returns
    - True if notification sent to socket,
    - False if environment variable with notification socket is not set."""

    sock_path: str = os.getenv(trick17.SD_NOTIFY_SOCKET_ENV, "")
    if not sock_path:
        return False

    if not sock_path.startswith("/"):
        msg = f"notify to socket type '{sock_path}' not supported"
        raise NotImplementedError(msg)
    with util.make_socket() as sock:
        util.send_dgram_or_fd(sock, state.encode(), sock_path)
    return True
