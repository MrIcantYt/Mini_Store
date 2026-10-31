from dataclasses import fields

import pytest

import mini_store.player as player_module
from mini_store.player import (
    BOOL_FIELDS,
    GOLD_PER_XP,
    MAX_BALANCE,
    MAX_LEVEL,
    Converted,
    Player,
)


class TestBalance:
    def test_default_balance_is_zero(self, player: Player) -> None:
        assert player.balance == 0

    def test_balance_is_capped(self, player: Player) -> None:
        player.balance = MAX_BALANCE + 500

        assert player.balance == MAX_BALANCE

    def test_negative_balance_is_allowed(self, player: Player) -> None:
        player.balance = -100

        assert player.balance == -100


class TestProperties:
    def test_next_level_xp_needed(self, player: Player) -> None:
        player.lvl = 4

        assert player.next_lvl_xp_needed == 400

    def test_level_multiplier(self, player: Player) -> None:
        assert player.level_multiplier == 1.0

        player.lvl = 5

        assert player.level_multiplier == 1.4


class TestAddCoins:
    def test_adds_with_multipliers(self, player: Player) -> None:
        player.balance_multiplier = 2
        player.lvl = 2

        message = player.add_coins(100)

        assert player.balance == 220
        assert '220' in message

    def test_can_skip_multipliers(self, player: Player) -> None:
        player.balance_multiplier = 5
        player.lvl = 10

        player.add_coins(100, apply_multipliers=False)

        assert player.balance == 100

    def test_truncates_fractional_reward(self, player: Player) -> None:
        player.balance_multiplier = 2
        player.lvl = 2

        player.add_coins(5)

        assert player.balance == 11


class TestAddXp:
    def test_adds_xp(self, player: Player) -> None:
        message = player.add_xp(50)

        assert player.xp == 50
        assert '50' in message

    def test_applies_multipliers(self, player: Player) -> None:
        player.xp_multiplier = 2

        player.add_xp(50)

        assert player.xp == 0
        assert player.lvl == 2

    def test_levels_up_multiple_times(self, player: Player) -> None:
        player.add_xp(250)

        assert player.lvl == 2
        assert player.xp == 150

    def test_skips_multipliers(self, player: Player) -> None:
        player.xp_multiplier = 5

        player.add_xp(100, apply_multipliers=False)

        assert player.xp == 0
        assert player.lvl == 2

    def test_add_coins_and_xp(self, player: Player) -> None:
        message = player.add_coins_and_xp(coins=100, xp=100)

        assert player.balance == 110
        assert player.xp == 0
        assert player.lvl == 2
        assert '100' in message


class TestLevelUp:
    def test_returns_none_without_level_up(self, player: Player) -> None:
        assert player.check_level_up() is None
        assert player.lvl == 1

    def test_returns_none_at_max_level(self, player: Player) -> None:
        player.lvl = MAX_LEVEL
        player.xp = 10_000

        assert player.check_level_up() is None
        assert player.xp == 10_000

    def test_max_level_converts_xp_to_gold(self, player: Player) -> None:
        player.lvl = MAX_LEVEL - 1
        player.xp = (MAX_LEVEL - 1) * 100 + 500

        message = player.check_level_up()

        assert player.lvl == MAX_LEVEL
        assert player.xp == 0
        assert player.balance == 500 * GOLD_PER_XP
        assert message is not None
        assert 'МАКСИМАЛЬНОГО' in message

    def test_convert_without_xp(self, player: Player) -> None:
        assert player._convert_xp_to_gold() == Converted(0, 0)

    def test_convert_xp_to_gold(self, player: Player) -> None:
        player.xp = 500

        converted = player._convert_xp_to_gold()

        assert converted == Converted(500, 500 * GOLD_PER_XP)
        assert player.balance == 500 * GOLD_PER_XP
        assert player.xp == 0


class TestSerialization:
    def test_to_dict_uses_balance_key(self, player: Player) -> None:
        player.balance = 123

        data = player.to_dict()

        assert data['balance'] == 123
        assert '_balance' not in data
        assert data['id'] == 1

    def test_from_dict_round_trip(self, player: Player) -> None:
        player.balance = 123
        player.lvl = 7
        player.lucky_amulet = True
        player.mining_lvl = 3
        data = player.to_dict()

        restored = Player.from_dict(data)

        assert restored == player

    def test_to_row_omits_id(self, player: Player) -> None:
        row = player.to_row()

        assert 'id' not in row
        assert 'balance' in row
        assert len(row) == len(fields(Player)) - 1

    def test_bool_fields_are_preserved(self) -> None:
        data = Player(id=1).to_dict()
        for name in BOOL_FIELDS:
            data[name] = True

        restored = Player.from_dict(data)

        assert all(getattr(restored, name) is True for name in BOOL_FIELDS)


class TestLuck:
    @pytest.mark.parametrize(
        ('roll', 'potion', 'expected'),
        [
            (15, False, True),
            (16, False, False),
            (35, True, True),
            (36, True, False),
        ],
    )
    def test_check_luck(
        self,
        monkeypatch: pytest.MonkeyPatch,
        player: Player,
        roll: int,
        potion: bool,
        expected: bool,
    ) -> None:
        monkeypatch.setattr(player_module, 'randint', lambda _a, _b: roll)
        player.potion_luck = potion

        assert player.check_luck() is expected
