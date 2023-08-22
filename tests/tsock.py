#!/usr/bin/env python

import logging
import os
import socket
import stat

from trick17 import daemon

LISTEN_FDS_START = 3

logging.basicConfig(level=logging.INFO)
for fd, name in daemon.listen_fds():
    fstat = os.fstat(fd)
    if not stat.S_ISSOCK(fstat.st_mode):
        logging.error("fd %d ('%s') not a socket", fd, name)
        continue
    with socket.socket(fileno=fd) as sock:
        logging.info("fd %d ('%s') bound to '%s'", fd, name, sock.getsockname())
        if sock.type == socket.SOCK_STREAM:
            while True:
                conn, address = sock.accept()
                logging.info("   remote '%s'", address)
                with conn:
                    data = conn.recv(4096)
                    logging.info("   -> %s", data)
                    if data.startswith(b"STOP"):
                        break
        elif sock.type == socket.SOCK_DGRAM:
            while True:
                data = sock.recv(4096)
                logging.info("   -> %s", data)
                if data.startswith(b"STOP"):
                    break
        else:
            msg = f"Unknown socket type {sock.type}"
            raise NotImplementedError(msg)
