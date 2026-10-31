import random
from time import sleep
from typing import Any

from mini_store.colors import Colors
from mini_store.context import GameContext
from mini_store.utils import ask_confirmation, fmt

from .abstract import AbstractGame


class CrapsGame(AbstractGame):
    def __init__(self, ctx: GameContext):
        super().__init__(ctx.player)
        self._ctx = ctx
        self._player = ctx.player

    def _roll_dice(self) -> tuple[int, int]:
        print("\n🎲 Незнакомец трясет стакан с костями...")
        
        sleep(0.8)
        
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)

        print(f"🎲 Результат броска: {Colors.yellow}[ {die1} ] [ {die2} ]{Colors.reset} -> {Colors.blue}{die1 + die2} очков{Colors.reset}")
        return die1, die2

    def play(self) -> Any:
        print(f'\n {Colors.yellow}== Игра: Кости (Craps) =={Colors.reset}\n')

        user_input = (
            input(f"Введите вашу ставку или 'all'/'все' (Ваш баланс: {Colors.yellow}{fmt(self._player.balance)}{Colors.reset} монет): ")
            .strip()
            .lower()
        )

        try:
            if user_input == 'all' or user_input == 'все':
                money_player = self._player.balance
            else:
                money_player = int(user_input)

        except ValueError:
            print(f"\n{Colors.red}Ошибка! Введите корректное число или слово 'all'/'все'.{Colors.reset}\n")
            return

        if money_player <= 0:
            print(f'\n{Colors.red}Ошибка! Ставка {fmt(money_player)} монет невозможна! Нельзя играть на 0 или меньше.{Colors.reset}\n')
            return

        elif money_player > self._player.balance:
            print(f'\n{Colors.red}Ошибка! Нельзя вводить ставку больше своего баланса!{Colors.reset}\n')
            return

        self._player.balance -= money_player

        print(f"\n{Colors.blue}--- Первый раунд: Начальный бросок ---{Colors.reset}")

        input("\nНажмите Enter, чтобы бросить кости...")
        
        d1, d2 = self._roll_dice()
        total = d1 + d2

        if total in (7, 11):
            reward_money = int(money_player * 1.5)
            reward_xp = 25
            
            print(f"\n🎉 {Colors.green}Натуральное число ({total})! Вы мгновенно победили дилера!{Colors.reset}")
            print(self._player.add_coins_and_xp(coins=reward_money, xp=reward_xp))
            print()
            return

        elif total in (2, 3, 12):
            print(f"\n💥 {Colors.red}Крэпс ({total})! Автоматический проигрыш ставки. Повезет в следующий раз!{Colors.reset}\n")
            return

        point = total

        print(f"\n📍 {Colors.purple}Установлена ТОЧКА: {point} очков.{Colors.reset}")
        print(f"Правила раунда: Чтобы победить, нужно выкинуть {Colors.yellow}{point}{Colors.reset} до того, как выпадет {Colors.red}7{Colors.reset}!")

        roll_count = 1

        while True:
            roll_count += 1

            print(f"\n{Colors.blue}--- Бросок №{roll_count} ---{Colors.reset}")
            
            if not ask_confirmation("Готовы сделать следующий бросок кубиков?"):
                refund = int(money_player / 2)
                self._player.balance += refund
                
                print(f"\n{Colors.yellow}🏳️  Вы решили сдаться. Вам возвращена половина ставки: {fmt(refund)} монет.{Colors.reset}\n")
                return

            d1, d2 = self._roll_dice()
            current_total = d1 + d2

            if current_total == point:
                reward_money = int(money_player * 1.5) 
                reward_xp = 25
                
                print(f"\n🎉 {Colors.green}Отлично! Вы выбили Точку ({point}) раньше, чем Семёрку! Победа!{Colors.reset}")
                print(self._player.add_coins_and_xp(coins=reward_money, xp=reward_xp))
                print()
                return

            elif current_total == 7:
                print(f"\n🔴 {Colors.red}Выпала Семёрка (Seven-Out)! Вы проиграли раунд и свою ставку.{Colors.reset}\n")
                return
            
            else:
                print(f"\nНичья ({current_total}). Точка по-прежнему {point}. Продолжаем...")
