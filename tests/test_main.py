import sys
import tomllib
from pathlib import Path

import pytest

from mini_store import __version__
from mini_store.__main__ import main


def test_version_flag(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, 'argv', ['mini-store', '--version'])

    main()

    assert capsys.readouterr().out.strip() == f'Mini-Store {__version__}'


def test_version_matches_pyproject() -> None:
    pyproject = Path(__file__).parent.parent / 'pyproject.toml'
    data = tomllib.loads(pyproject.read_text(encoding='utf-8'))

    assert data['project']['version'] == __version__
