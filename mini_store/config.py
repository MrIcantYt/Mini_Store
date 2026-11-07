__all__ = ('config',)

from pathlib import Path
from sys import argv
from tomllib import loads
from typing import ClassVar, Final

_PYPROJECT = Path(__file__).parent.parent / 'pyproject.toml'


def _read_version() -> str:
    data = loads(_PYPROJECT.read_text(encoding='utf-8'))
    return data['project']['version']


class Config:
    version: ClassVar[str] = _read_version()
    is_debug: ClassVar[bool] = '-d' in argv


config: Final[Config] = Config()
