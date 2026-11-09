from datetime import date
from pathlib import Path

import pytest

from mini_store.db import JsonDataBase
from mini_store.exceptions import SignCheckError
from mini_store.models import DailyContext, Player


@pytest.fixture
def db(tmp_path: Path) -> JsonDataBase:
    db = JsonDataBase(tmp_path / 'game.json')
    db.init_db()
    return db


class TestJsonDataBase:
    def test_init_creates_file(self, tmp_path: Path) -> None:
        path = tmp_path / 'game.json'
        db = JsonDataBase(path)

        db.init_db()

        assert path.exists()
        assert db.get_all_players() == []

    def test_init_does_not_overwrite_existing_file(self, db: JsonDataBase) -> None:
        player = Player(id=1)
        db.save_player(player)

        db.init_db()

        assert db.get_all_players() == [player]

    def test_save_first_player(self, db: JsonDataBase) -> None:
        player = Player(id=1)
        player.balance = 500

        db.save_player(player)

        assert db.get_player_by_id(1) == player

    def test_save_updates_existing_player(self, db: JsonDataBase) -> None:
        player = Player(id=1)
        db.save_player(player)

        player.balance = 1000
        player.lvl = 3
        db.save_player(player)

        saved = db.get_player_by_id(1)
        assert saved is not None
        assert saved.balance == 1000
        assert saved.lvl == 3
        assert len(db.get_all_players()) == 1

    def test_save_adds_new_player(self, db: JsonDataBase) -> None:
        db.save_player(Player(id=1))
        db.save_player(Player(id=2))

        assert {p.id for p in db.get_all_players()} == {1, 2}

    def test_get_missing_player(self, db: JsonDataBase) -> None:
        assert db.get_player_by_id(42) is None

    def test_get_player_keeps_flags(self, db: JsonDataBase) -> None:
        player = Player(id=1)
        player.lucky_amulet = True
        player.business = True
        player.mining_lvl = 4
        db.save_player(player)

        saved = db.get_player_by_id(1)

        assert saved is not None
        assert saved.lucky_amulet is True
        assert saved.business is True
        assert saved.mining_lvl == 4

    def test_reset_player_returns_defaults(self, db: JsonDataBase) -> None:
        player = Player(id=1)
        player.balance = 500
        player.lvl = 10
        player.lucky_amulet = True

        reset = db.reset_player(player)

        assert reset is not player
        assert reset.id == 1
        assert reset.balance == 0
        assert reset.lvl == 1
        assert reset.lucky_amulet is False

    def test_detects_tampered_save(self, db: JsonDataBase) -> None:
        db.save_player(Player(id=1))
        path = Path(db.path)
        path.write_text('bad-sign\n{"players":[]}')

        with pytest.raises(SignCheckError):
            db.get_player_by_id(1)

    @pytest.mark.xfail(reason='TODO in next update')
    def test_daily_round_trip(self, db: JsonDataBase) -> None:
        daily = DailyContext(
            contract='Сыграть 3 раунда в Блекджек',
            target=3,
            progress=1,
            reward=150,
            last_update=date(2026, 11, 7),
            completed=False,
            discount_item_id=3,
        )

        # TODO
        db.save_daily(daily)  # ty: ignore[unresolved-attribute]

        assert db.get_daily() == daily  # ty: ignore[unresolved-attribute]
