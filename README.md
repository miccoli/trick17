# trick17

[![Pre-Alpha warning](https://img.shields.io/badge/warning-Pre--Alpha%20code-red)]()

[![PyPI - Version](https://img.shields.io/pypi/v/trick17.svg)](https://pypi.org/project/trick17)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/trick17.svg)](https://pypi.org/project/trick17)

`trick17` is a pure python, lightweight package that interfaces with various [systemd](https://systemd.io) components.

-----

**Table of Contents**

- [Installation](#installation)
- [Modules](#modules)
- [License](#license)

## Installation

```console
pip install trick17
```

## Modules

### trick17.daemon

- `daemon.booted()` returns `True` if system was booted by systemd.
- `daemon.notify(state)` sends a notification to systemd.

### trick17.journal

The `trick17.journal` allows to use the systemd [Native Journal Protocol](https://systemd.io/JOURNAL_NATIVE_PROTOCOL/) via the Python [Logging facility](https://docs.python.org/3/library/logging.html).

- `JournalHandler` is a [`logging.Handler`](https://docs.python.org/3/library/logging.html#logging.Handler) subclass that speaks the systemd Native Journal Protocol
- Function `stderr_is_journal()` can be used to check if logging via `sys.stderr` should be upgraded to native logging, see [Automatic Protocol Upgrading](https://systemd.io/JOURNAL_NATIVE_PROTOCOL/#automatic-protocol-upgrading)

```python
import logging

from trick17 import journal

if journal.stderr_is_journal():
    handler = journal.JournalHandler()
else:
    handler = logging.StreamHandler()
root = logging.getLogger()
root.addHandler(handler)

logging.error('Something happened')
```

## License

`trick17` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
