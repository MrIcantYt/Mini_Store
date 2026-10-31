import pytest

from mini_store.deck import Card, Deck, Suit


class TestCard:
    def test_ace_value(self) -> None:
        assert Card(Suit.SPADES, 1).value == 11

    @pytest.mark.parametrize('rank', [10, 11, 12, 13])
    def test_face_cards_value(self, rank: int) -> None:
        assert Card(Suit.HEARTS, rank).value == 10

    @pytest.mark.parametrize(('rank', 'value'), [(2, 2), (5, 5), (9, 9)])
    def test_number_cards_value(self, rank: int, value: int) -> None:
        assert Card(Suit.CLUBS, rank).value == value

    @pytest.mark.parametrize(
        ('rank', 'expected'),
        [
            (1, 'A♥'),
            (5, '5♥'),
            (10, '10♥'),
            (11, 'J♥'),
            (12, 'Q♥'),
            (13, 'K♥'),
        ],
    )
    def test_str(self, rank: int, expected: str) -> None:
        assert str(Card(Suit.HEARTS, rank)) == expected

    def test_cards_are_frozen(self) -> None:
        card = Card(Suit.HEARTS, 1)

        with pytest.raises(AttributeError):
            card.rank = 2  # ty: ignore[invalid-assignment]


class TestDeck:
    def test_default_deck_has_52_cards(self) -> None:
        deck = Deck()

        assert len(deck) == 52
        assert len(set(deck.cards)) == 52

    def test_custom_cards(self) -> None:
        cards = [Card(Suit.HEARTS, 2), Card(Suit.HEARTS, 3)]

        deck = Deck(cards)
        cards.append(Card(Suit.HEARTS, 4))

        assert len(deck) == 2

    def test_take_card(self) -> None:
        deck = Deck([Card(Suit.HEARTS, 2), Card(Suit.HEARTS, 3)])

        drawn = deck.take_cards()

        assert drawn == [Card(Suit.HEARTS, 3)]
        assert len(deck) == 1

    def test_take_multiple_cards(self) -> None:
        deck = Deck()

        drawn = deck.take_cards(5)

        assert len(drawn) == 5
        assert len(deck) == 47

    def test_take_more_than_available(self) -> None:
        deck = Deck([Card(Suit.HEARTS, 2)])

        assert len(deck.take_cards(10)) == 1
        assert len(deck) == 0

    @pytest.mark.parametrize('count', [0, -1])
    def test_take_invalid_count(self, count: int) -> None:
        with pytest.raises(ValueError, match='count must be'):
            Deck().take_cards(count)

    def test_bool(self) -> None:
        assert Deck()
        assert not Deck([])

    def test_shuffle_keeps_same_cards(self) -> None:
        deck = Deck()
        before = set(deck.cards)

        deck.shuffle()

        assert set(deck.cards) == before
