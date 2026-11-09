from collections.abc import Callable

import pytest

import mini_store.games.roulette as roulette_module
from mini_store.games.roulette import RouletteGame
from mini_store.models import GameContext


class TestRouttle:
    def test_zero_win(
        self,
        feed_input: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 500
        game = RouletteGame(ctx)
        feed_input('100')
        monkeypatch.setattr(roulette_module, 'ask_option', lambda *_, **__: 'зеро')
        monkeypatch.setattr(roulette_module.random, 'randint', lambda _a, _b: 0)
        monkeypatch.setattr(roulette_module.time, 'sleep', lambda _s: None)

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
        game = RouletteGame(ctx)
        feed_input('100')
        monkeypatch.setattr(roulette_module, 'ask_option', lambda *_, **__: 'красное')
        monkeypatch.setattr(roulette_module.random, 'randint', lambda _a, _b: 2)
        monkeypatch.setattr(roulette_module.time, 'sleep', lambda _s: None)

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
        game = RouletteGame(ctx)
        feed_input('100')
        monkeypatch.setattr(roulette_module, 'ask_option', lambda *_, **__: 'красное')
        monkeypatch.setattr(roulette_module.random, 'randint', lambda _a, _b: 1)
        monkeypatch.setattr(roulette_module.time, 'sleep', lambda _s: None)

        game.play()

        assert ctx.player.balance == 400

    def test_all_in(
        self, feed_input: Callable[..., None], ctx: GameContext, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        ctx.player.balance = 500
        game = RouletteGame(ctx)
        feed_input('все')
        monkeypatch.setattr(roulette_module, 'ask_option', lambda *_, **__: 'зеро')
        monkeypatch.setattr(roulette_module.random, 'randint', lambda _a, _b: 0)
        monkeypatch.setattr(roulette_module.time, 'sleep', lambda _s: None)

        game.play()

        assert ctx.player.balance == 19_250

    @pytest.mark.parametrize('bet', ['abc', '0', '501'])
    def test_invalid_bets(
        self,
        feed_input: Callable[..., None],
        ctx: GameContext,
        bet: str,
    ) -> None:
        ctx.player.balance = 500
        game = RouletteGame(ctx)
        feed_input(bet)

        game.play()

        assert ctx.player.balance == 500
