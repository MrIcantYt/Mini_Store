import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import IntEnum
from functools import partial
from typing import ClassVar

from mini_store.colors import Colors
from mini_store.context import GameContext
from mini_store.player import Player
from mini_store.utils import Option, ask_confirmation, ask_number, ask_option, cls, fmt

type BuyHandler = Callable[[int], None]
type SellHandler = Callable[[], None]


@dataclass(frozen=True, slots=True)
class ShopItem:
    id: int
    name: str
    price: int | None


class ShopAction(IntEnum):
    BUY = 1
    RETURN = 2


class Shop:
    """Каталог Незнакомца: покупка и возврат товаров."""

    DISCOUNT_CHANCE: ClassVar[float] = 0.15
    DISCOUNT_RATE: ClassVar[float] = 0.8
    CASE_DROPS: ClassVar[dict[int, str]] = {
        1250: f'{Colors.red}Эх, Незнакомец подсунул дешёвку. Повезёт в следующий раз!{Colors.reset}\n',
        2500: f'{Colors.yellow}Нормально, вернули своё!{Colors.reset}\n',
        5000: f'{Colors.green}🔥 ЛУЧШИЙ ДРОП! Вы сорвали куш кейса!{Colors.reset}\n',
    }

    def __init__(self, ctx: GameContext) -> None:
        self.ctx = ctx
        self.player: Player = ctx.player
        self.catalog = self._build_catalog()
        self.catalog_by_id = {item.id: item for item in self.catalog}

        self._buy_handlers: dict[int, BuyHandler] = {
            1: self._buy_balance_multiplier,
            2: self._buy_xp_multiplier,
            3: partial(self._buy_flag, 'lucky_amulet', 'Счастливый Амулет (+1 жизнь)!'),
            4: self._buy_mining,
            5: partial(
                self._buy_flag,
                'potion_luck',
                'Счастливое Зелье (Больше шансов в Казино)!',
            ),
            6: partial(
                self._buy_flag,
                'lucky_ticket',
                'Счастливый Тикет (Не вычитается жизнь при первой попытке)!',
            ),
            7: self._buy_coffee,
            8: self._buy_business,
            9: self._buy_secret_case,
        }

        self._sell_handlers: dict[int, SellHandler] = {
            1: partial(self._sell_multiplier, 'balance_multiplier', 'x5 бонус к монетам'),
            2: partial(self._sell_multiplier, 'xp_multiplier', 'x5 бонус к опыту'),
            3: partial(self._sell_flag, 'lucky_amulet', 150, 'Счастливый Амулет'),
            4: self._sell_mining,
            5: partial(self._sell_flag, 'potion_luck', 250, 'Зелье Удачи'),
            6: partial(self._sell_flag, 'lucky_ticket', 200, 'Счастливый Тикет'),
            7: self._sell_coffee,
            8: self._sell_business,
            9: self._sell_secret_case,
        }

    def open(self) -> None:
        cls()
        print(f'\n{Colors.blue}🛒 Добро пожаловать в Каталог Незнакомца!{Colors.reset}\n')

        self._roll_discount()
        print(
            f'Ваш баланс: {Colors.yellow}{fmt(self.player.balance)} монет{Colors.reset}.\n\n{"=" * 30}'
        )

        item = self._choose_item()
        if item is None:
            cls()
            return

        action = self._choose_action()
        if action is None:
            cls()
            return

        if action is ShopAction.BUY:
            self._buy(item)
        else:
            self._return(item)

    def _build_catalog(self) -> list[ShopItem]:
        player = self.player

        balance_price = (
            100 * 2**player.balance_multiplier if player.balance_multiplier < 5 else None
        )
        xp_price = 100 * 2**player.xp_multiplier if player.xp_multiplier < 5 else None
        mining_price = 300 * (player.mining_lvl + 1) if player.mining_lvl < 10 else None

        return [
            ShopItem(1, f'Множитель монет {player.balance_multiplier}x', balance_price),
            ShopItem(2, f'Множитель опыта {player.xp_multiplier}x', xp_price),
            ShopItem(3, 'Счастливый Амулет', 300),
            ShopItem(4, 'Майнинг-ферма', mining_price),
            ShopItem(5, 'Зелье удачи', 500),
            ShopItem(6, 'Cчастливый тикет', 400),
            ShopItem(7, 'Кофе', 700),
            ShopItem(8, 'Пассивный бизнес', 1200),
            ShopItem(9, 'Секретный кейс', 2500),
        ]

    def _roll_discount(self) -> None:
        self.ctx.daily.discount_item_id = None

        if random.random() >= self.DISCOUNT_CHANCE:
            return

        item = random.choice(self.catalog)
        self.ctx.daily.discount_item_id = item.id

        print(
            f'{Colors.purple}✨ Загадочный Незнакомец хитро улыбается вам...{Colors.reset}\n'
            f'{Colors.yellow}   «Сегодня твой счастливый день, приятель! Устраиваю распродажу!»{Colors.reset}\n'
            f'🔥 Временная скидка 20% на товар {Colors.green}"{item.name}"{Colors.reset}\n'
        )

    def _choose_item(self) -> ShopItem | None:
        options = [
            Option(f'{item.name} — Цена: {self._price_label(item)}', item)
            for item in self.catalog
        ]

        return ask_option(
            f'{"=" * 30}\n\nВыберите товар для действия: ', options, blank_line=False
        )

    def _choose_action(self) -> ShopAction | None:
        action = ask_number(
            'Купить или вернуть? (1 или 2. 3 Для выхода): ',
            max=2,
            allow_cancel=True,
            cancel_on='3',
        )

        if action is None:
            return None

        return ShopAction(action)

    def _price_label(self, item: ShopItem) -> str:
        if item.price is None:
            return f'{Colors.red}MAX{Colors.reset} монет'

        if self.ctx.daily.discount_item_id == item.id:
            discounted = self._discounted_price(item.price)
            return (
                f'{Colors.red}{fmt(item.price)}{Colors.reset} -> '
                f'{Colors.green}{fmt(discounted)}{Colors.reset} монет '
                f'{Colors.yellow}% СКИДКА! %{Colors.reset}'
            )

        return f'{fmt(item.price)} монет'

    def _buy(self, item: ShopItem) -> None:
        if item.price is None:
            print(
                f'\n{Colors.yellow}Вы уже имеете максимальный уровень прокачки этого улучшения!{Colors.reset}\n'
            )
            return

        handler = self._buy_handlers.get(item.id)
        if handler is None:
            print(f'\n{Colors.red}Товара с таким ID не существует!{Colors.reset}')
            return

        handler(self._final_price(item))

    def _return(self, item: ShopItem) -> None:
        handler = self._sell_handlers.get(item.id)
        if handler is None:
            print(
                f'\n{Colors.red}Товара с таким ID не существует в системе возврата!{Colors.reset}\n'
            )
            return

        handler()

    def _final_price(self, item: ShopItem) -> int:
        if item.price is None:
            return 0

        if self.ctx.daily.discount_item_id == item.id:
            return self._discounted_price(item.price)

        return item.price

    def _discounted_price(self, price: int) -> int:
        return int(price * self.DISCOUNT_RATE)

    def _check_funds(self, price: int) -> bool:
        if self.player.balance >= price:
            return True

        print(
            f'\n{Colors.red}Недостаточно монет! Нужно {fmt(price)} монет, а у вас {fmt(self.player.balance)} монет.{Colors.reset}\n'
        )
        return False

    def _already_bought(self) -> None:
        print(f'\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}\n')

    def _not_bought(self, name: str) -> None:
        print(f'\n{Colors.red}У вас не куплено "{name}"!{Colors.reset}\n')

    def _buy_balance_multiplier(self, price: int) -> None:
        if not self._check_funds(price):
            return

        if not ask_confirmation(
            f'\nУлучшение множителя монет обойдётся вам в {Colors.yellow}{fmt(price)} монет{Colors.reset}. Купить?'
        ):
            return

        self.player.balance -= price
        self.player.balance_multiplier += 1

        print(
            f'\n{Colors.green}Успешно! Списано {fmt(price)} монет. Ваш множитель монет {self.player.balance_multiplier}x{Colors.reset}\n'
        )

    def _buy_xp_multiplier(self, price: int) -> None:
        if not self._check_funds(price):
            return

        if not ask_confirmation(
            f'\nУлучшение множителя опыта обойдётся вам в {Colors.yellow}{fmt(price)} монет{Colors.reset}. Купить?'
        ):
            return

        self.player.balance -= price
        self.player.xp_multiplier += 1

        print(
            f'\n{Colors.green}Успешно! Списано {fmt(price)} монет. Ваш множитель опыта {self.player.xp_multiplier}x{Colors.reset}\n'
        )

    def _buy_flag(self, attr: str, description: str, price: int) -> None:
        if getattr(self.player, attr):
            self._already_bought()
            return

        if not self._check_funds(price):
            return

        self.player.balance -= price
        setattr(self.player, attr, True)

        print(
            f'\n{Colors.green}Успешно! Списано {fmt(price)} монет, теперь у вас есть {description}{Colors.reset}\n'
        )

    def _buy_mining(self, price: int) -> None:
        if not self._check_funds(price):
            return

        self.player.balance -= price
        self.player.mining_lvl += 1

        next_price = (
            'MAX прокачка.'
            if self.player.mining_lvl == 10
            else f'{fmt(300 * (self.player.mining_lvl + 1))} монет.'
        )

        print(
            f'\n{Colors.green}Успешно! Списано {fmt(price)} монет, теперь у вас есть Майнинг ферма (лвл: {self.player.mining_lvl})!'
            f'\nСледующая прокачка будет стоить: {next_price}{Colors.reset}\n'
        )

    def _buy_coffee(self, price: int) -> None:
        if self.player.mining_multiplier == 2:
            self._already_bought()
            return

        if not self._check_funds(price):
            return

        if not ask_confirmation(
            f'\nНезнакомец: {Colors.blue_dark}Хм... Кофе? Ты уверен? Это не обычный напиток. Его аромат способен разогнать до предела любую электронику... Точно берешь?{Colors.reset}'
        ):
            return

        print(
            f'\nНезнакомец: {Colors.blue_dark}Отличный выбор. Твоя Майнинг-ферма скажет тебе спасибо. Работа пойдет в два раза быстрее!{Colors.reset}'
        )

        self.player.balance -= price
        self.player.mining_multiplier = 2

        print(
            f'\n{Colors.green}Успешно! Списано {fmt(price)} монет, теперь у вас есть Кофе (Майнинг ускорен)!{Colors.reset}\n'
        )

    def _buy_business(self, price: int) -> None:
        if self.player.business or self.player.balance >= price:
            print(f'\n{Colors.yellow}Этот товар был временно удалён!{Colors.reset}\n')
            return

        self._check_funds(price)

    def _buy_secret_case(self, price: int) -> None:
        if not self._check_funds(price):
            return

        self.player.balance -= price
        self.player.secret_case += 1

        win_money = random.choice(list(self.CASE_DROPS.keys()))
        self.player.balance += win_money

        print(
            f'\n{Colors.green}Успешно! Куплен Секретный кейс за {fmt(price)} монет.{Colors.reset}'
        )
        print('\nВы открываете кейс... ', end='')

        time.sleep(1)

        print(
            f'и внутри оказывается: {Colors.yellow}{fmt(win_money)} монет{Colors.reset}! 🔓'
        )
        print(self.CASE_DROPS[win_money])

    def _sell_multiplier(self, attr: str, name: str) -> None:
        if getattr(self.player, attr) != 5:
            self._not_bought(name)
            return

        setattr(self.player, attr, 1)
        self.player.balance += 1500

        print(
            f'\n{Colors.green}Успешно! Вы вернули "{name}"! К вашему балансу было прибавлено 1.500 монет!{Colors.reset}\n'
        )

    def _sell_flag(self, attr: str, refund: int, name: str) -> None:
        if not getattr(self.player, attr):
            self._not_bought(name)
            return

        setattr(self.player, attr, False)
        self.player.balance += refund

        print(
            f'\n{Colors.green}Успешно! Вы вернули "{name}"! К вашему балансу было прибавлено {fmt(refund)} монет!{Colors.reset}\n'
        )

    def _sell_mining(self) -> None:
        player = self.player

        if player.mining_lvl == 10 and player.balance >= 5000:
            print(f'\n{Colors.red}Майнинг ферму нельзя вернуть!{Colors.reset}\n')

        elif 0 < player.mining_lvl < 10:
            print(
                f'\nНезнакомец: {Colors.blue}Хех, у тебя ферма всего {Colors.yellow}{player.mining_lvl}-го уровня{Colors.blue}. Мелкие долги по свету меня не интересуют. Разгони её до максимума (10 LVL), вот тогда и поговорим о демонтаже!{Colors.reset}'
            )

        else:
            self._not_bought('Майнинг-ферма')

    def _sell_coffee(self) -> None:
        if self.player.mining_multiplier != 2:
            self._not_bought('Кофе')
            return

        self.player.mining_multiplier = 1
        self.player.balance += 350

        print(
            f'\n{Colors.green}Успешно! Вы вернули "Кофе"! К вашему балансу было прибавлено 350 монет!{Colors.reset}\n'
        )

    def _sell_business(self) -> None:
        if not self.player.business:
            self._not_bought('Пассивный Бизнес')
            return

        print(
            f'\nНезнакомец: {Colors.blue}Пассивный бизнес продан за полцены. Вам возвращено 600 монет.{Colors.reset}\n'
        )

        self.player.balance += 600
        self.player.business = False

        time.sleep(0.3)

        print(
            f'{Colors.green}Успешно! Пассивный бизнес закрыт, вам начислено +600 монет!{Colors.reset}\n'
        )

    def _sell_secret_case(self) -> None:
        print(f'\n{Colors.red}Ошибка! Секретный кейс нельзя вернуть!{Colors.reset}\n')
