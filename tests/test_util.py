import mmap
import random
import socket
import sys

import pytest

from trick17 import util


def test_make_socket():
    with util.make_socket() as sock:
        assert sock.fileno() != -1
        assert sock.gettimeout() is None


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="'socket.recv_fds' requires python3.9 or higher",
)
def test_send(tmp_path):
    sock_path = str(tmp_path / "socket")
    with util.make_socket() as a, util.make_socket() as b:
        a.bind(sock_path)

        for nsend in (1, 2**17, 2**18):
            out = random.getrandbits(nsend * 8).to_bytes(nsend, "little")

            util.send_dgram_or_fd(b, out, sock_path)

            msg, fds, msg_flags, _ = socket.recv_fds(a, len(out), 1)
            assert (
                msg_flags == 0
            ), f"Expecting 0, got msg_flags {socket.MsgFlag(msg_flags).name}"
            if msg:
                assert msg == out
                assert len(fds) == 0
            else:
                assert len(fds) == 1
                mm = mmap.mmap(fds[0], 0, flags=mmap.MAP_PRIVATE)
                assert mm[:] == out
