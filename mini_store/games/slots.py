import random
from enum import Enum
from time import sleep

from mini_store.colors import Colors
from mini_store.models import GameContext
from mini_store.utils import cls, fmt

from .abstract import AbstractGame


class Slot(Enum):
    SEVEN = (
        '7',
        30,
        240,
        f'{Colors.green}7 ТРИ СЕМЁРКИ В РЯД! У вас выпали три СЕМЁРКИ В РЯД! 7{Colors.reset}',
        f'{Colors.green}7 ЛЕГЕНДАРНЫЕ ТРИ СЕМЁРКИ В РЯД! 60x МНОЖИТЕЛЬ СРАБОТАЛ! 7{Colors.reset}',
    )
    SACK_MONEY = (
        '💰',
        15,
        120,
        f'{Colors.green}💰 ЧТО В МЕШОЧКЕ? У вас выпали три МЕШКА С ДЕНЬГАМИ! 💰{Colors.reset}',
        f'{Colors.green}💰 ЛЕГЕНДАРНЫЕ ТРИ МЕШКА! 30x МНОЖИТЕЛЬ СРАБОТАЛ! 💰{Colors.reset}',
    )
    CROWN = (
        '👑',
        7,
        60,
        f'{Colors.green}🔥 ДЖЕКПОТ! У вас выпали три КОРОНЫ! 🔥{Colors.reset}',
        f'{Colors.green}🔥 ЛЕГЕНДАРНЫЙ VIP-ДЖЕКПОТ! 14x МНОЖИТЕЛЬ СРАБОТАЛ! 🔥{Colors.reset}',
    )
    DIAMOND = (
        '💎',
        4,
        40,
        f'{Colors.green}💎 КРИСТАЛЛЫ! Отличная комбинация! {Colors.reset}',
        f'{Colors.green}💎 VIP-КРИСТАЛЛЫ! Отличная комбинация хайроллера! {Colors.reset}',
    )
    CHERRY = (
        '🍒',
        2,
        20,
        f'{Colors.green}🍒 Обычный выигрыш! Три вишни в ряд! {Colors.reset}',
        f'{Colors.green}🍒 VIP-Выигрыш на вишнях! Награда увеличена в 4х! {Colors.reset}',
    )

    symbol: str
    coins_reward: int
    xp_reward: int
    msg: str
    vip_msg: str

    def __init__(
        self,
        symbol: str,
        win_reward: int,
        xp_reward: int,
        msg: str,
        vip_msg: str,
    ):
        self.symbol = symbol
        self.coins_reward = win_reward
        self.xp_reward = xp_reward
        self.msg = msg
        self.vip_msg = vip_msg

    def __str__(self):
        return self.symbol


class SlotsGame(AbstractGame):
    def __init__(self, ctx: GameContext) -> None:
        super().__init__(ctx)

        self._variants = self._setup_variants()
        self._slots = random.choices(self._variants, k=3)
        self._is_vip = False

    def _setup_variants(self) -> list[Slot]:
        variants = [
            Slot.CHERRY,
            Slot.CHERRY,
            Slot.CHERRY,
            Slot.CHERRY,
            Slot.CHERRY,
            Slot.DIAMOND,
            Slot.DIAMOND,
            Slot.CROWN,
        ]
        if self._player.potion_luck:
            variants.extend([Slot.DIAMOND, Slot.CROWN, Slot.SACK_MONEY, Slot.SEVEN])
        return variants

    def _all_slots_is(self) -> Slot | None:
        set_ = set(self._slots)
        return next(iter(set_)) if len(set_) == 1 else None

    def play(self):
        cls()

        print(f'\n {Colors.yellow}== Игра: Игровой Автомат =={Colors.reset}\n')

        user_bet = (
            input(
                f"Введите вашу ставку или 'all'/'все' (Ваш баланс: {Colors.yellow}{fmt(self._player.balance)}{Colors.reset} монет): "
            )
            .strip()
            .lower()
        )

        try:
            if user_bet in ['all', 'все']:
                money_player = self._player.balance

            else:
                money_player = int(user_bet)

        except ValueError:
            cls()

            print(
                f"\n{Colors.red}Ошибка! Введите корректное число или слово 'all'/'все'.{Colors.reset}\n"
            )
            return

        if money_player <= 0:
            cls()

            print(
                f'\n{Colors.red}Ошибка! Ставка {fmt(self._player.balance)} монет невозможна! Нельзя играть на 0 или меньше.{Colors.reset}\n'
            )
            return

        elif money_player > self._player.balance:
            cls()

            print(
                f'\n{Colors.red}Ошибка! Нельзя вводить ставку больше своего баланса! {Colors.reset}\n'
            )
            return

        if money_player == 777 and self._player.balance >= 777:
            self._is_vip = True

            print(
                f'\n{Colors.yellow}⚡ ВНИМАНИЕ! Активирован VIP-режим ХАЙРОЛЛЕРА «777»!⚡{Colors.reset}\n'
                f'{Colors.red}Ставки максимальны. Риск удвоен. Выигрыш колоссален!{Colors.reset}\n'
                '\n| 🎰 БAРAБAНЫ VIP-AВТОМAТA СТРЕМИТЕЛЬНО ВРAЩАЮТСЯ... 🎰 |'
            )

        else:
            print('\n| 🎰 БAРAБAНЫ КРУТЯТСЯ... 🎰 |')

        self._player.balance -= money_player

        sleep(0.4)
        print(f'[{self._slots[0]}]')
        sleep(0.4)
        print(f'[{self._slots[0]}] [{self._slots[1]}]')
        sleep(0.4)
        print(f'[{self._slots[0]}] [{self._slots[1]}] [{self._slots[2]}]\n')
        sleep(0.4)

        if self._player.quest_id == 3:
            self._player.quest_progress += 1

        if slot := self._all_slots_is():  # win
            win_coins = slot.coins_reward * money_player
            win_xp = slot.xp_reward
            msg = slot.msg

            if self._is_vip:
                win_coins *= 2
                win_xp *= 2
                msg = slot.vip_msg

            print(msg, self._player.add_coins_and_xp(coins=win_coins, xp=win_xp), end='\n\n')
            return

        if self._is_vip:
            print(
                f'{Colors.red}💥 КРАХ ХАЙРОЛЛЕРА! Слот заблокирован. С вашего баланса списан ДВОЙНОЙ штраф за риск!{Colors.reset}'
            )

            self._player.balance -= money_player
            return

        print('🔴 Увы, комбинация пустая. Вы потеряли свою ставку. Попробуйте еще раз!\n')
