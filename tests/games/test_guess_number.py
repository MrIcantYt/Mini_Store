import pytest

import mini_store.games.guess_number as guess_module
from mini_store.games.guess_number import GuessNumberGame, Levels
from mini_store.models import GameContext, Player


@pytest.fixture(autouse=True)
def silence_clear(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(guess_module, 'cls', lambda: None)


class TestGuessNumber:
    def test_levels(self) -> None:
        assert Levels.easy.to_range == 15
        assert Levels.easy.win_reward == 25
        assert Levels.middle.to_range == 25
        assert Levels.hard.win_reward == 75

    def test_win(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        game = GuessNumberGame(ctx)
        monkeypatch.setattr(guess_module, 'ask_option', lambda *_, **__: Levels.easy)
        monkeypatch.setattr(guess_module, 'ask_number', lambda *_, **__: 7)
        monkeypatch.setattr(guess_module, 'randint', lambda _a, _b: 7)
        monkeypatch.setattr(Player, 'check_luck', lambda _self: False)

        game.play()

        assert ctx.player.balance == 25
        assert ctx.player.xp == 25

    def test_lucky_ticket_adds_life(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        ctx.player.lucky_ticket = True
        game = GuessNumberGame(ctx)
        monkeypatch.setattr(guess_module, 'ask_option', lambda *_, **__: Levels.easy)
        monkeypatch.setattr(guess_module, 'ask_number', lambda *_, **__: 7)
        monkeypatch.setattr(guess_module, 'randint', lambda _a, _b: 7)
        monkeypatch.setattr(Player, 'check_luck', lambda _self: False)

        game.play()

        assert '+1' in capsys.readouterr().out

    def test_cancel_level_selection(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        game = GuessNumberGame(ctx)
        monkeypatch.setattr(guess_module, 'ask_option', lambda *_, **__: None)

        game.play()

        assert ctx.player.balance == 0
