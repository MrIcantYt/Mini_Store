import pytest

import mini_store.games.blackjack as blackjack_module
import mini_store.games.craps as craps_module
import mini_store.games.guess_number as guess_module
import mini_store.games.rock_scissors_paper as rsp_module
import mini_store.games.routtle as routtle_module
import mini_store.games.slots as slots_module
from mini_store.context import GameContext
from mini_store.games.blackjack import BlackjackGame, Hand
from mini_store.games.craps import CrapsGame
from mini_store.games.guess_number import GuessNumberGame, Levels
from mini_store.games.rock_scissors_paper import RockScissorsPaperGame
from mini_store.games.routtle import RouttleGame
from mini_store.games.slots import Slot, SlotsGame
from mini_store.player import Player


def feed_input(monkeypatch: pytest.MonkeyPatch, *values: str) -> None:
    iterator = iter(values)
    monkeypatch.setattr('builtins.input', lambda _prompt='': next(iterator))


def set_blackjack_cards(
    monkeypatch: pytest.MonkeyPatch,
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


@pytest.fixture(autouse=True)
def silence_clear(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(guess_module, 'cls', lambda: None)


class TestSlots:
    def test_slot_symbols(self) -> None:
        assert str(Slot.SEVEN) == '7'
        assert str(Slot.SACK_MONEY) == '💰'

    def test_three_equal_slots(self, ctx: GameContext) -> None:
        game = SlotsGame(ctx)
        game._slots = [Slot.CHERRY, Slot.CHERRY, Slot.CHERRY]

        assert game._all_slots_is() is Slot.CHERRY

    def test_different_slots(self, ctx: GameContext) -> None:
        game = SlotsGame(ctx)
        game._slots = [Slot.CHERRY, Slot.CHERRY, Slot.SEVEN]

        assert game._all_slots_is() is None

    def test_variants_without_potion(self, ctx: GameContext) -> None:
        game = SlotsGame(ctx)

        assert len(game._setup_variants()) == 8

    def test_variants_with_potion(self, ctx: GameContext) -> None:
        ctx.player.potion_luck = True
        game = SlotsGame(ctx)

        assert len(game._setup_variants()) == 12

    def test_win_pays_reward(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = SlotsGame(ctx)
        game._slots = [Slot.CHERRY, Slot.CHERRY, Slot.CHERRY]
        feed_input(monkeypatch, '100')
        monkeypatch.setattr(slots_module, 'sleep', lambda _seconds: None)

        game.play()

        assert ctx.player.balance == 1100
        assert ctx.player.xp == 20

    def test_invalid_bet_does_not_change_balance(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = SlotsGame(ctx)
        feed_input(monkeypatch, 'abc')

        game.play()

        assert ctx.player.balance == 1000

    def test_bet_above_balance(self, ctx: GameContext, monkeypatch: pytest.MonkeyPatch) -> None:
        ctx.player.balance = 100
        game = SlotsGame(ctx)
        feed_input(monkeypatch, '500')

        game.play()

        assert ctx.player.balance == 100

    def test_vip_bet(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 2000
        game = SlotsGame(ctx)
        game._slots = [Slot.CHERRY, Slot.CHERRY, Slot.CHERRY]
        feed_input(monkeypatch, '777')
        monkeypatch.setattr(slots_module, 'sleep', lambda _seconds: None)

        game.play()

        assert ctx.player.balance == 4331
        assert ctx.player.xp == 40

    def test_quest_progress(self, ctx: GameContext, monkeypatch: pytest.MonkeyPatch) -> None:
        ctx.player.quest_id = 3
        ctx.player.balance = 100
        game = SlotsGame(ctx)
        feed_input(monkeypatch, '10')
        monkeypatch.setattr(slots_module, 'sleep', lambda _seconds: None)

        game.play()

        assert ctx.player.quest_progress == 1

    def test_quest_does_not_progress_on_invalid_bet(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.quest_id = 3
        ctx.player.balance = 100
        game = SlotsGame(ctx)
        feed_input(monkeypatch, 'abc')

        game.play()

        assert ctx.player.quest_progress == 0

    def test_vip_with_777_and_balance_1000(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = SlotsGame(ctx)
        game._slots = [Slot.CHERRY, Slot.CHERRY, Slot.CHERRY]
        feed_input(monkeypatch, '777')
        monkeypatch.setattr(slots_module, 'sleep', lambda _seconds: None)

        game.play()

        assert game._is_vip is True
        assert ctx.player.balance == 3331


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
        monkeypatch.setattr(guess_module, 'ask_option', lambda *a, **k: Levels.easy)
        monkeypatch.setattr(guess_module, 'ask_number', lambda *a, **k: 7)
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
        monkeypatch.setattr(guess_module, 'ask_option', lambda *a, **k: Levels.easy)
        monkeypatch.setattr(guess_module, 'ask_number', lambda *a, **k: 7)
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
        monkeypatch.setattr(guess_module, 'ask_option', lambda *a, **k: None)

        game.play()

        assert ctx.player.balance == 0


class TestRockScissorsPaper:
    def test_win(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        game = RockScissorsPaperGame(ctx)
        feed_input(monkeypatch, 'камень')
        monkeypatch.setattr(rsp_module.random, 'choice', lambda _items: 'ножницы')
        monkeypatch.setattr(rsp_module.random, 'randint', lambda _a, _b: 50)

        game.play()

        assert ctx.player.balance == 25

    def test_potion_increases_critical_chance(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.potion_luck = True
        game = RockScissorsPaperGame(ctx)
        feed_input(monkeypatch, 'камень')
        monkeypatch.setattr(rsp_module.random, 'choice', lambda _items: 'ножницы')
        monkeypatch.setattr(rsp_module.random, 'randint', lambda _a, _b: 20)

        game.play()

        assert ctx.player.balance == 50

    def test_invalid_choice_reprompts(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        game = RockScissorsPaperGame(ctx)
        feed_input(monkeypatch, 'invalid', 'камень')
        monkeypatch.setattr(rsp_module.random, 'choice', lambda _items: 'ножницы')
        monkeypatch.setattr(rsp_module.random, 'randint', lambda _a, _b: 50)

        game.play()

        assert ctx.player.balance == 25


class TestRouttle:
    def test_zero_win(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 500
        game = RouttleGame(ctx)
        feed_input(monkeypatch, '100')
        monkeypatch.setattr(routtle_module, 'ask_option', lambda *a, **k: 'зеро')
        monkeypatch.setattr(routtle_module.random, 'randint', lambda _a, _b: 0)
        monkeypatch.setattr(routtle_module.time, 'sleep', lambda _s: None)

        game.play()

        assert ctx.player.balance == 4250
        assert ctx.player.xp == 150

    def test_color_win(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 500
        game = RouttleGame(ctx)
        feed_input(monkeypatch, '100')
        monkeypatch.setattr(routtle_module, 'ask_option', lambda *a, **k: 'красное')
        monkeypatch.setattr(routtle_module.random, 'randint', lambda _a, _b: 2)
        monkeypatch.setattr(routtle_module.time, 'sleep', lambda _s: None)

        game.play()

        assert ctx.player.balance == 600
        assert ctx.player.xp == 30

    def test_loss(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 500
        game = RouttleGame(ctx)
        feed_input(monkeypatch, '100')
        monkeypatch.setattr(routtle_module, 'ask_option', lambda *a, **k: 'красное')
        monkeypatch.setattr(routtle_module.random, 'randint', lambda _a, _b: 1)
        monkeypatch.setattr(routtle_module.time, 'sleep', lambda _s: None)

        game.play()

        assert ctx.player.balance == 400

    def test_all_in(self, ctx: GameContext, monkeypatch: pytest.MonkeyPatch) -> None:
        ctx.player.balance = 500
        game = RouttleGame(ctx)
        feed_input(monkeypatch, 'все')
        monkeypatch.setattr(routtle_module, 'ask_option', lambda *a, **k: 'зеро')
        monkeypatch.setattr(routtle_module.random, 'randint', lambda _a, _b: 0)
        monkeypatch.setattr(routtle_module.time, 'sleep', lambda _s: None)

        game.play()

        assert ctx.player.balance == 19_250

    @pytest.mark.parametrize('bet', ['abc', '0', '501'])
    def test_invalid_bets(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
        bet: str,
    ) -> None:
        ctx.player.balance = 500
        game = RouttleGame(ctx)
        feed_input(monkeypatch, bet)

        game.play()

        assert ctx.player.balance == 500


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
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = CrapsGame(ctx)
        feed_input(monkeypatch, '100', '')
        monkeypatch.setattr(game, '_roll_dice_get_total', lambda: 7)

        game.play()

        assert ctx.player.balance == 1050
        assert ctx.player.xp == 25

    def test_craps_loss(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = CrapsGame(ctx)
        feed_input(monkeypatch, '100', '')
        monkeypatch.setattr(game, '_roll_dice_get_total', lambda: 2)

        game.play()

        assert ctx.player.balance == 900

    def test_surrender_refunds_half(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = CrapsGame(ctx)
        feed_input(monkeypatch, '100', '')
        monkeypatch.setattr(game, '_roll_dice_get_total', lambda: 5)
        monkeypatch.setattr(craps_module, 'ask_confirmation', lambda _prompt: False)

        game.play()

        assert ctx.player.balance == 950

    def test_point_win(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = CrapsGame(ctx)
        feed_input(monkeypatch, '100', '')
        rolls = iter([5, 5])
        monkeypatch.setattr(game, '_roll_dice_get_total', lambda: next(rolls))
        monkeypatch.setattr(craps_module, 'ask_confirmation', lambda _prompt: True)

        game.play()

        assert ctx.player.balance == 1050

    @pytest.mark.parametrize('bet', ['abc', '0', '5000'])
    def test_invalid_bets(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
        bet: str,
    ) -> None:
        ctx.player.balance = 1000
        game = CrapsGame(ctx)
        feed_input(monkeypatch, bet)

        game.play()

        assert ctx.player.balance == 1000


class TestBlackjack:
    def test_hand(self) -> None:
        hand = Hand(score=20, bet=100, overflow=False)

        assert hand.score == 20
        assert hand.bet == 100
        assert hand.overflow is False

    def test_bank_interest(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.bank_deposit = 1000
        ctx.player.bank_turns = 2
        game = BlackjackGame(ctx)
        feed_input(monkeypatch, '0')

        game.play()

        assert ctx.player.bank_deposit == 1100
        assert ctx.player.bank_turns == 0

    def test_bank_turns_are_counted(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.bank_deposit = 1000
        game = BlackjackGame(ctx)
        feed_input(monkeypatch, '0')

        game.play()

        assert ctx.player.bank_turns == 1
        assert ctx.player.bank_deposit == 1000

    @pytest.mark.parametrize('bet', ['abc', '0', '5000'])
    def test_invalid_bets(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
        bet: str,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        feed_input(monkeypatch, bet)

        game.play()

        assert ctx.player.balance == 1000

    def test_constructor_stores_context(self, ctx: GameContext) -> None:
        game = BlackjackGame(ctx)

        assert game._ctx is ctx
        assert game._player is ctx.player

    def test_win_pays_profit(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        set_blackjack_cards(monkeypatch, [10, 9], [10, 8])
        feed_input(monkeypatch, '100', 'н')

        game.play()

        assert ctx.player.balance == 1100
        assert ctx.player.xp == 25

    def test_loss_takes_the_bet(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        set_blackjack_cards(monkeypatch, [10, 7], [10, 9])
        feed_input(monkeypatch, '100', 'н')

        game.play()

        assert ctx.player.balance == 900

    def test_push_returns_the_bet(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        set_blackjack_cards(monkeypatch, [10, 9], [10, 9])
        feed_input(monkeypatch, '100', 'н')

        game.play()

        assert ctx.player.balance == 1000

    def test_bust_loses_the_bet(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        set_blackjack_cards(monkeypatch, [10, 6], [10, 8], draws=(10,))
        feed_input(monkeypatch, '100', 'д')

        game.play()

        assert ctx.player.balance == 900

    def test_split_plays_both_hands(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        set_blackjack_cards(monkeypatch, [10, 10], [10, 8], [2, 3])
        feed_input(monkeypatch, '100', 'д', 'н', 'н')

        game.play()

        assert ctx.player.balance == 800

    def test_insurance_pays_on_dealer_blackjack(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        set_blackjack_cards(monkeypatch, [10, 9], [11, 10])
        feed_input(monkeypatch, '100', 'д', 'н')

        game.play()

        assert ctx.player.balance == 1000

    def test_pair_of_aces_is_not_blackjack(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        set_blackjack_cards(monkeypatch, [11, 11], [10, 8])
        feed_input(monkeypatch, '100', 'н', 'н')

        game.play()

        assert ctx.player.balance == 900

    def test_bank_turns_do_not_grow_on_invalid_bet(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx.player.bank_deposit = 1000
        ctx.player.balance = 1000
        game = BlackjackGame(ctx)
        feed_input(monkeypatch, 'abc')

        game.play()

        assert ctx.player.bank_turns == 0
        assert ctx.player.bank_deposit == 1000
