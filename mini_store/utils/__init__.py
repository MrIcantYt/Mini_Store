from os import name as os_name
from subprocess import run

from .ask_functions import *


def fmt(value: int) -> str:
    return f'{value:,}'.replace(',', '.')


def cls() -> None:
    run('cls', shell=True, check=False) if os_name == 'nt' else run('clear', check=False)
