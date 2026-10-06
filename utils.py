__all__ = ('ask_number', 'clear_console', 'confirm', 'fmt')

import os
import subprocess

from colors import Colors


def fmt(value: int) -> str:
    return f'{value:,}'.replace(',', '.')


def clear_console() -> None:
    subprocess.run('cls' if os.name == 'nt' else 'clear', check=False)


def confirm(prompt: str) -> bool:
    return 'д' in input(prompt + ' [да/нет]')


def ask_number(
    prompt: str,
    *,
    min: int = 1,
    max: int | None = None,
    allow_cancel: bool = False,
    cancel_on: str = 'q',
) -> int | None:
    """Читает целое число с проверкой границ.

    Возвращает None, если allow_cancel=True и пользователь ввёл 'q'/'отмена'.
    """
    while True:
        raw = input(prompt).strip().lower()

        if allow_cancel and raw == cancel_on:
            return None

        try:
            value = int(raw)
        except ValueError:
            print(f'{Colors.red}Не число: {raw!r}{Colors.reset}')
            continue

        if min is not None and value < min:
            print(f'{Colors.red}Минимум: {min}{Colors.reset}')
            continue
        if max is not None and value > max:
            print(f'{Colors.red}Максимум: {max}{Colors.reset}')
            continue

        return value
