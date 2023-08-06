import logging
import syslog

import pytest

from trick17.journal import JournalHandler


def test_basic():
    handler = JournalHandler()

    root = logging.getLogger()
    root.addHandler(handler)

    root.setLevel(logging.DEBUG)

    root.debug("debug")
    root.info("info")
    root.warning("warning")
    root.error("error")
    root.critical("critical")

    root.info("Multiline\nmessage")

    with pytest.raises(RuntimeError):
        root.info("A" * 2**18)

    handler.SADDR = "/notexistent"
    with pytest.raises(FileNotFoundError):
        root.info("test")


def test_level():
    mapper = JournalHandler._log_level

    assert mapper(logging.CRITICAL) == syslog.LOG_CRIT
    assert mapper(logging.ERROR) == syslog.LOG_ERR
    assert mapper(logging.WARNING) == syslog.LOG_WARNING
    assert mapper(logging.INFO) == syslog.LOG_INFO
    assert mapper(logging.DEBUG) == syslog.LOG_DEBUG
    with pytest.raises(ValueError):
        mapper(logging.NOTSET)
