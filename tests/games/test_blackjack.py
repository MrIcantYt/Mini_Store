from collections.abc import Callable

import pytest

from mini_store.context import GameContext
from mini_store.deck import Card, Suit
from mini_store.games.blackjack import BlackjackGame, Hand


class TestBlackjack:
    def test_hand(self) -> None:
        hand = Hand(
            cards=[Card(Suit.HEARTS, 10), Card(Suit.SPADES, 9)],
            bet=100,
            overflow=False,
        )

        assert hand.score == 19
        assert hand.bet == 100
        assert hand.overflow is False

    def test_soft_ace_counts_as_one(self) -> None:
        hand = Hand(
            cards=[Card(Suit.HEARTS, 1), Card(Suit.SPADES, 1)],
            bet=100,
            overflow=False,
        )

        assert hand.score == 12

    def test_ace_with_ten_is_twenty_one(self) -> None:
        hand = Hand(
            cards=[Card(Suit.HEARTS, 1), Card(Suit.SPADES, 10)],
            bet=100,
            overflow=False,
        )

        assert hand.score == 21

    def test_two_aces_and_nine_is_twenty_one(self) -> None:
        hand = Hand(
            cards=[Card(Suit.HEARTS, 1), Card(Suit.SPADES, 1), Card(Suit.CLUBS, 9)],
            bet=100,
            overflow=False,
        )

        assert hand.score == 21

    def test_bank_interest(
        self,
        feed_input: Callable[..., None],
        set_blackjack_cards: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        ctx.player.bank_deposit = 1000
        ctx.player.bank_turns = 2
        game = BlackjackGame(ctx)
        set_blackjack_cards([10, 9], [10, 8])
        feed_input('100', 'н')

        game.play()

        assert ctx.player.bank_deposit == 1100
        assert ctx.player.bank_turns == 0

    def test_bank_turns_are_counted(
        self,
        feed_input: Callable[..., None],
        set_blackjack_cards: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        ctx.player.bank_deposit = 1000
        game = BlackjackGame(ctx)
        set_blackjack_cards([10, 9], [10, 8])
        feed_input('100', 'н')

        game.play()

        assert ctx.player.bank_turns == 1
        assert ctx.player.bank_deposit == 1000

    @pytest.mark.parametrize('bet', ['abc', '0', '5000'])
    def test_invalid_bets(
        self,
        feed_input: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
        bet: str,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        feed_input(bet)

        game.play()

        assert ctx.player.balance == 1000

    def test_constructor_stores_context(self, ctx: GameContext) -> None:
        game = BlackjackGame(ctx)

        assert game._ctx is ctx
        assert game._player is ctx.player

    def test_win_pays_profit(
        self,
        feed_input: Callable[..., None],
        set_blackjack_cards: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        set_blackjack_cards([10, 9], [10, 8])
        feed_input('100', 'н')

        game.play()

        assert ctx.player.balance == 1100
        assert ctx.player.xp == 25

    def test_natural_blackjack_pays_three_to_two(
        self,
        feed_input: Callable[..., None],
        set_blackjack_cards: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        set_blackjack_cards([1, 10], [10, 8])
        feed_input('100')

        game.play()

        assert ctx.player.balance == 1150

    def test_loss_takes_the_bet(
        self,
        feed_input: Callable[..., None],
        set_blackjack_cards: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        set_blackjack_cards([10, 7], [10, 9])
        feed_input('100', 'н')

        game.play()

        assert ctx.player.balance == 900

    def test_push_returns_the_bet(
        self,
        feed_input: Callable[..., None],
        set_blackjack_cards: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        set_blackjack_cards([10, 9], [10, 9])
        feed_input('100', 'н')

        game.play()

        assert ctx.player.balance == 1000

    def test_bust_loses_the_bet(
        self,
        feed_input: Callable[..., None],
        set_blackjack_cards: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        set_blackjack_cards([10, 6], [10, 8], draws=(10,))
        feed_input('100', 'д')

        game.play()

        assert ctx.player.balance == 900

    def test_split_plays_both_hands(
        self,
        feed_input: Callable[..., None],
        set_blackjack_cards: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        set_blackjack_cards([10, 10], [10, 8], [2, 3])
        feed_input('100', 'д', 'н', 'н')

        game.play()

        assert ctx.player.balance == 800

    def test_insurance_pays_on_dealer_blackjack(
        self,
        feed_input: Callable[..., None],
        set_blackjack_cards: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        set_blackjack_cards([10, 9], [1, 10])
        feed_input('100', 'д', 'н')

        game.play()

        assert ctx.player.balance == 1000

    def test_pair_of_aces_is_not_blackjack(
        self,
        feed_input: Callable[..., None],
        set_blackjack_cards: Callable[..., None],
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        set_blackjack_cards([1, 1], [10, 8])
        feed_input('100', 'н', 'н')

        game.play()

        assert ctx.player.balance == 900

    def test_bank_turns_do_not_grow_on_invalid_bet(
        self,
        feed_input: Callable[..., None],
        ctx: GameContext,
    ) -> None:
        ctx.player.bank_deposit = 1000
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        feed_input('abc')

        game.play()

        assert ctx.player.bank_turns == 0
        assert ctx.player.bank_deposit == 1000

    @pytest.mark.parametrize('bet', ['all', 'все'])
    def test_all_in_bet(
        self,
        feed_input: Callable[..., None],
        set_blackjack_cards: Callable[..., None],
        ctx: GameContext,
        bet: str,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        set_blackjack_cards([10, 9], [10, 8])
        feed_input(bet, 'н')

        game.play()

        assert ctx.player.balance == 2000

    def test_insurance_declined(
        self,
        feed_input: Callable[..., None],
        set_blackjack_cards: Callable[..., None],
        ctx: GameContext,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        set_blackjack_cards([10, 9], [1, 8])
        feed_input('100', 'н', 'н')

        game.play()

        assert ctx.player.balance == 1000

    def test_insurance_lost(
        self,
        feed_input: Callable[..., None],
        set_blackjack_cards: Callable[..., None],
        ctx: GameContext,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        set_blackjack_cards([10, 9], [1, 8])
        feed_input('100', 'д', 'н')

        game.play()

        # bet 100, insurance 50, push returns 100
        assert ctx.player.balance == 950

    def test_split_aces_get_one_card_each(
        self,
        feed_input: Callable[..., None],
        set_blackjack_cards: Callable[..., None],
        ctx: GameContext,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        set_blackjack_cards([1, 1], [10, 8], [10, 10])
        feed_input('100', 'д')

        game.play()

        # two bets of 100, both hands get A + 10 = 21 and win 1:1
        assert ctx.player.balance == 1200

    def test_dealer_draws_to_seventeen(
        self,
        feed_input: Callable[..., None],
        set_blackjack_cards: Callable[..., None],
        ctx: GameContext,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        set_blackjack_cards([10, 7], [10, 2], draws=(5,))
        feed_input('100', 'н')

        game.play()

        assert ctx.player.balance == 1000

    def test_natural_push_against_dealer_blackjack(
        self,
        feed_input: Callable[..., None],
        set_blackjack_cards: Callable[..., None],
        ctx: GameContext,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        set_blackjack_cards([1, 10], [1, 10])
        feed_input('100', 'н')

        game.play()

        assert ctx.player.balance == 1000

    def test_player_wins_when_dealer_busts(
        self,
        feed_input: Callable[..., None],
        set_blackjack_cards: Callable[..., None],
        ctx: GameContext,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        set_blackjack_cards([10, 9], [10, 6], draws=(10,))
        feed_input('100', 'н')

        game.play()

        assert ctx.player.balance == 1100

    def test_daily_round_progress(
        self,
        feed_input: Callable[..., None],
        set_blackjack_cards: Callable[..., None],
        ctx: GameContext,
    ) -> None:
        ctx.player.balance = 1000
        ctx.daily.contract = 'Сыграть 3 раундов в Блекджек'
        game = BlackjackGame(ctx)
        set_blackjack_cards([10, 9], [10, 8])
        feed_input('100', 'н')

        game.play()

        assert ctx.daily.progress == 1

    def test_daily_split_progress(
        self,
        feed_input: Callable[..., None],
        set_blackjack_cards: Callable[..., None],
        ctx: GameContext,
    ) -> None:
        ctx.player.balance = 1000
        ctx.daily.contract = 'Разделить карты 2 раза'
        game = BlackjackGame(ctx)
        set_blackjack_cards([10, 10], [10, 8], [2, 3])
        feed_input('100', 'д', 'н', 'н')

        game.play()

        assert ctx.daily.progress == 1
