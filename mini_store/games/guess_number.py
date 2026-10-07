import random

from mini_store.colors import Colors

from .abstract import AbstractGame

TO_RANGE = {1: 15, 2: 25, 3: 50}
WIN_BASE_REWARDS = {1: 25, 2: 50, 3: 75}


class GuessNumberGame(AbstractGame):
    def _choose_level(self) -> int:
        while True:
            try:
                level_choose = int(
                    input(
                        f'Выберите сложность: {Colors.green}\nЛёгкая (1){Colors.reset}\n{Colors.yellow}Средняя (2){Colors.reset}\n{Colors.red}Сложная (3){Colors.reset}\n: '
                    )
                )
            except ValueError:
                print(
                    f'\n{Colors.red}Ошибка! Выбрана несуществующая сложность.{Colors.reset}\n'
                )
                continue

            if level_choose not in TO_RANGE:
                print(
                    f'\n{Colors.red}Ошибка! Выбрана несуществующая сложность.{Colors.reset}\n'
                )
                continue
            return level_choose

    def play(self):
        print(f'\n {Colors.yellow}== Игра: Угадай число == {Colors.reset}\n')

        try:
            level_choose = self._choose_level()
            to_range = TO_RANGE[level_choose]
            guess_number = random.randint(1, to_range)

            life = 4 if self._player.lucky_amulet else 3

            while life > 0:
                user_number = int(
                    input(f'Введите число (От 1 до {to_range}): ')
                )

                if user_number < 1 or user_number > to_range:
                    print(
                        f'\n{Colors.red}Ошибка! Введите число в диапазоне от 1 до {to_range}.{Colors.reset}\n'
                    )
                    continue

                if self._player.lucky_ticket:
                    self._player.lucky_ticket = False
                    print(
                        f'\n🎫 {Colors.yellow}Счастливый тикет сработал и спас вашу жизнь!{Colors.reset}'
                    )
                else:
                    life -= 1

                if user_number == guess_number:
                    luck = random.randint(1, 100)
                    win_chance = 35 if self._player.potion_luck else 15
                    is_win = luck <= win_chance
                    reward = WIN_BASE_REWARDS[level_choose]

                    if is_win:
                        reward *= 2
                        print(
                            '\n💥 КРИТИЧЕСКИЙ УДАР! Вы разнесли систему в пух и прах! Награда умножена!'
                        )

                    print(
                        f'\n🎉 {Colors.green}Поздравляю! Вы победили! {Colors.reset}',
                        self._player.add_coins_and_xp(coins=reward, xp=reward),
                        '',
                        sep='\n',
                    )

                    return

                elif life == 0:
                    print(
                        f'\n{Colors.red}Вы програли! Загаданное число было: {guess_number}. {Colors.reset}\n'
                    )
                    return

                elif user_number > guess_number:
                    print(
                        f'\nЗагаданное число меньше! Осталось жизней: {life}\n'
                    )

                elif user_number < guess_number:
                    print(
                        f'\nЗагаданное число больше! Осталось жизней: {life}\n'
                    )

            return

        except (ValueError, TypeError):
            print(
                f'\n{Colors.red}Ошибка! Введите корректное число. {Colors.reset}\n'
            )

            return
