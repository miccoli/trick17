from trick17 import daemon


def test_booted():
    daemon.booted()


def test_notify():
    ret = daemon.notify("READY=1", "STATUS=running")
    assert ret is False


def test_listen_fds():
    assert len(daemon.listen_fds()) == 0
