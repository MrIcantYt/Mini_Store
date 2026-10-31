import random
from typing import Any

from mini_store.colors import Colors

from .abstract import AbstractGame


class RockScissorsPaperGame(AbstractGame):
    def play(self) -> Any:
        print(f'\n {Colors.yellow}== Игра: Камень, ножницы, бумага == {Colors.reset}\n')

        ticket = self._player.lucky_ticket
        variants = ['камень', 'ножницы', 'бумага']
        life = 4 if self._player.lucky_amulet else 3

        if ticket:
            life += 1
            print(
                f'Так как у вас имеется {Colors.yellow}счастливый билет{Colors.reset}, вам {Colors.yellow}+1{Colors.reset} жизнь.\n'
            )

        while life > 0:
            user_choice = input('Выберите (Камень, Ножницы, Бумага): ').lower().strip()

            if user_choice not in variants:
                print(
                    f'\n{Colors.red}Неверный выбор! Напишите: камень, ножницы или бумага. {Colors.reset}\n'
                )
                continue

            bot_choice = random.choice(variants)

            print(f'\nБот выбрал: {bot_choice}\n')

            if (
                (user_choice == 'камень' and bot_choice == 'ножницы')
                or (user_choice == 'ножницы' and bot_choice == 'бумага')
                or (user_choice == 'бумага' and bot_choice == 'камень')
            ):
                luck = random.randint(1, 100)
                chance = 35 if self._player.potion_luck else 15
                is_win = luck <= chance

                reward = 25

                if is_win:
                    reward *= 2

                    print(
                        '💥 КРИТИЧЕСКИЙ УДАР! Вы разнесли систему в пух и прах! Награда умножена!\n'
                    )

                print(
                    f'🎉 {Colors.green}Поздравляю! Вы победили! {Colors.reset}\n'
                    f'{self._player.add_coins_and_xp(coins=reward, xp=reward)}\n'
                )

                return

            elif user_choice == bot_choice:
                print(f'{Colors.yellow}Ничья! Продолжаем... {Colors.reset}\n')

            else:
                life -= 1

                print(f'Вы не угадали! У вас осталось {life} жизни!\n')

                if life == 0:
                    print(
                        f'{Colors.red}Вы полностью проиграли в этой игре! {Colors.reset}'
                    )

        return
