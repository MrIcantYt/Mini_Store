from collections.abc import Callable

import pytest

import mini_store.games.routtle as routtle_module
from mini_store.context import GameContext
from mini_store.games.routtle import RouttleGame


class TestRouttle:
    def test_zero_win(
        self,
        feed_input: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 500
        game = RouttleGame(ctx)
        feed_input('100')
        monkeypatch.setattr(routtle_module, 'ask_option', lambda *a, **k: 'зеро')
        monkeypatch.setattr(routtle_module.random, 'randint', lambda _a, _b: 0)
        monkeypatch.setattr(routtle_module.time, 'sleep', lambda _s: None)

        game.play()

        assert ctx.player.balance == 4250
        assert ctx.player.xp == 150

    def test_color_win(
        self,
        feed_input: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 500
        game = RouttleGame(ctx)
        feed_input('100')
        monkeypatch.setattr(routtle_module, 'ask_option', lambda *a, **k: 'красное')
        monkeypatch.setattr(routtle_module.random, 'randint', lambda _a, _b: 2)
        monkeypatch.setattr(routtle_module.time, 'sleep', lambda _s: None)

        game.play()

        assert ctx.player.balance == 600
        assert ctx.player.xp == 30

    def test_loss(
        self,
        feed_input: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 500
        game = RouttleGame(ctx)
        feed_input('100')
        monkeypatch.setattr(routtle_module, 'ask_option', lambda *a, **k: 'красное')
        monkeypatch.setattr(routtle_module.random, 'randint', lambda _a, _b: 1)
        monkeypatch.setattr(routtle_module.time, 'sleep', lambda _s: None)

        game.play()

        assert ctx.player.balance == 400

    def test_all_in(
        self, feed_input: Callable[..., None], ctx: GameContext, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        ctx.player.balance = 500
        game = RouttleGame(ctx)
        feed_input('все')
        monkeypatch.setattr(routtle_module, 'ask_option', lambda *a, **k: 'зеро')
        monkeypatch.setattr(routtle_module.random, 'randint', lambda _a, _b: 0)
        monkeypatch.setattr(routtle_module.time, 'sleep', lambda _s: None)

        game.play()

        assert ctx.player.balance == 19_250

    @pytest.mark.parametrize('bet', ['abc', '0', '501'])
    def test_invalid_bets(
        self,
        feed_input: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
        bet: str,
    ) -> None:
        ctx.player.balance = 500
        game = RouttleGame(ctx)
        feed_input(bet)

        game.play()

        assert ctx.player.balance == 500
