from __future__ import annotations

import pytest

from mini_store.context import Daily, GameContext
from mini_store.db import AbstractDataBase
from mini_store.player import Player


class FakeDB(AbstractDataBase):
    def __init__(self) -> None:
        self.path = ':memory:'
        self.saved: list[Player] = []
        self.resets = 0

    def init_db(self) -> None:
        pass

    def save_player(self, player: Player) -> None:
        self.saved.append(player)

    def reset_player(self, player: Player) -> Player:
        self.resets += 1
        return Player(id=player.id)

    def get_player_by_id(self, player_id: int) -> Player | None:
        return next((p for p in self.saved if p.id == player_id), None)

    def get_all_players(self) -> list[Player]:
        return list(self.saved)


@pytest.fixture
def player() -> Player:
    return Player(id=1)


@pytest.fixture
def ctx(player: Player) -> GameContext:
    return GameContext(player=player, db=FakeDB(), daily=Daily())
