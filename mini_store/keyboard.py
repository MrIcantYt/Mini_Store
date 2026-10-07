import sys
import time
from typing import Self

if sys.platform == 'win32':
    import msvcrt

    def _read_key() -> str | None:
        """Один символ без ожидания Enter. None, если ничего не нажато."""
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
        """Один символ без ожидания Enter. None, если ничего не нажато."""
        if not select.select([sys.stdin], [], [], 0)[0]:
            return None
        return sys.stdin.read(1)


class RawTerminal:
    """Контекстный менеджер: переводит терминал в raw-режим на Unix.

    На Windows ничего не делает (msvcrt и так работает без Enter).
    """

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
    """Проверяет, нажата ли клавиша `key` прямо сейчас.

    На Unix требует, чтобы терминал был в raw-режиме (см. RawTerminal).
    На Windows работает без подготовки.

    `interval` — если > 0, после проверки ждёт указанное время.
    Это защита от busy-wait: символ из stdin уже прочитан, повторно
    он не вернётся, но цикл может крутиться очень быстро.

    ВНИМАНИЕ: символ СЪЕДАЕТСЯ из stdin. Если вызвать is_pressed('q'),
    а потом input(), символ 'q' туда не попадёт. Это by design —
    мы прочитали его и обработали.
    """
    ch = _read_key()
    if ch is None:
        return False

    matched = ch.lower() == key.lower()

    if interval > 0:
        time.sleep(interval)

    return matched


def wait(key: str, *, poll: float = 0.05) -> None:
    """Блокирует поток, пока не будет нажата клавиша `key`.

    На Unix требует raw-режим (см. RawTerminal).

    `poll` — период опроса stdin. Меньше = отзывчивее, больше = меньше CPU.

    ВНИМАНИЕ: если терминал не в raw-режиме, функция будет ждать Enter,
    потому что stdin буферизуется построчно.
    """
    while True:
        if is_pressed(key):
            return
        time.sleep(poll)
