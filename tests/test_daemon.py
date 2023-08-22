import pytest

from trick17 import daemon


def test_booted():
    daemon.booted()


def test_notify():
    ret = daemon.notify("READY=1")
    assert ret is False


def test_listen_fds():
    with pytest.raises(StopIteration):
        next(daemon.listen_fds())
