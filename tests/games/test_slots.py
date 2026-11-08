from collections.abc import Callable

import pytest

import mini_store.games.slots as slots_module
from mini_store.games.slots import Slot, SlotsGame
from mini_store.models import GameContext


class TestSlots:
    def test_slot_symbols(self) -> None:
        assert str(Slot.SEVEN) == '7'
        assert str(Slot.SACK_MONEY) == '💰'

    def test_three_equal_slots(self, ctx: GameContext) -> None:
        game = SlotsGame(ctx)
        game._slots = [Slot.CHERRY, Slot.CHERRY, Slot.CHERRY]

        assert game._all_slots_is() is Slot.CHERRY

    def test_different_slots(self, ctx: GameContext) -> None:
        game = SlotsGame(ctx)
        game._slots = [Slot.CHERRY, Slot.CHERRY, Slot.SEVEN]

        assert game._all_slots_is() is None

    def test_variants_without_potion(self, ctx: GameContext) -> None:
        game = SlotsGame(ctx)

        assert len(game._setup_variants()) == 8

    def test_variants_with_potion(self, ctx: GameContext) -> None:
        ctx.player.potion_luck = True
        game = SlotsGame(ctx)

        assert len(game._setup_variants()) == 12

    def test_win_pays_reward(
        self,
        feed_input: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = SlotsGame(ctx)
        game._slots = [Slot.CHERRY, Slot.CHERRY, Slot.CHERRY]
        feed_input('100')
        monkeypatch.setattr(slots_module, 'sleep', lambda _seconds: None)

        game.play()

        assert ctx.player.balance == 1100
        assert ctx.player.xp == 20

    def test_invalid_bet_does_not_change_balance(
        self,
        feed_input: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = SlotsGame(ctx)
        feed_input('abc')

        game.play()

        assert ctx.player.balance == 1000

    def test_bet_above_balance(
        self, feed_input: Callable[..., None], ctx: GameContext, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        ctx.player.balance = 100
        game = SlotsGame(ctx)
        feed_input('500')

        game.play()

        assert ctx.player.balance == 100

    def test_vip_bet(
        self,
        feed_input: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 2000
        game = SlotsGame(ctx)
        game._slots = [Slot.CHERRY, Slot.CHERRY, Slot.CHERRY]
        feed_input('777')
        monkeypatch.setattr(slots_module, 'sleep', lambda _seconds: None)

        game.play()

        assert ctx.player.balance == 4331
        assert ctx.player.xp == 40

    def test_quest_progress(
        self, feed_input: Callable[..., None], ctx: GameContext, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        ctx.player.quest_id = 3
        ctx.player.balance = 100
        game = SlotsGame(ctx)
        feed_input('10')
        monkeypatch.setattr(slots_module, 'sleep', lambda _seconds: None)

        game.play()

        assert ctx.player.quest_progress == 1

    def test_quest_does_not_progress_on_invalid_bet(
        self,
        feed_input: Callable[..., None],
        ctx: GameContext,
    ) -> None:
        ctx.player.quest_id = 3
        ctx.player.balance = 100
        game = SlotsGame(ctx)
        feed_input('abc')

        game.play()

        assert ctx.player.quest_progress == 0

    def test_vip_with_777_and_balance_1000(
        self,
        feed_input: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = SlotsGame(ctx)
        game._slots = [Slot.CHERRY, Slot.CHERRY, Slot.CHERRY]
        feed_input('777')
        monkeypatch.setattr(slots_module, 'sleep', lambda _seconds: None)

        game.play()

        assert game._is_vip is True
        assert ctx.player.balance == 3331
