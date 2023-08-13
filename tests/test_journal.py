import logging
import syslog

import pytest

from trick17 import journal


def test_broken_handler(tmp_path):
    """Test error returns when JournalHandler is instantiated but
    JournalHandler.SADRR points to an invalid socket.

    Instead of monkey patching JournalHandler we subclass it locally with
    BrokenHandler, and test the given error conditions"""
    test_path = tmp_path / "socket"

    class BrokenHandler(journal.JournalHandler):
        SADDR = str(test_path)

    with pytest.raises(RuntimeError, match="^Nonexistent journal socket"):
        BrokenHandler()

    test_path.touch()
    with pytest.raises(RuntimeError, match="not a socket$"):
        BrokenHandler()

    test_path.chmod(0)
    with pytest.raises(RuntimeError, match="^Not writable journal socket"):
        BrokenHandler()


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

    root.info("Very long message:\n" + "A" * 2**18)


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
