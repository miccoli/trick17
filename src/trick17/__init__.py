# SPDX-FileCopyrightText: 2023-present Stefano Miccoli <stefano.miccoli@polimi.it>
#
# SPDX-License-Identifier: MIT

# systemd notable paths
SD_BOOTED_PATH = "/run/systemd/system"
SD_JOURNAL_SOCKET_PATH = "/run/systemd/journal/socket"
SD_LISTEN_FDS_START = 3

# environmet variables possibly set by systemd
SD_JOURNAL_STREAM_ENV = "JOURNAL_STREAM"
SD_NOTIFY_SOCKET_ENV = "NOTIFY_SOCKET"
SD_LISTEN_FDS_PID_ENV = "LISTEN_PID"
SD_LISTEN_FDS_ENV = "LISTEN_FDS"
SD_LISTEN_FDS_NAMES_ENV = "LISTEN_FDNAMES"
