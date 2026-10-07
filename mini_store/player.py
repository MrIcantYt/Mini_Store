from dataclasses import asdict, dataclass, fields
from time import sleep

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


@dataclass(slots=True)
class Player:
    id: int
    _balance: int = 0
    balance_multiplier: int = 1
    _xp: int = 0
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
        data['_xp'] = data.pop('xp')
        for name in BOOL_FIELDS:
            data[name] = bool(data[name])
        return cls(**data)

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data['xp'] = data.pop('_xp')
        data['balance'] = data.pop('_balance')
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> 'Player':
        data['_xp'] = data.pop('xp')
        data['_balance'] = data.pop('balance')
        return cls(**data)  # pyright: ignore[reportArgumentType]

    @property
    def xp(self) -> int:
        return self._xp

    @xp.setter
    def xp(self, value):
        self._xp = value
        self.check_level_up()

    @property
    def balance(self) -> int:
        return self._balance

    @balance.setter
    def balance(self, value):
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
        return f'📈 Вам начислено {Colors.yellow}{fmt(final_amount)}{Colors.reset} XP ({Colors.yellow}{fmt(self._xp)}{Colors.reset} XP на счету)'

    def add_coins_and_xp(self, *, coins: int, xp: int) -> str:
        return self.add_coins(coins) + '\n' + self.add_xp(xp)

    def check_level_up(self):
        """Проверяет и обрабатывает повышение уровня."""

        if self.lvl >= MAX_LEVEL:
            self._convert_xp_to_gold()

        while self._xp >= self.next_lvl_xp_needed:
            self._xp -= self.next_lvl_xp_needed
            self.lvl += 1

            print(
                f'{Colors.green}🎉 ПОЗДРАВЛЯЕМ! Вы достигли {self.lvl} уровня! 🎉 {Colors.reset}\n'
            )
            sleep(0.5)

            if self.lvl >= MAX_LEVEL:
                print(
                    f'{Colors.yellow}⭐ Вы достигли МАКСИМАЛЬНОГО {MAX_LEVEL} уровня! '
                    f'Теперь опыт превращается в монеты!{Colors.reset}\n'
                )
                self._convert_xp_to_gold()

    def _convert_xp_to_gold(self) -> None:
        """Конвертирует накопленный XP в золото на максимальном уровне."""
        if self.xp <= 0:
            return

        gold_bonus = self.xp * GOLD_PER_XP
        self.balance += gold_bonus

        print(
            f'{Colors.yellow}⭐ МАКСИМАЛЬНЫЙ УРОВЕНЬ! '
            f'{fmt(self.xp)} XP были конвертированы в '
            f'+{fmt(gold_bonus)} монет!{Colors.reset}\n'
        )
        self.xp = 0
