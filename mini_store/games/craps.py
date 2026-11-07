import random
from time import sleep

from mini_store.colors import Colors
from mini_store.utils import ask_confirmation, cls, fmt

from .abstract import AbstractGame


class CrapsGame(AbstractGame):
    def _roll_dice_get_total(self) -> int:
        print('\n🎲 Незнакомец трясет стакан с костями...')

        sleep(0.8)

        dice = random.choices(range(1, 7), k=2)
        total = sum(dice)

        print(
            f'🎲 Результат броска: {Colors.yellow}[ {dice[0]} ] [ {dice[1]} ]{Colors.reset} -> {Colors.blue}{total} очков{Colors.reset}'
        )

        if (
            total == 12
            and self._ctx.daily.contract
            and 'сумму 12 в Костях' in self._ctx.daily.contract
            and not self._ctx.daily.completed
        ):
            self._ctx.daily.progress += 1
            print(f'\n{Colors.green}⭐ КВЕСТ ВЫПОЛНЕН: Вы выбросили заветные 6 и 6!{Colors.reset}')

        return total

    def play(self):
        cls()

        print(f'\n {Colors.yellow}== Игра: Кости (Craps) =={Colors.reset}\n')

        user_input = (
            input(
                f"Введите вашу ставку или 'all'/'все' (Ваш баланс: {Colors.yellow}{fmt(self._player.balance)}{Colors.reset} монет): "
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
                f"\n{Colors.red}Ошибка! Введите корректное число или слово 'all'/'все'.{Colors.reset}\n"
            )
            return

        if money_player <= 0:
            print(
                f'\n{Colors.red}Ошибка! Ставка {fmt(money_player)} монет невозможна! Нельзя играть на 0 или меньше.{Colors.reset}\n'
            )
            return

        elif money_player > self._player.balance:
            print(
                f'\n{Colors.red}Ошибка! Нельзя вводить ставку больше своего баланса!{Colors.reset}\n'
            )
            return

        self._player.balance -= money_player

        print(f'\n{Colors.blue}--- Первый раунд: Начальный бросок ---{Colors.reset}')

        input('\nНажмите Enter, чтобы бросить кости...')

        total = self._roll_dice_get_total()

        if total in (7, 11):
            reward_money = int(money_player * 1.5)
            reward_xp = 25

            print(
                f'\n🎉 {Colors.green}Натуральное число ({total})! Вы мгновенно победили дилера!{Colors.reset}'
            )
            print(self._player.add_coins_and_xp(coins=reward_money, xp=reward_xp))
            print()
            return

        elif total in (2, 3, 12):
            print(
                f'\n💥 {Colors.red}Крэпс ({total})! Автоматический проигрыш ставки. Повезет в следующий раз!{Colors.reset}\n'
            )
            return

        point = total

        print(f'\n📍 {Colors.purple}Установлена ТОЧКА: {point} очков.{Colors.reset}')
        print(
            f'Правила раунда: Чтобы победить, нужно выкинуть {Colors.yellow}{point}{Colors.reset} до того, как выпадет {Colors.red}7{Colors.reset}!'
        )

        roll_count = 1

        while True:
            roll_count += 1

            print(f'\n{Colors.blue}--- Бросок №{roll_count} ---{Colors.reset}')

            if not ask_confirmation('Готовы сделать следующий бросок кубиков?'):
                refund = int(money_player / 2)
                self._player.balance += refund

                print(
                    f'\n{Colors.yellow}🏳️  Вы решили сдаться. Вам возвращена половина ставки: {fmt(refund)} монет.{Colors.reset}\n'
                )
                return

            total = self._roll_dice_get_total()

            if total == point:
                reward_money = int(money_player * 1.5)
                reward_xp = 25

                print(
                    f'\n🎉 {Colors.green}Отлично! Вы выбили Точку ({point}) раньше, чем Семёрку! Победа!{Colors.reset}'
                )
                print(self._player.add_coins_and_xp(coins=reward_money, xp=reward_xp))
                print()
                return

            elif total == 7:
                print(
                    f'\n🔴 {Colors.red}Выпала Семёрка (Seven-Out)! Вы проиграли раунд и свою ставку.{Colors.reset}\n'
                )
                return

            else:
                print(f'\nНичья ({total}). Точка по-прежнему {point}. Продолжаем...')
