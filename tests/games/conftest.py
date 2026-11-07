from collections.abc import Callable

import pytest

import mini_store.games.blackjack as blackjack_module


@pytest.fixture
def feed_input(monkeypatch: pytest.MonkeyPatch) -> Callable[..., None]:
    """Return a helper that feeds the given values to `input` one by one."""

    def feed(*values: str) -> None:
        iterator = iter(values)
        monkeypatch.setattr('builtins.input', lambda _prompt='': next(iterator))

    return feed


@pytest.fixture
def set_blackjack_cards(monkeypatch: pytest.MonkeyPatch) -> Callable[..., None]:
    """Return a helper that fixes the cards dealt in a blackjack round."""

    def setup(
        player_cards: list[int],
        bot_cards: list[int],
        *extra_hands: list[int],
        draws: tuple[int, ...] = (),
    ) -> None:
        hands = iter([player_cards, bot_cards, *extra_hands])
        monkeypatch.setattr(blackjack_module.random, 'choices', lambda _population, k: next(hands))

        cards = iter(draws)
        monkeypatch.setattr(blackjack_module.random, 'choice', lambda _population: next(cards))
        monkeypatch.setattr(blackjack_module, 'sleep', lambda _seconds: None)

    return setup
