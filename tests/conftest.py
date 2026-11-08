import subprocess
from pathlib import Path

import pytest

import mini_store.utils
from mini_store.db import AbstractDataBase
from mini_store.models import DailyContext, GameContext, Player


class FakeDB(AbstractDataBase):
    def __init__(self) -> None:
        self.path = Path(':memory:')
        self.saved: list[Player] = []
        self.resets = 0

    def init_db(self) -> None:
        pass

    def save_player(self, player: Player) -> None:
        self.saved.append(player)

    def reset(self):
        pass

    def reset_player(self, player: Player) -> Player:
        self.resets += 1
        return Player(id=player.id)

    def get_player_by_id(self, player_id: int) -> Player | None:
        return next((p for p in self.saved if p.id == player_id), None)

    def get_all_players(self) -> list[Player]:
        return list(self.saved)


@pytest.fixture
def db() -> FakeDB:
    return FakeDB()


@pytest.fixture
def player() -> Player:
    return Player(id=1)


@pytest.fixture
def ctx(player: Player, db: FakeDB) -> GameContext:
    return GameContext(player=player, db=db, daily=DailyContext())


@pytest.fixture(autouse=True)
def disable_clear_screen(monkeypatch):
    def fake_run(*args, **kwargs):
        cmd = args[0] if args else kwargs.get('args', '')
        if isinstance(cmd, str) and cmd.lower() in ('cls', 'clear'):
            return subprocess.CompletedProcess(args, returncode=0)

        return original_run(*args, **kwargs)

    original_run = subprocess.run

    monkeypatch.setattr(mini_store.utils, 'run', fake_run)
