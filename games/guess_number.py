import random

from colors import Colors
from player import Player
from utils import fmt

from .abstract import AbstractGame

TO_RANGE = {1: 15, 2: 25, 3: 50}
WIN_BASE_REWARDS = {1: 25, 2: 50, 3: 75}


class GuessNumber(AbstractGame):
    def __init__(self):
        self._level_choose: int = 0
        self._to_range: int = 0
        self._guess_number: int = 0

    def _choose_level(self) -> int:
        while True:
            try:
                level_choose = int(
                    input(
                        f"Выберите сложность: {Colors.green}Лёгкая (1){Colors.reset}\n{Colors.yellow}Средняя (2){Colors.reset}\n{Colors.red}Сложная (3){Colors.reset}: "
                    )
                )
            except ValueError:
                print(
                    f"\n{Colors.red}Ошибка! Выбрана несуществующая сложность.{Colors.reset}\n"
                )
                continue

            if level_choose not in TO_RANGE:
                print(
                    f"\n{Colors.red}Ошибка! Выбрана несуществующая сложность.{Colors.reset}\n"
                )
                continue
            return level_choose

    def play(self, player: Player):
        print(f"\n {Colors.yellow}== Игра: Угадай число == {Colors.reset}\n")

        try:
            self._level_choose = self._choose_level()
            self._to_range = TO_RANGE[self._level_choose]
            self._guess_number = random.randint(1, self._to_range)
            life = 4 if player.lucky_amulet else 3

            while life > 0:
                user_number = int(input(f"Введите число (От 1 до {self._to_range}): "))

                if user_number < 1 or user_number > self._to_range:
                    print(
                        f"\n{Colors.red}Ошибка! Введите число в диапазоне от 1 до {self._to_range}.{Colors.reset}\n"
                    )
                    continue

                if player.lucky_ticket:
                    player.lucky_ticket = False
                    print(
                        f"\n🎫 {Colors.yellow}Счастливый тикет сработал и спас вашу жизнь!{Colors.reset}"
                    )
                else:
                    life -= 1

                if user_number == self._guess_number:
                    # Calculate multipliers
                    level_multiplier = 1.0 + (player.lvl - 1) * 0.1
                    xp_multiplier = 2 if player.xp_x2 else 1

                    # Will be surcharged
                    luck = random.randint(1, 100)
                    win_chance = 35 if player.potion_luck else 15
                    is_surcharged = luck <= win_chance
                    surcharge_factor = 2 if is_surcharged else 1

                    # Calculate rewards
                    base = WIN_BASE_REWARDS[self._level_choose]
                    reward_base = base * surcharge_factor
                    reward_xp = reward_base * xp_multiplier
                    reward_coins = int(
                        reward_base * level_multiplier * surcharge_factor
                    )

                    if is_surcharged:
                        print(
                            "\n💥 КРИТИЧЕСКИЙ УДАР! Вы разнесли систему в пух и прах! Награда умножена!"
                        )

                    print(
                        f"\n🎉 {Colors.green}Поздравляю! Вы победили! {Colors.reset}\n"
                        f"💰 Вы получили {Colors.yellow}{fmt(reward_coins)}{Colors.reset} монет "
                        f"(Множитель уровня: {Colors.yellow}{level_multiplier:.1f}x{Colors.reset})!\n"
                        f"📈 Вам начислено {Colors.yellow}{fmt(reward_xp)}{Colors.reset} XP!\n"
                    )

                    return

                elif life == 0:
                    print(
                        f"\n{Colors.red}Вы програли! Загаданное число было: {self._guess_number}. {Colors.reset}\n"
                    )
                    return

                elif user_number > self._guess_number:
                    print(f"\nЗагаданное число меньше! Осталось жизней: {life}\n")

                elif user_number < self._guess_number:
                    print(f"\nЗагаданное число больше! Осталось жизней: {life}\n")

            return

        except (ValueError, TypeError):
            print(f"\n{Colors.red}Ошибка! Введите корректное число. {Colors.reset}\n")

            return
