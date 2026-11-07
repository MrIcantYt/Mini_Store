import sys

import pytest

from mini_store.__main__ import main
from mini_store.config import config


def test_version_flag(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(sys, 'argv', ['mini-store', '--version'])

    main()

    assert capsys.readouterr().out.strip() == f'Mini-Store {config.version}'
