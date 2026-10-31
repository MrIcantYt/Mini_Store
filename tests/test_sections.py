from datetime import UTC, date, datetime
from typing import Self

import pytest
from conftest import FakeDB

from mini_store import sections
from mini_store.context import GameContext


@pytest.fixture(autouse=True)
def silence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sections, 'cls', lambda: None)
    monkeypatch.setattr(sections, 'wait', lambda _key, **_kwargs: None)


def feed_input(monkeypatch: pytest.MonkeyPatch, *values: str) -> None:
    iterator = iter(values)
    monkeypatch.setattr('builtins.input', lambda _prompt='': next(iterator))


class TestProfile:
    def test_lists_empty_inventory(
        self,
        ctx: GameContext,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        sections.profile(ctx)

        output = capsys.readouterr().out
        assert 'ПРОФИЛЬ ИГРОКА' in output
        assert 'Рюкзак пуст' in output

    def test_lists_bought_items(
        self,
        ctx: GameContext,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        ctx.player.lucky_amulet = True
        ctx.player.potion_luck = True
        ctx.player.lucky_ticket = True
        ctx.player.mining_lvl = 3
        ctx.player.mining_multiplier = 2
        ctx.player.business = True

        sections.profile(ctx)

        output = capsys.readouterr().out
        assert 'Счастливый Амулет' in output
        assert 'Зелье Удачи' in output
        assert 'Счастливый Тикет' in output
        assert 'Майнинг-ферма' in output
        assert 'Кофе ускорил' in output
        assert 'Пассивный бизнес' in output

    def test_quest_one_completed(self, ctx: GameContext) -> None:
        ctx.player.balance = 500

        sections.profile(ctx)

        assert ctx.player.quest_id == 2
        assert ctx.player.lvl == 2

    def test_quest_one_not_completed(self, ctx: GameContext) -> None:
        ctx.player.balance = 100

        sections.profile(ctx)

        assert ctx.player.quest_id == 1

    def test_quest_two_completed(self, ctx: GameContext) -> None:
        ctx.player.quest_id = 2
        ctx.player.mining_lvl = 3

        sections.profile(ctx)

        assert ctx.player.quest_id == 3
        assert ctx.player.balance == 1000

    def test_quest_three_completed(self, ctx: GameContext) -> None:
        ctx.player.quest_id = 3
        ctx.player.quest_progress = 5

        sections.profile(ctx)

        assert ctx.player.quest_id == 4
        assert ctx.player.quest_progress == 0
        assert ctx.player.balance == 600
        assert ctx.player.lvl == 3

    def test_all_quests_completed(
        self,
        ctx: GameContext,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        ctx.player.quest_id = 4

        sections.profile(ctx)

        assert 'Контракты закончились' in capsys.readouterr().out


class TestMining:
    def test_mining_without_farm(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        monkeypatch.setattr(sections.time, 'sleep', lambda _seconds: None)

        sections.mining(ctx)

        assert ctx.player.balance == 0
        assert 'Сначала купите ферму' in capsys.readouterr().out

    def test_mining_adds_coins(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.mining_lvl = 2
        monkeypatch.setattr(sections.time, 'sleep', lambda _seconds: None)
        monkeypatch.setattr(sections, 'is_pressed', lambda _key: True)

        sections.mining(ctx)

        assert ctx.player.balance == 2

    def test_mining_speed_does_not_crash(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.mining_lvl = 1
        ctx.player.mining_multiplier = 2
        monkeypatch.setattr(sections.time, 'sleep', lambda _seconds: None)
        monkeypatch.setattr(sections, 'is_pressed', lambda _key: True)

        sections.mining(ctx)

        assert ctx.player.balance == 1


class TestPromocode:
    def test_valid_promocode(
        self, ctx: GameContext, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        feed_input(monkeypatch, sections.PROMO)

        sections.promocode(ctx)

        assert ctx.player.promo_used is True
        assert ctx.player.balance == 50
        assert ctx.player.xp == 30

    def test_invalid_promocode(
        self, ctx: GameContext, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        feed_input(monkeypatch, 'wrong')

        sections.promocode(ctx)

        assert ctx.player.promo_used is False
        assert ctx.player.balance == 0

    def test_promocode_is_stripped(
        self, ctx: GameContext, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        feed_input(monkeypatch, f'  {sections.PROMO}  ')

        sections.promocode(ctx)

        assert ctx.player.promo_used is True


class TestEasterEgg:
    def test_first_activation(self, ctx: GameContext) -> None:
        sections.easter_egg(ctx)

        assert ctx.player.secret_used is True
        assert ctx.player.balance == 100

    def test_second_activation_gives_nothing(self, ctx: GameContext) -> None:
        ctx.player.secret_used = True

        sections.easter_egg(ctx)

        assert ctx.player.balance == 0


class TestReset:
    def test_reset_confirmed(
        self,
        ctx: GameContext,
        db: FakeDB,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        old_player = ctx.player
        old_player.balance = 500
        monkeypatch.setattr(sections, 'ask_confirmation', lambda _prompt: True)
        monkeypatch.setattr(sections.time, 'sleep', lambda _seconds: None)

        sections.reset(ctx)

        assert ctx.player is not old_player
        assert ctx.player.balance == 0
        assert db.resets == 1

    def test_reset_cancelled(
        self,
        ctx: GameContext,
        db: FakeDB,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(sections, 'ask_confirmation', lambda _prompt: False)

        sections.reset(ctx)

        assert db.resets == 0


class TestDebugMenu:
    def test_add_coins(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(sections, 'ask_option', lambda *a, **k: 1)
        monkeypatch.setattr(sections, 'ask_number', lambda *a, **k: 100)

        sections.debug_menu(ctx)

        assert ctx.player.balance == 100

    def test_add_xp(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(sections, 'ask_option', lambda *a, **k: 2)
        monkeypatch.setattr(sections, 'ask_number', lambda *a, **k: 100)

        sections.debug_menu(ctx)

        assert ctx.player.lvl == 2

    def test_set_level(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(sections, 'ask_option', lambda *a, **k: 3)
        monkeypatch.setattr(sections, 'ask_number', lambda *a, **k: 42)

        sections.debug_menu(ctx)

        assert ctx.player.lvl == 42

    def test_cancel(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(sections, 'ask_option', lambda *a, **k: None)

        sections.debug_menu(ctx)

        assert ctx.player.balance == 0


class TestBank:
    def test_deposit_all(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 500
        monkeypatch.setattr(sections, 'ask_option', lambda *a, **k: 1)
        feed_input(monkeypatch, 'all')

        sections.bank_menu(ctx)

        assert ctx.player.balance == 0
        assert ctx.player.bank_deposit == 500

    def test_deposit_amount(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 500
        monkeypatch.setattr(sections, 'ask_option', lambda *a, **k: 1)
        feed_input(monkeypatch, '200')

        sections.bank_menu(ctx)

        assert ctx.player.balance == 300
        assert ctx.player.bank_deposit == 200

    def test_deposit_invalid_amount(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 500
        monkeypatch.setattr(sections, 'ask_option', lambda *a, **k: 1)
        feed_input(monkeypatch, '9999')

        sections.bank_menu(ctx)

        assert ctx.player.balance == 500
        assert ctx.player.bank_deposit == 0

    def test_deposit_invalid_input(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 500
        monkeypatch.setattr(sections, 'ask_option', lambda *a, **k: 1)
        feed_input(monkeypatch, 'abc')

        sections.bank_menu(ctx)

        assert ctx.player.balance == 500

    def test_withdraw(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.bank_deposit = 300
        ctx.player.bank_turns = 2
        monkeypatch.setattr(sections, 'ask_option', lambda *a, **k: 2)

        sections.bank_menu(ctx)

        assert ctx.player.balance == 300
        assert ctx.player.bank_deposit == 0
        assert ctx.player.bank_turns == 0

    def test_withdraw_without_deposit(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(sections, 'ask_option', lambda *a, **k: 2)

        sections.bank_menu(ctx)

        assert ctx.player.balance == 0

    def test_cancel(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(sections, 'ask_option', lambda *a, **k: None)

        sections.bank_menu(ctx)

        assert ctx.player.balance == 0


class FakeDateTime(datetime):
    @classmethod
    def now(cls, tz=None) -> Self:
        return cls(2026, 1, 1, 12, 0, tzinfo=tz or UTC)


class TestTimeUntilMidnight:
    def test_formats_hours_and_minutes(self) -> None:
        now = datetime(2026, 1, 1, 22, 30, tzinfo=UTC)

        assert sections._time_until_midnight(now) == ' 1ч 30м'

    def test_less_than_an_hour(self) -> None:
        now = datetime(2026, 1, 1, 23, 45, tzinfo=UTC)

        assert sections._time_until_midnight(now) == ' 0ч 15м'

    def test_exactly_midnight(self) -> None:
        now = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)

        assert sections._time_until_midnight(now) == '24ч 00м'


class TestMerchantContracts:
    def test_creates_new_contract(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        monkeypatch.setattr(sections, 'datetime', FakeDateTime)
        monkeypatch.setattr(sections.random, 'choice', lambda items: items[0])
        monkeypatch.setattr(sections.random, 'randint', lambda _a, _b: 5)
        feed_input(monkeypatch, '')

        sections.merchant_contracts(ctx)

        assert ctx.daily.contract == 'Сыграть 5 раундов в Блекджек'
        assert ctx.daily.target == 5
        assert ctx.daily.progress == 0
        assert ctx.daily.reward == 750
        assert ctx.daily.last_update == date(2026, 1, 1)
        assert ctx.daily.completed is False
        assert 'обновил ассортимент' in capsys.readouterr().out

    def test_keeps_contract_for_the_same_day(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.daily.contract = 'Старый контракт'
        ctx.daily.target = 5
        ctx.daily.last_update = date(2026, 1, 1)
        monkeypatch.setattr(sections, 'datetime', FakeDateTime)
        feed_input(monkeypatch, '')

        sections.merchant_contracts(ctx)

        assert ctx.daily.contract == 'Старый контракт'

    def test_claims_reward(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.daily.contract = 'Сыграть 5 раундов в Блекджек'
        ctx.daily.target = 5
        ctx.daily.progress = 5
        ctx.daily.reward = 750
        ctx.daily.last_update = date(2026, 1, 1)
        ctx.daily.completed = False
        monkeypatch.setattr(sections, 'datetime', FakeDateTime)
        monkeypatch.setattr(sections, 'ask_confirmation', lambda _prompt: True)
        feed_input(monkeypatch, '')

        sections.merchant_contracts(ctx)

        assert ctx.daily.completed is True
        assert ctx.player.balance == 750

    def test_does_not_claim_twice(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.daily.contract = 'Сыграть 5 раундов в Блекджек'
        ctx.daily.target = 5
        ctx.daily.progress = 5
        ctx.daily.reward = 750
        ctx.daily.last_update = date(2026, 1, 1)
        ctx.daily.completed = True
        monkeypatch.setattr(sections, 'datetime', FakeDateTime)
        feed_input(monkeypatch, '')

        sections.merchant_contracts(ctx)

        assert ctx.player.balance == 0

    def test_no_reward_before_completion(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.daily.contract = 'Сыграть 5 раундов в Блекджек'
        ctx.daily.target = 5
        ctx.daily.progress = 2
        ctx.daily.reward = 750
        ctx.daily.last_update = date(2026, 1, 1)
        monkeypatch.setattr(sections, 'datetime', FakeDateTime)
        feed_input(monkeypatch, '')

        sections.merchant_contracts(ctx)

        assert ctx.daily.completed is False
        assert ctx.player.balance == 0


class TestGame:
    def test_starts_selected_game(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        events: list[str] = []

        class FakeGame:
            def __init__(self, game_ctx: GameContext) -> None:
                events.append('init')
                assert game_ctx is ctx

            def play(self) -> None:
                events.append('play')

        monkeypatch.setattr(sections, 'ask_option', lambda *a, **k: FakeGame)

        sections.game(ctx)

        assert events == ['init', 'play']

    def test_cancel(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(sections, 'ask_option', lambda *a, **k: None)

        sections.game(ctx)


class TestExitAndDelegation:
    def test_game_exit_saves_and_exits(
        self,
        ctx: GameContext,
        db: FakeDB,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        with pytest.raises(SystemExit):
            sections.game_exit(ctx)

        assert db.saved == [ctx.player]
        assert 'Прогресс сохранен' in capsys.readouterr().out

    def test_shop_delegates_to_shop_class(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        opened: list[GameContext] = []

        class FakeShop:
            def __init__(self, shop_ctx: GameContext) -> None:
                self.ctx = shop_ctx

            def open(self) -> None:
                opened.append(self.ctx)

        monkeypatch.setattr(sections, 'Shop', FakeShop)

        sections.shop(ctx)

        assert opened == [ctx]


def test_promo_constant() -> None:
    assert sections.PROMO == 'MrIcant'
