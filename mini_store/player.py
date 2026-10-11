from dataclasses import asdict, dataclass, fields
from random import randint
from typing import NamedTuple

from mini_store.colors import Colors
from mini_store.utils import fmt

MAX_LEVEL = 100
MAX_BALANCE = 1_000_000
XP_PER_LEVEL_MULTIPLIER = 100
GOLD_PER_XP = 2
BOOL_FIELDS = frozenset(
    {
        'promo_used',
        'lucky_amulet',
        'secret_used',
        'potion_luck',
        'lucky_ticket',
        'business',
    }
)


class Converted(NamedTuple):
    xp_converted: int
    gold: int


@dataclass(slots=True)
class Player:
    id: int
    _balance: int = 0
    balance_multiplier: int = 1
    xp: int = 0
    xp_multiplier: int = 1
    lvl: int = 1
    promo_used: bool = False
    lucky_amulet: bool = False
    secret_used: bool = False
    bought: int = 0
    mining_lvl: int = 0
    mining_multiplier: int = 1
    potion_luck: bool = False
    lucky_ticket: bool = False
    buy_num_boost: int = 0
    business: bool = False
    secret_case: int = 0
    quest_id: int = 1
    quest_progress: int = 0
    rebirths: int = 0

    def to_row(self) -> dict[str, object]:
        data = self.to_dict()
        data.pop('id')
        return data

    @classmethod
    def from_row(cls, row) -> 'Player':
        data = {f.name: row[f.name] for f in fields(cls)}
        for name in BOOL_FIELDS:
            data[name] = bool(data[name])
        return cls(**data)

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data['balance'] = data.pop('_balance')
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> 'Player':
        data['_balance'] = data.pop('balance')
        return cls(**data)  # pyright: ignore[reportArgumentType]  # ty: ignore[invalid-argument-type]

    @property
    def balance(self) -> int:
        return self._balance

    @balance.setter
    def balance(self, value: int):
        self._balance = min(value, MAX_BALANCE)

    @property
    def next_lvl_xp_needed(self) -> int:
        return self.lvl * XP_PER_LEVEL_MULTIPLIER

    @property
    def level_multiplier(self) -> float:
        return 1.0 + (self.lvl - 1) * 0.1

    def add_coins(self, amount: int) -> str:
        final_amount = int(amount * self.balance_multiplier * self.level_multiplier)
        self.balance += final_amount
        return f'💰 Вы получили {Colors.yellow}{fmt(final_amount)}{Colors.reset} монет ({Colors.yellow}{fmt(self.balance)}{Colors.reset} монет на счету)'

    def add_xp(self, amount: int) -> str:
        final_amount = int(amount * self.xp_multiplier * self.level_multiplier)
        self.xp += final_amount
        return f'📈 Вам начислено {Colors.yellow}{fmt(final_amount)}{Colors.reset} XP ({Colors.yellow}{fmt(self.xp)}{Colors.reset} XP на счету)\n{self.check_level_up()}'

    def add_coins_and_xp(self, *, coins: int, xp: int) -> str:
        return self.add_coins(coins) + '\n' + self.add_xp(xp)

    def check_level_up(self) -> str | None:
        """Checks for and applies any pending level-ups.

        Consumes XP from the player until the level-up threshold is no
        longer met or the maximum level is reached. If the maximum level
        is reached, remaining XP is converted to gold via `_convert_xp_to_gold`.

        Returns:
            str | None: A message describing the level-up, or None if the level did not change.
        """
        if self.lvl >= MAX_LEVEL:
            return None

        start_level = self.lvl

        while self.xp >= self.next_lvl_xp_needed and self.lvl < MAX_LEVEL:
            self.xp -= self.next_lvl_xp_needed
            self.lvl += 1

        if self.lvl == start_level:
            return None

        if self.lvl >= MAX_LEVEL:
            xp_converted, gold = self._convert_xp_to_gold()
            return (
                f'{Colors.yellow}⭐ Вы достигли МАКСИМАЛЬНОГО {MAX_LEVEL} уровня!\n'
                f'{fmt(xp_converted)} XP были конвертированы в '
                f'+{fmt(gold)} монет!{Colors.reset}\n'
            )

        return f'{Colors.green}🎉 ПОЗДРАВЛЯЕМ! Вы достигли {self.lvl} уровня! 🎉{Colors.reset}\n'

    def _convert_xp_to_gold(self) -> Converted:
        """Converts accumulated XP into gold at the maximum level.

        Resets `self.xp` to 0 and adds the converted amount to `self.balance`.

        Returns:
            Converted: A pair (xp_converted, gold). Both are 0 if there was no XP to convert.
        """
        if self.xp <= 0:
            return Converted(0, 0)

        xp_converted = self.xp
        gold = xp_converted * GOLD_PER_XP
        self.balance += gold
        self.xp = 0
        return Converted(xp_converted, gold)

    def check_luck(self) -> bool:
        return randint(1, 100) <= (35 if self.potion_luck else 15)
