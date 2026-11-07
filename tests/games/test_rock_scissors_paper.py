from collections.abc import Callable

import pytest

import mini_store.games.rock_scissors_paper as rsp_module
from mini_store.context import GameContext
from mini_store.games.rock_scissors_paper import RockScissorsPaperGame


class TestRockScissorsPaper:
    def test_win(
        self,
        feed_input: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        game = RockScissorsPaperGame(ctx)
        feed_input('камень')
        monkeypatch.setattr(rsp_module.random, 'choice', lambda _items: 'ножницы')
        monkeypatch.setattr(rsp_module.random, 'randint', lambda _a, _b: 50)

        game.play()

        assert ctx.player.balance == 25

    def test_potion_increases_critical_chance(
        self,
        feed_input: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.potion_luck = True
        game = RockScissorsPaperGame(ctx)
        feed_input('камень')
        monkeypatch.setattr(rsp_module.random, 'choice', lambda _items: 'ножницы')
        monkeypatch.setattr(rsp_module.random, 'randint', lambda _a, _b: 20)

        game.play()

        assert ctx.player.balance == 50

    def test_invalid_choice_reprompts(
        self,
        feed_input: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        game = RockScissorsPaperGame(ctx)
        feed_input('invalid', 'камень')
        monkeypatch.setattr(rsp_module.random, 'choice', lambda _items: 'ножницы')
        monkeypatch.setattr(rsp_module.random, 'randint', lambda _a, _b: 50)

        game.play()

        assert ctx.player.balance == 25
