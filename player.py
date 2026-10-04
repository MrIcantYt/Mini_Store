from time import sleep

from colors import Colors
from utils import fmt

MAX_LEVEL = 100
XP_PER_LEVEL_MULTIPLIER = 100
GOLD_PER_XP = 2


class Player:
    def __init__(self):
        self.balance: int = 0
        self.balance_x2: bool = False
        self._xp: int = 0
        self.xp_x2: bool = False
        self.level: int = 1
        self.promo_used: bool = False
        self.lucky_amulet: bool = False
        self.secret_used: bool = False
        self.bought: int = 0
        self.mining_lvl: int = 0
        self.potion_luck: bool = False
        self.lucky_ticket: bool = False
        self.mining_boost: bool = False
        self.buy_num_boost: int = 0
        self.business: bool = False
        self.reset_num: int = 0
        self.rebirths: int = 0

    @property
    def xp(self):
        return self._xp

    @xp.setter
    def xp(self, value):
        self._xp = value
        self.check_level_up()

    @property
    def _xp_needed(self) -> int:
        return self.level * XP_PER_LEVEL_MULTIPLIER

    def check_level_up(self):
        """Проверяет и обрабатывает повышение уровня."""

        if self.level >= MAX_LEVEL:
            self._convert_xp_to_gold()

        while self._xp >= self._xp_needed:
            self._xp -= self._xp_needed
            self.level += 1

            print(
                f"{Colors.green}🎉 ПОЗДРАВЛЯЕМ! Вы достигли {self.level} уровня! 🎉 {Colors.reset}\n"
            )
            sleep(0.5)

            if self.level >= MAX_LEVEL:
                print(
                    f"{Colors.yellow}⭐ Вы достигли МАКСИМАЛЬНОГО {MAX_LEVEL} уровня! "
                    f"Теперь опыт превращается в монеты!{Colors.reset}\n"
                )
                self._convert_xp_to_gold()

    def _convert_xp_to_gold(self) -> None:
        """Конвертирует накопленный XP в золото на максимальном уровне."""
        if self._xp <= 0:
            return

        gold_bonus = self._xp * GOLD_PER_XP
        self.balance += gold_bonus

        print(
            f"{Colors.yellow}⭐ МАКСИМАЛЬНЫЙ УРОВЕНЬ! "
            f"{fmt(self._xp)} XP были конвертированы в "
            f"+{fmt(gold_bonus)} монет!{Colors.reset}\n"
        )
        self._xp = 0
