from dataclasses import asdict, dataclass, fields
from time import sleep

from colors import Colors
from utils import fmt

MAX_LEVEL = 100
XP_PER_LEVEL_MULTIPLIER = 100
GOLD_PER_XP = 2
BOOL_FIELDS = frozenset(
    {
        'promo_used',
        'lucky_amulet',
        'secret_used',
        'potion_luck',
        'lucky_ticket',
        'mining_boost',
        'business',
    }
)


@dataclass(slots=True)
class Player:
    id: int
    balance: int = 0
    balance_multiplier: int = 1
    _xp: int = 0
    xp_multiplier: int = 1
    lvl: int = 1
    promo_used: bool = False
    lucky_amulet: bool = False
    secret_used: bool = False
    bought: int = 0
    mining_lvl: int = 0
    potion_luck: bool = False
    lucky_ticket: bool = False
    mining_boost: bool = False
    buy_num_boost: int = 0
    business: bool = False
    reset_num: int = 0
    secret_case: int = 0
    rebirths: int = 0

    def to_row(self) -> dict[str, object]:
        data = asdict(self)

        data.pop('id')
        return data

    @classmethod
    def from_row(cls, row) -> "Player":
        data = {f.name: row[f.name] for f in fields(cls)}
        for name in BOOL_FIELDS:
            data[name] = bool(data[name])
        return cls(**data)

    @property
    def xp(self):
        return self._xp

    @xp.setter
    def xp(self, value):
        self._xp = value
        self.check_level_up()

    @property
    def _xp_needed(self) -> int:
        return self.lvl * XP_PER_LEVEL_MULTIPLIER

    def check_level_up(self):
        """Проверяет и обрабатывает повышение уровня."""

        if self.lvl >= MAX_LEVEL:
            self._convert_xp_to_gold()

        while self._xp >= self._xp_needed:
            self._xp -= self._xp_needed
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
        if self._xp <= 0:
            return

        gold_bonus = self._xp * GOLD_PER_XP
        self.balance += gold_bonus

        print(
            f'{Colors.yellow}⭐ МАКСИМАЛЬНЫЙ УРОВЕНЬ! '
            f'{fmt(self._xp)} XP были конвертированы в '
            f'+{fmt(gold_bonus)} монет!{Colors.reset}\n'
        )
        self._xp = 0
