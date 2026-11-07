from collections.abc import Callable

import pytest

import mini_store.games.craps as craps_module
from mini_store.context import GameContext
from mini_store.games.craps import CrapsGame


class TestCraps:
    def test_roll_dice(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        game = CrapsGame(ctx)
        monkeypatch.setattr(craps_module.random, 'choices', lambda _population, k: [3, 4])
        monkeypatch.setattr(craps_module, 'sleep', lambda _s: None)

        assert game._roll_dice_get_total() == 7

    def test_natural_win(
        self,
        feed_input: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = CrapsGame(ctx)
        feed_input('100', '')
        monkeypatch.setattr(game, '_roll_dice_get_total', lambda: 7)

        game.play()

        assert ctx.player.balance == 1050
        assert ctx.player.xp == 25

    def test_craps_loss(
        self,
        feed_input: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = CrapsGame(ctx)
        feed_input('100', '')
        monkeypatch.setattr(game, '_roll_dice_get_total', lambda: 2)

        game.play()

        assert ctx.player.balance == 900

    def test_surrender_refunds_half(
        self,
        feed_input: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = CrapsGame(ctx)
        feed_input('100', '')
        monkeypatch.setattr(game, '_roll_dice_get_total', lambda: 5)
        monkeypatch.setattr(craps_module, 'ask_confirmation', lambda _prompt: False)

        game.play()

        assert ctx.player.balance == 950

    def test_point_win(
        self,
        feed_input: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = CrapsGame(ctx)
        feed_input('100', '')
        rolls = iter([5, 5])
        monkeypatch.setattr(game, '_roll_dice_get_total', lambda: next(rolls))
        monkeypatch.setattr(craps_module, 'ask_confirmation', lambda _prompt: True)

        game.play()

        assert ctx.player.balance == 1050

    @pytest.mark.parametrize('bet', ['abc', '0', '5000'])
    def test_invalid_bets(
        self,
        feed_input: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
        bet: str,
    ) -> None:
        ctx.player.balance = 1000
        game = CrapsGame(ctx)
        feed_input(bet)

        game.play()

        assert ctx.player.balance == 1000
