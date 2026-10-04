import random
from typing import Any

from colors import Colors
from player import Player
from utils import fmt

from .abstract import AbstractGame


class RockScissorsPaperGame(AbstractGame):
    def play(self, player: Player) -> Any:
        print(f'\n {Colors.yellow}== Игра: Камень, ножницы, бумага == {Colors.reset}\n')

        variants = ['камень', 'ножницы', 'бумага']

        life = 4 if player.lucky_amulet else 3

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
                # TODO: check 64-87 lines in guess_the_number.py. There is a similar reward calculation logic
                luck = random.randint(1, 100)
                chance = 35 if player.potion_luck else 15

                base_reward = 50 if luck <= chance else 25
                reward_xp = 20 * player.xp_multiplier

                level_multiplier = 1.0 + (player.lvl - 1) * 0.1
                reward_coins = int(base_reward * level_multiplier * player.balance_multiplier)

                if luck <= chance:
                    reward_xp *= 2

                    print(
                        '💥 КРИТИЧЕСКИЙ УДАР! Вы разнесли систему в пух и прах! Награда умножена!\n'
                    )

                print(
                    f'🎉 {Colors.green}Поздравляю! Вы победили! {Colors.reset}'
                    f'💰 Вы получили {Colors.yellow}{fmt(reward_coins)}{Colors.reset} монет (Множитель уровня: {Colors.yellow}{level_multiplier:.1f}x{Colors.reset})!'
                    f'📈 Вам начислено {Colors.yellow}{fmt(reward_xp)}{Colors.reset} XP!\n'
                )

                return

            elif user_choice == bot_choice:
                print(f'{Colors.yellow}Ничья! Продолжаем... {Colors.reset}\n')

            else:
                life -= 1

                if player.lucky_ticket:
                    player.lucky_ticket = False
                    life += 1

                    print(
                        f'🎫 {Colors.yellow}Счастливый тикет сработал и спас вашу жизнь!{Colors.reset}\n'
                    )

                print(f'Вы не угадали! У вас осталось {life} жизни!\n')

                if life == 0:
                    print(f'{Colors.red}Вы полностью проиграли в этой игре! {Colors.reset}\n')

        return
