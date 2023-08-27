#!/usr/bin/env python
import sys

from trick17 import daemon


def main():
    ok = daemon.notify("READY=1", "STATUS=notified")
    if ok:
        sys.exit(0)
    else:
        sys.exit("Unable to send notification")


if __name__ == "__main__":
    main()
