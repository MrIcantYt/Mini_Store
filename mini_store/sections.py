__all__ = (
    'SectionFunc',
    'bank_menu',
    'debug_menu',
    'easter_egg',
    'game',
    'game_exit',
    'merchant_contracts',
    'mining',
    'profile',
    'promocode',
    'reset',
    'shop',
)

import random
import sys
import time
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Final

from mini_store.colors import Colors
from mini_store.context import GameContext
from mini_store.games import *
from mini_store.keyboard import is_pressed, wait
from mini_store.shop import Shop
from mini_store.utils import *

PROMO: Final[str] = 'MrIcant'

type SectionFunc = Callable[[GameContext], None]


def game(ctx: GameContext) -> None:
    cls()
    game_type: type[AbstractGame] | None = ask_option(
        'Выберите игру: ',
        [
            Option('Угадать число', GuessNumberGame),
            Option('Камень, ножницы, бумага', RockScissorsPaperGame),
            Option('Игровой автомат (Слоты)', SlotsGame),
            Option('Блекдежек (21 очко)', BlackjackGame),
            Option('Колесо Рулетки', RouttleGame),
            Option('Кости (Craps)', CrapsGame),
        ],
        allow_cancel=True,
    )

    if game_type is None:
        cls()
        return

    game: AbstractGame = game_type(ctx)
    game.play()


def shop(ctx: GameContext) -> None:
    Shop(ctx).open()


def profile(ctx: GameContext) -> None:
    cls()

    print(
        f'\n--- ПРОФИЛЬ ИГРОКА ---\n'
        f'⭐ Уровень: {Colors.yellow}{ctx.player.lvl}{Colors.reset} '
        f'(до следующего уровня {Colors.yellow}{fmt(ctx.player.next_lvl_xp_needed - ctx.player.xp)}{Colors.reset} XP)\n'
        f'📈 Опыт: {Colors.yellow}{fmt(ctx.player.xp)}{Colors.reset} / '
        f'{Colors.yellow}{fmt(ctx.player.lvl * 100)}{Colors.reset} XP\n'
        f'💰 Баланс: {Colors.yellow}{fmt(ctx.player.balance)}{Colors.reset} монет'
    )

    print(
        '\nМножители:\n'
        f' - Множитель уровня {Colors.yellow}{ctx.player.level_multiplier:.1f}x{Colors.reset}\n'
        f' - Множитель монет {Colors.yellow}{ctx.player.balance_multiplier:.1f}x{Colors.reset}\n'
        f' - Множитель опыта {Colors.yellow}{ctx.player.xp_multiplier:.1f}x{Colors.reset}\n'
    )

    print('Купленные предметы:')
    items = []

    if ctx.player.lucky_amulet:
        items.append(f' - Счастливый Амулет {Colors.green}[+1 жизнь]{Colors.reset}')
    if ctx.player.potion_luck:
        items.append(
            f' - Зелье Удачи {Colors.green}[Шанс в казино повышен]{Colors.reset}'
        )
    if ctx.player.lucky_ticket:
        items.append(
            f' - Счастливый Тикет {Colors.green}[Защита от 1 проигрыша]{Colors.reset}'
        )

    if ctx.player.mining_lvl > 0:
        msg = (
            f' - Майнинг-ферма: {Colors.yellow}{ctx.player.mining_lvl} лвл{Colors.reset}.'
        )

        if ctx.player.mining_multiplier != 1.0:
            msg += f' {Colors.blue}[Кофе ускорил в {ctx.player.mining_multiplier:.0f} раза]{Colors.reset}'

        items.append(msg)

    if ctx.player.business:
        items.append(
            f' - Пассивный бизнес {Colors.green}[+25 монет за ход]{Colors.reset}'
        )

    if not items:
        print(f'{Colors.red}Рюкзак пуст. Купите что-нибудь в магазине.{Colors.reset}')
    else:
        print('\n'.join(items))

    print('\n--- 📜 ЗАДАНИЯ НЕЗНАКОМЦА ---\n')

    # Квест 1: Стартовый капитал
    if ctx.player.quest_id == 1:
        print(f'Задание 1: {Colors.blue}«Первые шаги»{Colors.reset}')
        print(
            f'Цель: Накопить {Colors.yellow}500 монет{Colors.reset}. (У вас сейчас: {Colors.yellow}{fmt(ctx.player.balance)} монет{Colors.reset})'
        )

        if ctx.player.balance >= 500:
            ctx.player.quest_id = 2

            print(
                f'\n{Colors.green}🎉 Квест выполнен! Награда: +150 XP. Открыто новое задание!{Colors.reset}'
            )

            ctx.player.add_xp(150)

        else:
            print(f'\n{Colors.red}Задание не выполнено. Копи монеты.{Colors.reset}')

    # Квест 2: Прокачка железа
    elif ctx.player.quest_id == 2:
        print(f'Задание 2: {Colors.blue}«Разгон фермы»{Colors.reset}')
        print(
            f'Цель: Прокачать Майнинг-ферму до {Colors.yellow}3 уровня{Colors.reset} или выше. (Ваш уровень: {Colors.yellow}{ctx.player.mining_lvl} лвл{Colors.reset})'
        )

        if ctx.player.mining_lvl >= 3:
            ctx.player.quest_id = 3

            print(
                f'\n{Colors.green}🎉 Квест выполнен! Награда: +1.000 монет. Открыто новое задание!{Colors.reset}'
            )

            ctx.player.add_coins(1000)

        else:
            print(
                f'\n{Colors.red}Задание не выполнено. Улучши ферму в Каталоге до 3 лвл.{Colors.reset}'
            )

    # Квест 3: Испытать удачу в Слотах
    elif ctx.player.quest_id == 3:
        print(f'Задание 3: {Colors.blue}«Азартный тиктокер»{Colors.reset}')
        print(
            f'Цель: Сыграть в Игровой Автомат (Слоты) {Colors.yellow}5 раз{Colors.reset}. (Прогресс: {Colors.yellow}{ctx.player.quest_progress} / 5{Colors.reset})'
        )

        if ctx.player.quest_progress >= 5:
            ctx.player.quest_id = 4
            ctx.player.quest_progress = 0

            print(
                f'\n{Colors.green}🎉 Все задания Незнакомца выполнены! Награда: +500 монет и +300 XP!{Colors.reset}'
            )

            ctx.player.add_coins_and_xp(coins=500, xp=300)

        else:
            print(
                f'\n{Colors.red}Задание выполняется в казино (Пункт 2 -> Игра 3).{Colors.reset}'
            )

    else:
        print(
            f'{Colors.yellow}Незнакомец: Контракты закончились. Ты выполнил всё, что я просил. Жди обновлений!{Colors.reset}'
        )

    print('-' * 20, '\n\nНажмите "q" для выхода в меню')

    wait('q')
    cls()


def mining(ctx: GameContext) -> None:
    cls()

    if ctx.player.mining_lvl > 0:
        print(
            f'\n⛏️ {Colors.green}Майнинг-ферма запущена! [Нажмите Q для выхода]{Colors.reset}\n'
        )

        while True:
            ctx.player.balance += 1 * ctx.player.mining_lvl

            print(
                f'Добыча... Ваш баланс: {Colors.yellow}{fmt(ctx.player.balance)}{Colors.reset} монет 💰',
                end='\r',
            )

            sleep_time = 1 // ctx.player.mining_multiplier
            time.sleep(sleep_time)

            if is_pressed('q'):
                print()
                print(f'\n{Colors.green}Майнинг приостановлен...{Colors.reset}\n')
                break

    else:
        print(f'\n{Colors.red}Сначала купите ферму в каталоге!{Colors.reset}\n')


def promocode(ctx: GameContext) -> None:
    user_promo = input('\nВведите промокод: ').strip()

    if user_promo == PROMO:
        ctx.player.promo_used = True

        print(
            f'\n🎉 {Colors.green}Успешно, промокод был активирован!{Colors.reset}'
            f'\n{ctx.player.add_coins_and_xp(coins=50, xp=30)}\n'
        )

    else:
        print(f'\n{Colors.red}Промокод не верен! {Colors.reset}\n')


def game_exit(ctx: GameContext) -> None:
    ctx.db.save_player(ctx.player)
    print('\nПрогресс сохранен! Прощайте, удачи вам! \n')
    sys.exit()


def reset(ctx: GameContext) -> None:
    if not ask_confirmation(
        f'\nНезнакомец: {Colors.blue_dark}Вы уверенны, что хотите сбросить весь свой прогресс?{Colors.reset}\n'
    ):
        return

    print(
        f'\nНезнакомец: {Colors.blue_dark}Хорошо! Ваше решение принято.{Colors.reset}\n'
    )

    ctx.player = ctx.db.reset_player(ctx.player)

    time.sleep(3)

    cls()


def easter_egg(ctx: GameContext) -> None:
    cls()
    if not ctx.player.secret_used:
        print(
            f'\n{Colors.green}Успешно! Вы нашли пасхалку!{Colors.reset}\n'
            f'\n{ctx.player.add_coins(100)}\n'
        )

        ctx.player.secret_used = True

    else:
        print(f'\n{Colors.red}Ошибка 666! Вы уже нашли пасхалку!{Colors.reset}\n')


def debug_menu(ctx: GameContext) -> None:
    cls()
    print('=== Debug menu ===\n')
    action_choose = ask_option(
        'Выберите действие: ',
        [
            Option('Добавить монет', 1),
            Option('Добавить опыта', 2),
            Option('Установить уровень', 3),
        ],
        allow_cancel=True,
    )

    cls()

    if action_choose is None:
        return

    match action_choose:
        case 1:
            amount = ask_number('Сколько монет добавить: ')
            if amount is None:
                return
            print(ctx.player.add_coins(amount, False))
        case 2:
            amount = ask_number('Сколько опыта добавить: ')
            if amount is None:
                return
            print(ctx.player.add_xp(amount, False))
        case 3:
            level: int | None = ask_number('Какой уровень установить: ')
            if level is None:
                return
            ctx.player.lvl = level
            print(f'Был установлен {level} уровень.')


def bank_menu(ctx: GameContext) -> None:
    cls()
    print(f'\n{Colors.blue}=== 🏦 Инвестиции Незнакомца ==={Colors.reset}')
    print(
        f'\n{Colors.yellow}Правила{Colors.reset}: Сложный процент ({Colors.yellow}+10%{Colors.reset}) начисляется каждые 3 сыгранных раунда в Блекджек.'
    )

    if ctx.player.bank_deposit > 0:
        print(
            f'\nВаш текущий вклад: {Colors.yellow}{fmt(ctx.player.bank_deposit)}{Colors.reset} монет.'
        )

    else:
        print('\nУ вас пока нет активных вкладов.')

    action = ask_option(
        'Выберите действие: ',
        [
            Option(
                f'Положить монеты на депозит (Ваш баланс: {Colors.yellow}{fmt(ctx.player.balance)}{Colors.reset} монет)',
                1,
            ),
            Option('Снять все деньги с депозита', 2),
        ],
        allow_cancel=True,
        cancel_on='3',
    )

    if action is None:
        cls()
        return

    match action:
        case 1:
            try:
                dep_input = (
                    input("\nВведите сумму для вклада или 'all'/'все': ").strip().lower()
                )

                if dep_input in ('all', 'все'):
                    dep_amount = ctx.player.balance
                else:
                    dep_amount = int(dep_input)

                if 0 < dep_amount <= ctx.player.balance:
                    ctx.player.balance -= dep_amount
                    ctx.player.bank_deposit += dep_amount

                    print(
                        f'\n{Colors.green}✅ Вы успешно инвестировали {fmt(dep_amount)} монет!{Colors.reset}\n'
                    )
                else:
                    print(f'\n{Colors.red}Ошибка! Некорректная сумма.{Colors.reset}\n')

            except ValueError:
                print(f'\n{Colors.red}Ошибка ввода.{Colors.reset}\n')

        case 2:
            if ctx.player.bank_deposit > 0:
                withdrawn = ctx.player.bank_deposit

                ctx.player.balance += withdrawn
                ctx.player.bank_deposit = 0
                ctx.player.bank_turns = 0

                print(
                    f'\n{Colors.green}💰 Вы сняли весь свой вклад: {fmt(withdrawn)} монет!{Colors.reset}\n'
                )

            else:
                print(f'\n{Colors.red}У вас нет денег на депозите!{Colors.reset}\n')


def _time_until_midnight(now: datetime) -> str:
    """Возвращает отформатированное время до ближайшей полуночи."""
    midnight = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    time_left = midnight - now
    hours, remainder = divmod(int(time_left.total_seconds()), 3600)
    minutes, _ = divmod(remainder, 60)
    return f'{hours:2d}ч {minutes:02d}м'


def merchant_contracts(ctx: GameContext):
    @dataclass
    class MerchantContract:
        text: str
        min: int
        max: int
        reward_base: int

    cls()

    print(f'\n {Colors.yellow}== 📅 Ежедневные Контракты Торговца =={Colors.reset}\n')

    player = ctx.player
    daily = ctx.daily

    now = datetime.now(UTC).astimezone()
    today = now.date()
    timer_str = _time_until_midnight(now)

    available_contracts: list[MerchantContract] = [
        MerchantContract('Сыграть {target} раундов в Блекджек', 3, 7, 150),
        MerchantContract('Набрать ровно 21 очко {target} раз(а)', 1, 2, 300),
        MerchantContract('Разделить карты (Сплит) хотя бы {target} раз', 1, 1, 250),
    ]

    if daily.last_update != today:
        selected = random.choice(available_contracts)
        target_value = random.randint(selected.min, selected.max)

        daily.contract = selected.text.format(target=target_value)
        daily.target = target_value
        daily.progress = 0
        daily.reward = target_value * selected.reward_base
        daily.last_update = today
        daily.completed = False

        print(
            f'{Colors.blue}🛒 Торговец обновил ассортимент контрактов на сегодня!{Colors.reset}\n'
        )

    print(f'🕒 Время до обновления контракта:{Colors.red}{timer_str}{Colors.reset}')
    print(f'📜 Задание: {Colors.yellow}{daily.contract}{Colors.reset}')

    if daily.completed:
        print(
            f'📊 Прогресс: [{Colors.green}ВЫПОЛНЕНО{Colors.reset}] ({daily.progress}/{daily.target})'
        )
        print('🎉 Вы уже забрали награду за этот контракт!')

    else:
        print(f'📊 Прогресс: {Colors.blue}{daily.progress}/{daily.target}{Colors.reset}')
        print(
            f'💰 Награда за выполнение: {Colors.yellow}{fmt(daily.reward)}{Colors.reset} монет'
        )

        if daily.progress >= daily.target:
            print(
                f'\n{Colors.green}⭐ Контракт выполнен! Торговец готов заплатить. {Colors.reset}'
            )

            if ask_confirmation('\nЗабрать награду?'):
                player.balance += daily.reward
                daily.completed = True

                print(
                    f'\n💰 {Colors.green}Вы получили {fmt(daily.reward)} монет от Торговца!{Colors.reset}'
                )

        else:
            print('\nВозвращайтесь за наградой, когда выполните условия контракта.')

    input('\nНажмите Enter, чтобы вернуться в меню...')
    print()
