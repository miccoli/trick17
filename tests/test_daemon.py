from trick17 import daemon


def test_booted():
    daemon.booted()


def test_notify():
    ret = daemon.notify("READY=1")
    assert ret is False
