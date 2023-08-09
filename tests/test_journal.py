import logging
import syslog

import pytest

from trick17 import journal


def test_handler():
    handler = journal.JournalHandler()

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
    mapper = journal.JournalHandler._log_level

    assert mapper(logging.CRITICAL) == syslog.LOG_CRIT
    assert mapper(logging.ERROR) == syslog.LOG_ERR
    assert mapper(logging.WARNING) == syslog.LOG_WARNING
    assert mapper(logging.INFO) == syslog.LOG_INFO
    assert mapper(logging.DEBUG) == syslog.LOG_DEBUG
    with pytest.raises(ValueError):
        mapper(logging.NOTSET)


def test_stderr():
    journal.stderr_is_journal()
