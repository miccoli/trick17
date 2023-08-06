# trick17

[![PyPI - Version](https://img.shields.io/pypi/v/trick17.svg)](https://pypi.org/project/trick17)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/trick17.svg)](https://pypi.org/project/trick17)

`trick17` is a pure python lightweight packages that interfaces with various [systemd](https://systemd.io) components.

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

- `trick17.journal` implements `JournalHandler`, a [`logging.Handler`](https://docs.python.org/3/library/logging.html#logging.Handler) subclass that speaks the systemd [Native Journal Protocol](https://systemd.io/JOURNAL_NATIVE_PROTOCOL/).
  ```python
  import logging
  from trick17.journal import JournalHandler

  handler = JournalHandler()
  root = logging.getLogger()
  root.addHandler(handler)

  logging.error('Something happened')
  ```

## License

`trick17` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
