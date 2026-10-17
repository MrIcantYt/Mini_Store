import random
from time import sleep
from typing import Any

from mini_store.colors import Colors
from mini_store.utils import fmt

from .abstract import AbstractGame, Player


class BlackjackGame(AbstractGame):
    def __init__(self, player: Player):
        self._player = player

    def play(self) -> Any:
        print(f'\n {Colors.yellow}== Игра: Блекджек (21 очко) =={Colors.reset}\n')

        cards: tuple[int, ...] = (2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11)

        user_input = (
            input(
                f"Введите вашу ставку или 'all'/'все', чтобы поставить всё (Ваш баланс: {fmt(self._player.balance)}): "
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
            print(f"\n{Colors.red}Ошибка! Введите корректное число или слово 'all'/'все'.{Colors.reset}")
            return

        if money_player <= 0:
            print(f'\n{Colors.red}Ошибка! Ставка {fmt(money_player)} монет невозможна! Нельзя играть на 0 или меньше.{Colors.reset}')
            return

        elif money_player > self._player.balance:
            print(f'\n{Colors.red}Ошибка! Нельзя вводить ставку больше своего баланса!{Colors.reset}')
            return

        self._player.balance -= money_player

        player_card1 = random.choice(cards)
        player_card2 = random.choice(cards)
        
        player_hands = [
            {"score": player_card1 + player_card2, "bet": money_player, "overflow": False}
        ]

        bot_card1 = random.choice(cards)
        bot_card2 = random.choice(cards)
        bot_score = bot_card1 + bot_card2

        print("\nДилер раздал карты...")
        print(f"Открытая карта дилера: {Colors.blue}{bot_card1}{Colors.reset}")

        insurance_bet = 0

        if bot_card1 == 11:
            print(f"\n{Colors.blue}🃏 У дилера открыт ТУЗ! Доступна страховка от Блекджека.{Colors.reset}\n")
            
            insurance_cost = int(money_player / 2)
            
            if self._player.balance >= insurance_cost:
                ins_choice = input(f"Хотите купить страховку за {Colors.yellow}{fmt(insurance_cost)}{Colors.reset} монет? (Да/Нет): ").strip().lower()
                
                if ins_choice in ('д', 'y', 'yes', 'да'):
                    self._player.balance -= insurance_cost
                    insurance_bet = insurance_cost
                
                    print(f"\n{Colors.green}✅ Страховка оформлена!{Colors.reset}")
            
            else:
                print(f"{Colors.red}У вас недостаточно монет для покупки страховки (нужно {fmt(insurance_cost)}).{Colors.reset}")

        can_split = (player_card1 == player_card2) and (self._player.balance >= money_player)
        
        if can_split:
            print(f"\n{Colors.blue}🃏 У вас две одинаковые карты ({player_card1} и {player_card2})! Доступен СПЛИТ.{Colors.reset}")
            
            split_choice = input(f"\nРазделить карты на две руки за дополнительную ставку {Colors.yellow}{fmt(money_player)}{Colors.reset} монет? (Да/Нет): ").strip().lower()
            
            if split_choice in ('д', 'y', 'yes', 'да'):
                self._player.balance -= money_player

                new_card1 = random.choice(cards)
                new_card2 = random.choice(cards)
                
                player_hands = [
                    {"score": player_card1 + new_card1, "bet": money_player, "overflow": False},
                    {"score": player_card2 + new_card2, "bet": money_player, "overflow": False}
                ]

                print(f"\n{Colors.green}✂️ Карты разделены! Текущие руки:{Colors.reset}")
                print(f"Рука №1: {Colors.yellow}{player_hands[0]['score']}{Colors.reset} очков (карты: {player_card1} + {new_card1})")
                print(f"Рука №2: {Colors.yellow}{player_hands[1]['score']}{Colors.reset} очков (карты: {player_card2} + {new_card2})")

        for idx, hand in enumerate(player_hands):
            if len(player_hands) > 1:
                print(f"\n{Colors.blue}=== Разыгрывается Рука №{idx + 1} ==={Colors.reset}")

            while hand["score"] < 21:
                print(f'\nУ вас на руках: {Colors.yellow}{hand["score"]}{Colors.reset} очков')

                try:
                    user_choice = int(input('1. Взять ещё карту | 2. Остановиться: '))

                except ValueError:
                    print(f'\n{Colors.red}Ошибка! Введите 1 или 2.{Colors.reset}')
                    continue

                if user_choice == 1:
                    random_card = random.choice(cards)
                    hand["score"] += random_card

                    print(f'\nВы вытянули карту: {Colors.yellow}{random_card}{Colors.reset}')

                    if hand["score"] > 21:
                        print(f'\nУ вас на руках: {Colors.red}{hand["score"]}{Colors.reset} очков')
                        print(f'\n{Colors.red}💥 Перебор на этой руке!{Colors.reset}')
                        
                        hand["overflow"] = True
                        
                        break

                elif user_choice == 2:
                    break
                
                else:
                    print(f'\n{Colors.red}Неверный пункт! Выберите 1 или 2.{Colors.reset}\n')

            if hand["score"] == 21:
                print(f'\n🎉 {Colors.green}ОГО! На этой руке ровно 21 очко!{Colors.reset}')

        all_overflow = all(hand["overflow"] for hand in player_hands)

        if all_overflow and insurance_bet == 0:
            print(f'\n{Colors.red}💥 Все ваши руки сгорели. Вы проиграли раунд!{Colors.reset}')
            return

        print(f'\n{Colors.blue}🤖 Очередь Дилера (Бота)...{Colors.reset}\n')
        print(f'Стартовые очки бота: {Colors.blue}{bot_score}{Colors.reset} (карты: {Colors.blue}{bot_card1}{Colors.reset} и {Colors.blue}{bot_card2}{Colors.reset})\n')

        sleep(0.6)

        while bot_score < 17:
            bot_card = random.choice(cards)
            bot_score += bot_card
            
            print(f'🤖 Бот вытянул карту: {Colors.blue}{bot_card}{Colors.reset} (Всего у бота: {Colors.blue}{bot_score}{Colors.reset})\n')
            
            sleep(0.6)

        print(f'Финальный счёт дилера: {Colors.blue}{bot_score}{Colors.reset} очков\n')
        
        sleep(0.4)

        if insurance_bet > 0:
            is_dealer_blackjack = (bot_card1 + bot_card2 == 21)
            
            if is_dealer_blackjack:
                insurance_payout = insurance_bet * 3
                self._player.balance += insurance_payout
                
                print(f"\n💰 {Colors.green}Страховка сработала! У дилера Блекджек! Выплата: {fmt(insurance_payout)} монет.{Colors.reset}")
            
            else:
                print(f"🔴 {Colors.red}У дилера нет Блекджека на старте. Страховка сгорела.{Colors.reset}")

        level_multiplier = 1.0 + (self._player.lvl - 1) * 0.1

        for idx, hand in enumerate(player_hands):
            if len(player_hands) > 1:
                print(f"\n{Colors.blue}--- Итог по Руке №{idx + 1} ({hand['score']} очков) ---{Colors.reset}")

            if hand["overflow"]:
                print(f"{Colors.red}Эта рука проиграла из-за перебора.{Colors.reset}")
                continue

            if bot_score > 21 or hand["score"] > bot_score:
                reward_coins = int(
                    hand["bet"] * level_multiplier * self._player.balance_multiplier
                )
                reward_xp = self._player.xp_multiplier

                if bot_score > 21:
                    print(
                        f'🎉 {Colors.green}Бот перебрал ({bot_score} очков)! Вы победили!{Colors.reset}',
                        self._player.add_coins_and_xp(coins=reward_coins, xp=reward_xp),
                        sep='\n'
                        )
                else:
                    print(
                        f'🎉 {Colors.green}Вы победили дилера ({hand["score"]} vs {bot_score})!{Colors.reset}',
                        self._player.add_coins_and_xp(coins=reward_coins, xp=reward_xp),
                        sep='\n'
                        )

            elif hand["score"] == bot_score:
                self._player.balance += hand["bet"]
                print(f'{Colors.yellow}🤝 Ничья! Очков поровну ({hand["score"]} vs {bot_score}). Ставка возвращена.{Colors.reset}')
            
            else:
                print(f'{Colors.red}🔴 У дилера больше очков ({bot_score}). Ставка сгорела!{Colors.reset}')

        return
