from collections.abc import Callable

import pytest

import mini_store.games.blackjack as blackjack_module
from mini_store.deck import Card, Suit


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
        sequence = [
            *player_cards,
            *bot_cards,
            *(card for hand in extra_hands for card in hand),
            *draws,
        ]
        cards = iter(Card(Suit.HEARTS, rank) for rank in sequence)

        monkeypatch.setattr(
            blackjack_module.Deck,
            'take_cards',
            lambda _self, count=1: [next(cards) for _ in range(count)],
        )
        monkeypatch.setattr(blackjack_module.Deck, 'shuffle', lambda _self: None)
        monkeypatch.setattr(blackjack_module, 'sleep', lambda _seconds: None)

    return setup
