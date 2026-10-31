import random
from dataclasses import dataclass
from time import sleep
from typing import Any

from mini_store.colors import Colors
from mini_store.utils import ask_confirmation, fmt

from .abstract import AbstractGame


@dataclass
class Hand:
    score: int
    bet: int
    overflow: bool


class BlackjackGame(AbstractGame):
    def play(self) -> Any:
        print(f'\n {Colors.yellow}== Игра: Блекджек (21 очко) =={Colors.reset}\n')

        cards: tuple[int, ...] = (2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11)

        if self._player.bank_deposit > 0:
            self._player.bank_turns += 1

            if self._player.bank_turns >= 3:
                bonus = int(self._player.bank_deposit * 0.10)

                self._player.bank_deposit += bonus
                self._player.bank_turns = 0

                print(
                    f'{Colors.blue}📈 Инвестиции Незнакомца принесли плоды!{Colors.reset}'
                )
                print(
                    f'Ваш вклад увеличился: {Colors.green}+{fmt(bonus)}{Colors.reset} монет (Новый баланс вклада: {Colors.yellow}{fmt(self._player.bank_deposit)}{Colors.reset} монет).\n'
                )

            else:
                turns_left = 3 - self._player.bank_turns

                print(
                    f'⏳ До начисления процентов по вкладу осталось сыграть раундов: {turns_left} {"раз" if turns_left == 1 else "раза"}\n'
                )

        user_input = (
            input(
                f"Введите вашу ставку или 'all'/'все', чтобы поставить всё (Ваш баланс: {Colors.yellow}{fmt(self._player.balance)}{Colors.reset} монет): "
            )
            .strip()
            .lower()
        )

        try:
            if user_input == 'all' or user_input == 'все':
                money_player = self._player.balance

            else:
                money_player = int(user_input)

        except ValueError:
            print(
                f"\n{Colors.red}Ошибка! Введите корректное число или слово 'all'/'все'.{Colors.reset}"
            )
            return

        if money_player <= 0:
            print(
                f'\n{Colors.red}Ошибка! Ставка {fmt(money_player)} монет невозможна! Нельзя играть на 0 или меньше.{Colors.reset}'
            )
            return

        elif money_player > self._player.balance:
            print(
                f'\n{Colors.red}Ошибка! Нельзя вводить ставку больше своего баланса!{Colors.reset}'
            )
            return

        self._player.balance -= money_player

        player_cards = random.choices(cards, k=2)
        player_hands: list[Hand] = [Hand(sum(player_cards), money_player, False)]

        bot_cards = random.choices(cards, k=2)
        bot_score = sum(bot_cards)

        print('\nДилер раздал карты...')
        print(f'Открытая карта дилера: {Colors.blue}{bot_cards[0]}{Colors.reset}')

        insurance_bet = 0

        if bot_cards[0] == 11:
            print(
                f'\n{Colors.blue}🃏 У дилера открыт ТУЗ! Доступна страховка от Блекджека.{Colors.reset}\n'
            )

            insurance_cost = int(money_player / 2)

            if self._player.balance >= insurance_cost and ask_confirmation(
                f'Хотите купить страховку за {Colors.yellow}{fmt(insurance_cost)}{Colors.reset} монет?'
            ):
                self._player.balance -= insurance_cost

                insurance_bet = insurance_cost

                print(f'\n{Colors.green}✅ Страховка оформлена!{Colors.reset}')

        can_split = len(set(player_cards)) == 1 and (self._player.balance >= money_player)

        if can_split:
            print(
                f'\n{Colors.blue}🃏 У вас две одинаковые карты ({player_cards[0]} и {player_cards[1]})! Доступен СПЛИТ.{Colors.reset}'
            )
            if ask_confirmation(
                f'\nРазделить карты на две руки за дополнительную ставку {Colors.yellow}{fmt(money_player)}{Colors.reset} монет?'
            ):
                self._player.balance -= money_player

                if (
                    self._ctx.daily.contract is not None
                    and 'Разделить карты' in self._ctx.daily.contract
                    and not self._ctx.daily.completed
                ):
                    self._ctx.daily.progress += 1

                new_cards = random.choices(cards, k=2)

                player_hands = [
                    Hand(player_cards[i] + new_cards[i], money_player, False)
                    for i in range(2)
                ]

                print(f'\n{Colors.green}✂️ Карты разделены! Текущие руки:{Colors.reset}')
                print(
                    f'Рука №1: {Colors.yellow}{player_hands[0].score}{Colors.reset} очков (карты: {player_cards[0]} + {new_cards[0]})'
                )
                print(
                    f'Рука №2: {Colors.yellow}{player_hands[1].score}{Colors.reset} очков (карты: {player_cards[1]} + {new_cards[1]})'
                )

        for idx, hand in enumerate(player_hands):
            if len(player_hands) > 1:
                print(
                    f'\n{Colors.blue}=== Разыгрывается Рука №{idx + 1} ==={Colors.reset}'
                )

            while hand.score < 21:
                print(
                    f'\nУ вас на руках: {Colors.yellow}{hand.score}{Colors.reset} очков'
                )

                if ask_confirmation('Взять ещё карту?'):
                    random_card = random.choice(cards)
                    hand.score += random_card
                    print(
                        f'\nВы вытянули карту: {Colors.yellow}{random_card}{Colors.reset}'
                    )

                    if hand.score > 21:
                        print(
                            f'\nУ вас на руках: {Colors.red}{hand.score}{Colors.reset} очков'
                        )
                        print(f'\n{Colors.red}💥 Перебор на этой руке!{Colors.reset}')

                        hand.overflow = True
                        break
                else:
                    break

            if hand.score == 21:
                print(
                    f'\n🎉 {Colors.green}ОГО! На этой руке ровно 21 очко!{Colors.reset}'
                )

                if (
                    self._ctx.daily.contract
                    and 'ровно 21 очко' in self._ctx.daily.contract
                    and not self._ctx.daily.completed
                ):
                    self._ctx.daily.progress += 1

        all_overflow = all(hand.overflow for hand in player_hands)

        if all_overflow and insurance_bet == 0:
            print(
                f'\n{Colors.red}💥 Все ваши руки сгорели. Вы проиграли раунд!{Colors.reset}\n'
            )

            if (
                self._ctx.daily.contract
                and 'раундов в Блекджек' in self._ctx.daily.contract
                and not self._ctx.daily.completed
            ):
                self._ctx.daily.progress += 1

            return

        print(f'\n{Colors.blue}🤖 Очередь Дилера (Бота)...{Colors.reset}\n')
        print(
            f'Стартовые очки бота: {Colors.blue}{bot_score}{Colors.reset} (карты: {Colors.blue}{bot_cards[0]}{Colors.reset} и {Colors.blue}{bot_cards[1]}{Colors.reset})\n'
        )

        sleep(0.6)

        while bot_score < 17:
            bot_card = random.choice(cards)
            bot_score += bot_card

            print(
                f'🤖 Бот вытянул карту: {Colors.blue}{bot_card}{Colors.reset} (Всего у бота: {Colors.blue}{bot_score}{Colors.reset})\n'
            )

            sleep(0.6)

        print(f'Финальный счёт дилера: {Colors.blue}{bot_score}{Colors.reset} очков\n')

        sleep(0.4)

        if insurance_bet > 0:
            is_dealer_blackjack = sum(bot_cards) == 21

            if is_dealer_blackjack:
                insurance_payout = insurance_bet * 3

                self._player.balance += insurance_payout

                print(
                    f'💰 {Colors.green}Страховка сработала! У дилера Блекджек! Выплата: {fmt(insurance_payout)} монет.{Colors.reset}'
                )

            else:
                print(
                    f'🔴 {Colors.red}У дилера нет Блекджека на старте. Страховка сгорела.{Colors.reset}\n'
                )

        for idx, hand in enumerate(player_hands):
            if len(player_hands) > 1:
                print(
                    f'{Colors.blue}--- Итог по Руке №{idx + 1} ({hand.score} очков) ---{Colors.reset}'
                )

            if hand.overflow:
                print(f'{Colors.red}Эта рука проиграла из-за перебора.{Colors.reset}\n')
                continue

            if bot_score > 21 or hand.score > bot_score:
                reward_money = hand.bet
                reward_xp = 25

                if bot_score > 21:
                    print(
                        f'🎉 {Colors.green}Бот перебрал ({bot_score} очков)! Вы победили!{Colors.reset}',
                        f'{self._player.add_coins_and_xp(coins=reward_money, xp=reward_xp)}\n',
                        sep='\n',
                    )

                else:
                    print(
                        f'🎉 {Colors.green}Вы победили дилера ({hand.score} vs {bot_score})!{Colors.reset}',
                        f'{self._player.add_coins_and_xp(coins=reward_money, xp=reward_xp)}\n',
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

        if (
            self._ctx.daily.contract
            and 'раундов в Блекджек' in self._ctx.daily.contract
            and not self._ctx.daily.completed
        ):
            self._ctx.daily.progress += 1

        return
