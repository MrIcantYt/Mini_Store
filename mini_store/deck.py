from dataclasses import dataclass
from enum import StrEnum
from random import shuffle


class Suit(StrEnum):
    HEARTS = '♥'
    DIAMONDS = '♦'
    CLUBS = '♣'
    SPADES = '♠'


@dataclass(frozen=True, slots=True)
class Card:
    """A playing card.

    Attributes:
        suit (Suit): The card's suit.
        rank (int): Card rank, 1 (Ace) through 13 (King).
    """

    suit: Suit
    rank: int

    @property
    def value(self) -> int:
        """Blackjack value of the card, treating Ace as 11.

        Aces are counted as 11 here; soft-hand logic (downgrading an
        Ace to 1) is handled at the hand level, not per card.
        """
        if self.rank == 1:
            return 11
        if self.rank >= 10:
            return 10
        return self.rank

    def __str__(self) -> str:
        names = {1: 'A', 11: 'J', 12: 'Q', 13: 'K'}
        rank = names.get(self.rank, str(self.rank))
        return f'{rank}{self.suit.value}'


class Deck:
    """A deck of playing cards for blackjack.

    Attributes:
        cards (list[Card]): Remaining cards in the shoe.
    """

    def __init__(self, cards: list[Card] | None = None) -> None:
        """Initializes the shoe.

        Args:
            cards (list[Card] | None): Explicit card list. If None, a
                shoe is built from `decks` standard decks.
        """
        if cards is None:
            self.cards = [Card(suit, rank) for suit in Suit for rank in range(1, 14)]
        else:
            self.cards = list(cards)

    def take_cards(self, count: int = 1) -> list[Card]:
        """Draws `count` cards from the shoe.

        Args:
            count (int): Number of cards to draw. Defaults to 1.

        Returns:
            list[Card]: Drawn cards. Returns fewer if the shoe runs out.

        Raises:
            ValueError: If `count` is less than 1.
        """
        if count < 1:
            raise ValueError(f'count must be >= 1, got {count}')
        count = min(count, len(self.cards))
        return [self.cards.pop() for _ in range(count)]

    def shuffle(self) -> None:
        """Shuffles the remaining cards in place."""
        shuffle(self.cards)

    def __len__(self) -> int:
        """Returns the number of remaining cards."""
        return len(self.cards)

    def __bool__(self) -> bool:
        """Returns True if the shoe still has cards."""
        return bool(self.cards)
