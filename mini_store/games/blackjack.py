from dataclasses import dataclass
from time import sleep

from mini_store.colors import Colors
from mini_store.deck import Card, Deck
from mini_store.utils import ask_confirmation, cls, fmt

from .abstract import AbstractGame

DEALER_STAND = 17
BLACKJACK_PAYOUT = 1.5
INSURANCE_PAYOUT = 3
WIN_XP = 25
BANK_TURNS = 3
BANK_BONUS_RATE = 0.1


def score_cards(cards: list[Card]) -> int:
    """Returns the blackjack score of the cards, downgrading aces when needed."""
    total = sum(card.value for card in cards)
    aces = sum(card.rank == 1 for card in cards)

    while total > 21 and aces:
        total -= 10
        aces -= 1

    return total


@dataclass(slots=True)
class Hand:
    cards: list[Card]
    bet: int
    overflow: bool

    @property
    def score(self) -> int:
        return score_cards(self.cards)


class BlackjackGame(AbstractGame):
    def play(self):
        cls()
        print(f'\n {Colors.yellow}== Игра: Блекджек (21 очко) =={Colors.reset}\n')

        deck = Deck()
        deck.shuffle()

        bet = self._ask_bet()
        if bet is None:
            return

        self._player.balance -= bet

        player_hands, bot_cards = self._deal(deck, bet)
        bot_score = score_cards(bot_cards)

        print('\nДилер раздал карты...')
        print(f'Открытая карта дилера: {Colors.blue}{bot_cards[0]}{Colors.reset}')

        insurance_bet = self._offer_insurance(bot_cards, bet)
        dealer_blackjack = len(bot_cards) == 2 and bot_score == 21

        player_hands, split_aces = self._offer_split(deck, player_hands, bet)

        for index, hand in enumerate(player_hands):
            self._play_hand(index, hand, len(player_hands), deck, split_aces)

        bot_score = self._dealer_turn(deck, bot_cards, bot_score)
        self._settle_insurance(insurance_bet, dealer_blackjack)

        for index, hand in enumerate(player_hands):
            self._settle_hand(index, hand, len(player_hands), bot_score, dealer_blackjack)

        self._ctx.daily.register_daily('раундов в Блекджек')
        self._apply_bank_interest()

    def _ask_bet(self) -> int | None:
        user_input = (
            input(
                f"Введите вашу ставку или 'all'/'все' (Ваш баланс: {Colors.yellow}{fmt(self._player.balance)}{Colors.reset} монет): "
            )
            .strip()
            .lower()
        )

        try:
            if user_input == 'all' or user_input == 'все':
                bet = self._player.balance

            else:
                bet = int(user_input)

        except ValueError:
            print(
                f"\n{Colors.red}Ошибка! Введите корректное число или слово 'all'/'все'.{Colors.reset}\n"
            )
            return None

        if bet <= 0:
            print(
                f'\n{Colors.red}Ошибка! Ставка {fmt(bet)} монет невозможна! Нельзя играть на 0 или меньше.{Colors.reset}\n'
            )
            return None

        if bet > self._player.balance:
            print(
                f'\n{Colors.red}Ошибка! Нельзя вводить ставку больше своего баланса!{Colors.reset}\n'
            )
            return None

        return bet

    def _deal(self, deck: Deck, bet: int) -> tuple[list[Hand], list[Card]]:
        player_hands = [Hand(deck.take_cards(2), bet, False)]
        bot_cards = deck.take_cards(2)

        return player_hands, bot_cards

    def _offer_insurance(self, bot_cards: list[Card], bet: int) -> int:
        if bot_cards[0] != 11:
            return 0

        print(
            f'\n{Colors.blue}🃏 У дилера открыт ТУЗ! Доступна страховка от Блекджека.{Colors.reset}\n'
        )

        insurance_cost = int(bet / 2)

        if self._player.balance < insurance_cost or not ask_confirmation(
            f'Хотите купить страховку за {Colors.yellow}{fmt(insurance_cost)}{Colors.reset} монет?'
        ):
            return 0

        self._player.balance -= insurance_cost
        print(f'\n{Colors.green}✅ Страховка оформлена!{Colors.reset}')

        return insurance_cost

    def _offer_split(
        self,
        deck: Deck,
        player_hands: list[Hand],
        bet: int,
    ) -> tuple[list[Hand], bool]:
        hand = player_hands[0]
        can_split = (
            len(hand.cards) == 2
            and hand.cards[0].value == hand.cards[1].value
            and self._player.balance >= bet
        )

        if not can_split:
            return player_hands, False

        print(
            f'\n{Colors.blue}🃏 У вас две одинаковые карты ({hand.cards[0]} и {hand.cards[1]})! Доступен СПЛИТ.{Colors.reset}'
        )

        if not ask_confirmation(
            f'\nРазделить карты на две руки за дополнительную ставку {Colors.yellow}{fmt(bet)}{Colors.reset} монет?'
        ):
            return player_hands, False

        self._player.balance -= bet
        self._ctx.daily.register_daily('Разделить карты')

        left, right = hand.cards
        split_aces = left.rank == 1
        player_hands = [
            Hand([left, *deck.take_cards(1)], bet, False),
            Hand([right, *deck.take_cards(1)], bet, False),
        ]

        print(f'\n{Colors.green}✂️ Карты разделены! Текущие руки:{Colors.reset}')
        print(
            f'Рука №1: {Colors.yellow}{player_hands[0].score}{Colors.reset} очков (карты: {", ".join(map(str, player_hands[0].cards))})'
        )
        print(
            f'Рука №2: {Colors.yellow}{player_hands[1].score}{Colors.reset} очков (карты: {", ".join(map(str, player_hands[1].cards))})'
        )

        return player_hands, split_aces

    def _play_hand(
        self,
        index: int,
        hand: Hand,
        hands_count: int,
        deck: Deck,
        split_aces: bool,
    ) -> None:
        if hands_count > 1:
            print(f'\n{Colors.blue}=== Разыгрывается Рука №{index + 1} ==={Colors.reset}')

        # After splitting aces each hand gets one card only.
        if split_aces:
            print(f'\nУ вас на руках: {Colors.yellow}{hand.score}{Colors.reset} очков')
            return

        while hand.score < 21:
            print(f'\nУ вас на руках: {Colors.yellow}{hand.score}{Colors.reset} очков')

            if not ask_confirmation('Взять ещё карту?'):
                break

            card = deck.take_cards(1)[0]
            hand.cards.append(card)
            print(f'\nВы вытянули карту: {Colors.yellow}{card}{Colors.reset}')

            if hand.score > 21:
                print(f'\nУ вас на руках: {Colors.red}{hand.score}{Colors.reset} очков')
                print(f'\n{Colors.red}💥 Перебор на этой руке!{Colors.reset}')

                hand.overflow = True
                break

        if hand.score == 21:
            print(f'\n🎉 {Colors.green}ОГО! На этой руке ровно 21 очко!{Colors.reset}')
            self._ctx.daily.register_daily('ровно 21 очко')

    def _dealer_turn(self, deck: Deck, bot_cards: list[Card], bot_score: int) -> int:
        print(f'\n{Colors.blue}🤖 Очередь Дилера (Бота)...{Colors.reset}\n')
        print(
            f'Стартовые очки бота: {Colors.blue}{bot_score}{Colors.reset} (карты: {Colors.blue}{bot_cards[0]}{Colors.reset} и {Colors.blue}{bot_cards[1]}{Colors.reset})\n'
        )

        sleep(0.6)

        while bot_score < DEALER_STAND:
            bot_card = deck.take_cards(1)[0]
            bot_cards.append(bot_card)
            bot_score = score_cards(bot_cards)

            print(
                f'🤖 Бот вытянул карту: {Colors.blue}{bot_card}{Colors.reset} (Всего у бота: {Colors.blue}{bot_score}{Colors.reset})\n'
            )

            sleep(0.6)

        print(f'Финальный счёт дилера: {Colors.blue}{bot_score}{Colors.reset} очков\n')

        sleep(0.4)

        return bot_score

    def _settle_insurance(self, insurance_bet: int, dealer_blackjack: bool) -> None:
        if insurance_bet <= 0:
            return

        if dealer_blackjack:
            insurance_payout = insurance_bet * INSURANCE_PAYOUT

            self._player.balance += insurance_payout

            print(
                f'💰 {Colors.green}Страховка сработала! У дилера Блекджек! Выплата: {fmt(insurance_payout)} монет.{Colors.reset}'
            )

        else:
            print(
                f'🔴 {Colors.red}У дилера нет Блекджека на старте. Страховка сгорела.{Colors.reset}\n'
            )

    def _settle_hand(
        self,
        index: int,
        hand: Hand,
        hands_count: int,
        bot_score: int,
        dealer_blackjack: bool,
    ) -> None:
        if hands_count > 1:
            print(
                f'{Colors.blue}--- Итог по Руке №{index + 1} ({hand.score} очков) ---{Colors.reset}'
            )

        if hand.overflow:
            print(f'{Colors.red}Эта рука проиграла из-за перебора.{Colors.reset}\n')
            return

        natural_blackjack = hands_count == 1 and len(hand.cards) == 2 and hand.score == 21

        if natural_blackjack:
            if dealer_blackjack:
                self._player.balance += hand.bet

                print(
                    f'{Colors.yellow}🤝 У дилера тоже Блекджек! Ставка возвращена.{Colors.reset}\n'
                )
                return

            profit = int(hand.bet * BLACKJACK_PAYOUT)

            # return bet without multipliers, profit goes through multipliers
            self._player.balance += hand.bet
            print(
                f'🎉 {Colors.green}БЛЕКДЖЕК! Выплата 3:2.{Colors.reset}',
                f'{self._player.add_coins_and_xp(coins=profit, xp=WIN_XP)}\n',
                sep='\n',
            )
            return

        if bot_score > 21 or hand.score > bot_score:
            # return bet without multipliers, profit goes through multipliers
            self._player.balance += hand.bet

            print(
                f'🎉 {Colors.green}Бот перебрал ({bot_score} очков)! Вы победили!{Colors.reset}'
                if bot_score > 21
                else f'🎉 {Colors.green}Вы победили дилера ({hand.score} vs {bot_score})!{Colors.reset}',
                f'{self._player.add_coins_and_xp(coins=hand.bet, xp=WIN_XP)}\n',
                sep='\n',
            )

        elif hand.score == bot_score:
            self._player.balance += hand.bet

            print(
                f'{Colors.yellow}🤝 Ничья! Очков поровну ({hand.score} vs {bot_score}). Ставка возвращена.{Colors.reset}\n'
            )

        else:
            print(
                f'{Colors.red}🔴 У дилера больше очков ({bot_score}). Ставка сгорела!{Colors.reset}\n'
            )

    def _apply_bank_interest(self) -> None:
        if self._player.bank_deposit <= 0:
            return

        self._player.bank_turns += 1

        if self._player.bank_turns >= BANK_TURNS:
            bonus = int(self._player.bank_deposit * BANK_BONUS_RATE)

            self._player.bank_deposit += bonus
            self._player.bank_turns = 0

            print(f'{Colors.blue}📈 Инвестиции Незнакомца принесли плоды!{Colors.reset}')
            print(
                f'Ваш вклад увеличился: {Colors.green}+{fmt(bonus)}{Colors.reset} монет (Новый баланс вклада: {Colors.yellow}{fmt(self._player.bank_deposit)}{Colors.reset} монет).\n'
            )

        else:
            turns_left = BANK_TURNS - self._player.bank_turns

            print(
                f'⏳ До начисления процентов по вкладу осталось сыграть раундов: {turns_left} {"раз" if turns_left == 1 else "раза"}\n'
            )
