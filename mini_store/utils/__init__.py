from os import name as os_name
from subprocess import run

from .ask_functions import *


def fmt(value: int) -> str:
    return f'{value:,}'.replace(',', '.')


def cls() -> None:
    if os_name == 'nt':
        run('cls', shell=True, check=False)
    else:
        run('clear', check=False)


def confirm(prompt: str) -> bool:
    return 'д' in input(prompt + '\n[Да/Нет]: ')
