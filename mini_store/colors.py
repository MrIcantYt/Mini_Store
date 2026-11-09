import sys
from enum import StrEnum

_ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004


class Colors(StrEnum):
    red = '\033[31m'
    green = '\033[32m'
    yellow = '\033[33m'
    blue_dark = '\033[34m'
    blue = '\033[36m'
    purple = '\033[35m'
    reset = '\033[0m'


def enable_ansi() -> None:
    """Enable ANSI escape sequences in the Windows console."""
    if sys.platform != 'win32':
        return

    import ctypes

    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)
    mode = ctypes.c_uint32()

    if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        kernel32.SetConsoleMode(handle, mode.value | _ENABLE_VIRTUAL_TERMINAL_PROCESSING)
