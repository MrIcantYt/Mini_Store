import sys
import time
from typing import Self

if sys.platform == 'win32':
    import msvcrt

    def _read_key() -> str | None:
        if not msvcrt.kbhit():
            return None

        ch = msvcrt.getwch()

        if ch in ('\x00', '\xe0'):
            msvcrt.getwch()
            return ''

        return ch

else:
    import select
    import termios
    import tty

    def _read_key() -> str | None:
        if not select.select([sys.stdin], [], [], 0)[0]:
            return None

        return sys.stdin.read(1)

    class RawTerminal:
        def __init__(self) -> None:
            self._fd: int | None = None
            self._old_settings = None

        def __enter__(self) -> Self:
            if sys.platform != 'win32':
                self._fd = sys.stdin.fileno()
                self._old_settings = termios.tcgetattr(self._fd)
                tty.setcbreak(self._fd)

            return self

        def __exit__(self, *exc) -> None:
            if self._fd is not None and self._old_settings is not None:
                termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old_settings)


def is_pressed(key: str, *, interval: float = 0.0) -> bool:
    ch = _read_key()

    if ch is None:
        return False

    matched = ch.lower() == key.lower()

    if interval > 0:
        time.sleep(interval)

    return matched


def wait(key: str, *, poll: float = 0.05) -> None:
    while True:
        if is_pressed(key):
            return

        time.sleep(poll)
