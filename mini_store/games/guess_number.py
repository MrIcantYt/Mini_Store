from enum import Enum
from random import randint

from mini_store.colors import Colors
from mini_store.context import GameContext
from mini_store.utils import cls
from mini_store.utils.ask_functions import Option, ask_number, ask_option

from .abstract import AbstractGame


class Levels(Enum):
    easy = (15, 25, 'Лёгкая', Colors.green)
    middle = (25, 50, 'Средняя', Colors.yellow)
    hard = (50, 75, 'Сложная', Colors.red)

    def __init__(self, to_range: int, win_base_reward: int, title: str, color: Colors):
        self.to_range = to_range
        self.win_reward = win_base_reward
        self.title = title
        self.color = color


class GuessNumberGame(AbstractGame):
    def __init__(self, ctx: GameContext):
        self._ctx = ctx
        self._player = ctx.player

    def play(self):
        cls()
        print(f'{Colors.yellow}=== Игра: Угадай число ==={Colors.reset}\n')

        level_choose = ask_option(
            'Выберите сложность: ', [Option(l.title, l, color=l.color) for l in Levels]
        )

        if level_choose is None:
            return

        guess_number = randint(1, level_choose.to_range)

        life = 4 if self._player.lucky_amulet else 3

        if self._player.lucky_ticket:
            life += 1
            print(f'\nТак как у вас имеется {Colors.yellow}счастливый билет{Colors.reset}, вам {Colors.yellow}+1{Colors.reset} жизнь.\n')

        while life > 0:
            user_number = ask_number(
                f'Введите число (От 1 до {level_choose.to_range}): ',
                max=level_choose.to_range,
            )

            if user_number is None:
                return

            life -= 1

            if user_number == guess_number:
                cls()
                is_win = self._player.check_luck()
                reward = level_choose.win_reward

                if is_win:
                    reward *= 2
                    print(
                        '\n💥 КРИТИЧЕСКИЙ УДАР! Вы разнесли систему в пух и прах! Награда умножена!'
                    )

                print(
                    f'\n🎉 {Colors.green}Поздравляю! Вы победили! {Colors.reset}\n{self._player.add_coins_and_xp(coins=reward, xp=reward)}\n',
                )

                break

            elif life == 0:
                cls()
                print(
                    f'\n{Colors.red}Вы програли! Загаданное число было: {guess_number}.{Colors.reset}\n'
                )

                break

            else:
                print(
                    f'\nЗагаданное число {"меньше" if user_number > guess_number else "больше"}! Осталось жизней: {life}\n'
                )
