import sys
import time

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

    def _read_key() -> str | None:
        if not select.select([sys.stdin], [], [], 0)[0]:
            return None

        return sys.stdin.read(1)


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
