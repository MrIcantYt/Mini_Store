import random
import sys
import time
from collections.abc import Callable
from datetime import date, datetime
from typing import Any, Final

from mini_store.colors import Colors
from mini_store.context import GameContext
from mini_store.games import *
from mini_store.keyboard import is_pressed, wait
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
        return

    game: AbstractGame = game_type(ctx)
    game.play()


def shop(ctx: GameContext) -> None:
    cls()

    player = ctx.player

    price_balance_multiplier = 100 * 2**player.balance_multiplier if player.balance_multiplier < 5 else 'MAX'
    price_xp_multiplier = 100 * 2**player.xp_multiplier if player.xp_multiplier < 5 else 'MAX'
    result_mining_lvl_mon = 300 * (player.mining_lvl + 1) if player.mining_lvl != 0 else 300
    price_mining = result_mining_lvl_mon if player.mining_lvl != 10 else 'MAX'

    items_catalog: Final[dict[int, dict[str, Any]]] = {
        1: {"name": f"Множитель монет {player.balance_multiplier}x", "price": price_balance_multiplier},
        2: {"name": f"Множитель опыта {player.xp_multiplier}x", "price": price_xp_multiplier},
        3: {"name": "Счастливый Амулет", "price": 300},
        4: {"name": "Майнинг-ферма", "price": price_mining},
        5: {"name": "Зелье удачи", "price": 500},
        6: {"name": "Cчастливый тикет", "price": 400},
        7: {"name": "Кофе", "price": 700},
        8: {"name": "Пассивный бизнес", "price": 1200},
        9: {"name": "Секретный кейс", "price": 2500}
    }

    if ctx.daily.discount_checked != ctx:
        if random.random() < 0.15:
            valid_ids = [id_ for id_, data in items_catalog.items() if isinstance(data["price"], int)]
            ctx.daily.discount_id = random.choice(valid_ids) if valid_ids else None
        
        else:
            ctx.daily.discount_id = None
        
        ctx.daily.discount_checked = ctx

    print(f"\n{Colors.blue}🛒 Добро пожаловать в Каталог Незнакомца!{Colors.reset}\n")

    if ctx.daily.discount_id and ctx.daily.discount_id in items_catalog:
        print(f"{Colors.purple}✨ Загадочный Незнакомец хитро улыбается вам...{Colors.reset}")
        print(f"{Colors.yellow}   «Сегодня твой счастливый день, приятель! Устраиваю распродажу!»{Colors.reset}")
        print(f"🔥 Временная скидка 20% на товар под номером {ctx.daily.discount_id}: {Colors.green}{items_catalog[ctx.daily.discount_id]['name']}{Colors.reset}!\n")

    print(f'Ваш баланс: {Colors.yellow}{fmt(player.balance)} монет{Colors.reset}.\n')
    print('==============================')

    for item_id, data in items_catalog.items():
        base_price = data["price"]
        
        if base_price == 'MAX' or base_price == 'MAX прокачка.':
            price_display = f"{Colors.red}MAX{Colors.reset} монет"

        elif ctx.daily.discount_id == item_id and isinstance(base_price, int):
            discounted_price = int(base_price * 0.8)
            price_display = f"{Colors.red}{fmt(base_price)}{Colors.reset} -> {Colors.green}{fmt(discounted_price)}{Colors.reset} монет {Colors.yellow}% СКИДКА! %{Colors.reset}"

        else:
            price_display = f"{fmt(base_price)} монет"
            
        print(f'{item_id}. {data["name"]} — Цена: {price_display}')
        
    print('==============================\n')

    user_action = ask_number(
        'Купить или вернуть? (1 или 2. 3 Для выхода): ',
        max=2,
        allow_cancel=True,
        cancel_on='3',
    )

    if user_action is None:
        return

    if user_action == 1:
        try:
            user_id_buy = int(input('\nВыберите номер продукта для покупки: '))
        except ValueError:
            print(f'\n{Colors.red}Ошибка! Введите корректный ID числом!\n{Colors.reset}')
            return

        if user_id_buy not in items_catalog:
            print(f'\n{Colors.red}Товара с таким ID не существует!{Colors.reset}')
            return

        target_item = items_catalog[user_id_buy]
        base_price = target_item["price"]

        if base_price == 'MAX' or base_price == 'MAX прокачка.':
            print(f'\n{Colors.yellow}Вы уже имеете максимальный уровень прокачки этого улучшения!{Colors.reset}\n')
            return

        final_price = int(base_price * 0.8) if ctx.daily.discount_id == user_id_buy and isinstance(base_price, int) else base_price

        match user_id_buy:
            case 1:
                if player.balance < final_price:
                    print(f'\n{Colors.red}Недостаточно монет! Нужно {fmt(final_price)} монет, а у вас {fmt(player.balance)} монет.{Colors.reset}\n')
                    return

                if not ask_confirmation(f'\nУлучшение множителя монет обойдётся вам в {Colors.yellow}{fmt(final_price)} монет{Colors.reset}. Купить?'):
                    return

                player.balance -= final_price
                player.balance_multiplier += 1

                print(f'\n{Colors.green}Успешно! Списано {fmt(final_price)} монет. Ваш множитель монет {player.balance_multiplier}x{Colors.reset}\n')

            case 2:
                if player.balance < final_price:
                    print(f'\n{Colors.red}Недостаточно монет! Нужно {fmt(final_price)} монет, а у вас {fmt(player.balance)} монет.{Colors.reset}\n')
                    return

                if not ask_confirmation(f'\nУлучшение множителя опыта обойдётся вам в {Colors.yellow}{fmt(final_price)} монет{Colors.reset}. Купить?'):
                    return

                player.balance -= final_price
                player.xp_multiplier += 1

                print(f'\n{Colors.green}Успешно! Списано {fmt(final_price)} монет. Ваш множитель опыта {player.xp_multiplier}x{Colors.reset}\n')

            case 3:
                if player.lucky_amulet:
                    print(f'\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}\n')

                elif player.balance >= final_price:
                    player.balance -= final_price
                    player.lucky_amulet = True

                    print(f'\n{Colors.green}Успешно! Списано {fmt(final_price)} монет, теперь у вас есть Счастливый Амулет (+1 жизнь)!{Colors.reset}\n')

                else:
                    print(f'\n{Colors.red}Недостаточно монет! Нужно {fmt(final_price)}, а у вас {player.balance}.{Colors.reset}\n')

            case 4:
                if player.balance >= final_price:
                    player.balance -= final_price
                    player.mining_lvl += 1

                    print(
                        f'\n{Colors.green}Успешно! Списано {fmt(final_price)} монет, теперь у вас есть Майнинг ферма (лвл: {player.mining_lvl})!'
                        f'\nСледующая прокачка будет стоить: {f"{fmt(300 * (player.mining_lvl + 1))} монет." if player.mining_lvl != 10 else "MAX прокачка."}{Colors.reset}\n'
                    )

                else:
                    print(f'\n{Colors.red}Недостаточно монет! Нужно {fmt(final_price)}, а у вас {fmt(player.balance)}.{Colors.reset}\n')

            case 5:
                if player.potion_luck:
                    print(f'\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}\n')

                elif player.balance >= final_price:
                    player.balance -= final_price
                    player.potion_luck = True

                    print(f'\n{Colors.green}Успешно! Списано {fmt(final_price)} монет, теперь у вас есть Счастливое Зелье (Больше шансов в Казино)!{Colors.reset}\n')

                else:
                    print(f'\n{Colors.red}Недостаточно монет! Нужно {fmt(final_price)}, а у вас {player.balance}.{Colors.reset}\n')

            case 6:
                if player.lucky_ticket:
                    print(f'\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}\n')

                elif player.balance >= final_price:
                    player.balance -= final_price
                    player.lucky_ticket = True

                    print(f'\n{Colors.green}Успешно! Списано {fmt(final_price)} монет, теперь у вас есть Счастливый Тикет (Не вычитается жизнь при первой попытке)!{Colors.reset}\n')

                else:
                    print(f'\n{Colors.red}Недостаточно монет! Нужно {fmt(final_price)}, а у вас {player.balance}.{Colors.reset}\n')

            case 7:
                if player.mining_multiplier == 2:
                    print(f'\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}\n')
                    return

                if player.balance < final_price:
                    print(f'\n{Colors.red}Недостаточно монет! Нужно {fmt(final_price)}, а у вас {player.balance}.{Colors.reset}\n')
                    return

                if not ask_confirmation(f'\nНезнакомец: {Colors.blue_dark}Хм... Кофе? Ты уверен? Это не обычный напиток. Его аромат способен разогнать до предела любую электронику... Точно берешь?{Colors.reset}'):
                    return

                print(f'\nНезнакомец: {Colors.blue_dark}Отличный выбор. Твоя Майнинг-ферма скажет тебе спасибо. Работа пойдет в два раза быстрее!{Colors.reset}')

                player.balance -= final_price
                player.mining_multiplier = 2

                print(f'\n{Colors.green}Успешно! Списано {fmt(final_price)} монет, теперь у вас есть Кофе (Майнинг ускорен)!{Colors.reset}\n')

            case 8:
                if player.business or player.balance >= final_price:
                    print(f'\n{Colors.yellow}Этот товар был временно удалён!{Colors.reset}\n')

                else:
                    print(f'\n{Colors.red}Недостаточно монет! Нужно {fmt(final_price)}, а у вас {fmt(player.balance)}.{Colors.reset}\n')

            case 9:
                if player.balance >= final_price:
                    player.balance -= final_price
                    player.secret_case += 1
                    case_list = [1250, 2500, 5000]
                    win_money = random.choice(case_list)
                    player.balance += win_money

                    print(f'\n{Colors.green}Успешно! Куплен Секретный кейс за {fmt(final_price)} монет.{Colors.reset}')
                    print('\nВы открываете кейс... ', end='')
                    
                    time.sleep(1)
                    
                    print(f'и внутри оказывается: {Colors.yellow}{fmt(win_money)} монет{Colors.reset}! 🔓')

                    if win_money == 5000:
                        print(f'{Colors.green}🔥 ЛУЧШИЙ ДРОП! Вы сорвали куш кейса!{Colors.reset}\n')

                    elif win_money == 1250:
                        print(f'{Colors.red}Эх, Незнакомец подсунул дешёвку. Повезёт в следующий раз!{Colors.reset}\n')

                    else:
                        print(f'{Colors.yellow}Нормально, вернули своё!{Colors.reset}\n')

                else:
                    print(f'\n{Colors.red}Недостаточно монет! Нужно {fmt(final_price)}, а у вас {fmt(player.balance)}.{Colors.reset}\n')

    elif user_action == 2:
        try:
            user_id_return = int(input('\nВыберите ID продукта для возвращения товара: '))
        except ValueError:
            print(f'\n{Colors.red}Ошибка! Введите корректный ID числом!\n{Colors.reset}')
            return

        match user_id_return:
            case 1:
                if player.balance_multiplier == 5:
                    print(f'\n{Colors.green}Успешно! Вы вернули "x5 бонус к монетам"! К вашему балансу было прибавлено 1.500 монет!{Colors.reset}\n')

                    player.balance_multiplier = 1
                    player.balance += 1500

                else:
                    print(f'\n{Colors.red}У вас не куплено "x5 бонус к монетам"!{Colors.reset}\n')

            case 2:
                if player.xp_multiplier == 5:
                    print(f'\n{Colors.green}Успешно! Вы вернули "x5 бонус к опыту"! К вашему балансу было прибавлено 1.500 монет!{Colors.reset}\n')

                    player.xp_multiplier = 1
                    player.balance += 1500

                else:
                    print(f'\n{Colors.red}У вас не куплено "x5 бонус к опыту"!{Colors.reset}\n')

            case 3:
                if player.lucky_amulet:
                    print(f'\n{Colors.green}Успешно! Вы вернули "Счастливый Амулет"! К вашему балансу было прибавлено 150 монет!{Colors.reset}\n')

                    player.lucky_amulet = False
                    player.balance += 150
                else:
                    print(f'\n{Colors.red}У вас не куплен "Счастливый Амулет"!{Colors.reset}\n')

            case 4:
                if player.mining_lvl == 10 and player.balance >= 5000:
                    print(f'\n{Colors.red}Майнинг ферму нельзя вернуть!{Colors.reset}\n')

                elif player.mining_lvl > 0 and player.mining_lvl < 10:
                    print(f'\nНезнакомец: {Colors.blue}Хех, у тебя ферма всего {Colors.yellow}{player.mining_lvl}-го уровня{Colors.blue}. Мелкие долги по свету меня не интересуют. Разгони её до максимума (10 LVL), вот тогда и поговорим о демонтаже!{Colors.reset}')

                else:
                    print(f'\n{Colors.red}У вас не куплена "Майнинг-ферма"!{Colors.reset}')

            case 5:
                if player.potion_luck:
                    print(f'\n{Colors.green}Успешно! Вы вернули "Зелье Удачи"! К вашему балансу было прибавлено 250 монет!{Colors.reset}\n')

                    player.potion_luck = False
                    player.balance += 250

                else:
                    print(f'\n{Colors.red}У вас не куплено "Зелье Удачи"!{Colors.reset}\n')

            case 6:
                if player.lucky_ticket:
                    print(f'\n{Colors.green}Успешно! Вы вернули "Cчастливый Тикет"! К вашему балансу было прибавлено 200 монет!{Colors.reset}\n')

                    player.lucky_ticket = False
                    player.balance += 200

                else:
                    print(f'\n{Colors.red}У вас не куплено "Счастливый Тикет"!{Colors.reset}\n')

            case 7:
                if player.mining_multiplier == 2:
                    print(f'\n{Colors.green}Успешно! Вы вернули "Кофе"! К вашему балансу было прибавлено 350 монет!{Colors.reset}\n')

                    player.mining_multiplier = 1
                    player.balance += 350

                else:
                    print(f'\n{Colors.red}У вас не куплено "Кофе"!{Colors.reset}\n')

            case 8:
                if player.business:
                    print(f'\nНезнакомец: {Colors.blue}Пассивный бизнес продан за полцены. Вам возвращено 600 монет.{Colors.reset}\n')

                    player.balance += 600
                    player.business = False

                    time.sleep(0.3)

                    print(f'{Colors.green}Успешно! Пассивный бизнес закрыт, вам начислено +600 монет!{Colors.reset}\n')
                else:
                    print(f'\n{Colors.red}У вас не куплен "Пассивный Бизнес"!{Colors.reset}\n')

            case 9:
                print(f'\n{Colors.red}Ошибка! Секретный кейс нельзя вернуть!{Colors.reset}\n')

            case _:
                print(f'\n{Colors.red}Товара с таким ID не существует в системе возврата!{Colors.reset}\n')


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
        print(f'Цель: Накопить {Colors.yellow}500 монет{Colors.reset}. (У вас сейчас: {Colors.yellow}{fmt(ctx.player.balance)} монет{Colors.reset})')

        if ctx.player.balance >= 500:
            ctx.player.quest_id = 2

            print(f'\n{Colors.green}🎉 Квест выполнен! Награда: +150 XP. Открыто новое задание!{Colors.reset}')

            ctx.player.add_xp(150)

        else:
            print(f'\n{Colors.red}Задание не выполнено. Копи монеты.{Colors.reset}')

    # Квест 2: Прокачка железа
    elif ctx.player.quest_id == 2:
        print(f'Задание 2: {Colors.blue}«Разгон фермы»{Colors.reset}')
        print(f'Цель: Прокачать Майнинг-ферму до {Colors.yellow}3 уровня{Colors.reset} или выше. (Ваш уровень: {Colors.yellow}{ctx.player.mining_lvl} лвл{Colors.reset})')

        if ctx.player.mining_lvl >= 3:
            ctx.player.quest_id = 3

            print(f'\n{Colors.green}🎉 Квест выполнен! Награда: +1.000 монет. Открыто новое задание!{Colors.reset}')

            ctx.player.add_coins(1000)

        else:
            print(f'\n{Colors.red}Задание не выполнено. Улучши ферму в Каталоге до 3 лвл.{Colors.reset}')

    # Квест 3: Испытать удачу в Слотах
    elif ctx.player.quest_id == 3:
        print(f'Задание 3: {Colors.blue}«Азартный тиктокер»{Colors.reset}')
        print(f'Цель: Сыграть в Игровой Автомат (Слоты) {Colors.yellow}5 раз{Colors.reset}. (Прогресс: {Colors.yellow}{ctx.player.quest_progress} / 5{Colors.reset})')

        if ctx.player.quest_progress >= 5:
            ctx.player.quest_id = 4
            ctx.player.quest_progress = 0

            print(f'\n{Colors.green}🎉 Все задания Незнакомца выполнены! Награда: +500 монет и +300 XP!{Colors.reset}')

            ctx.player.add_coins_and_xp(coins=500, xp=300)

        else:
            print(f'\n{Colors.red}Задание выполняется в казино (Пункт 2 -> Игра 3).{Colors.reset}')

    else:
        print(f'{Colors.yellow}Незнакомец: Контракты закончились. Ты выполнил всё, что я просил. Жди обновлений!{Colors.reset}')

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

        time.sleep(3)


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
    if not ctx.player.secret_used:
        print(
            f'\n{Colors.green}Успешно! Вы нашли пасхалку!{Colors.reset}\n'
            f'\n{ctx.player.add_coins(10000000000)}\n'
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

    if action_choose is None:
        cls()
        return

    cls()
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

    print(
        f'\n1. Положить монеты на депозит (Ваш баланс: {Colors.yellow}{fmt(ctx.player.balance)}{Colors.reset} монет)'
    )
    print('2. Снять все деньги с депозита')
    print('3. Назад')

    try:
        action = int(input('\nВыберите действие: '))

    except ValueError:
        return

    if action == 1:
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

    elif action == 2:
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


def merchant_contracts(ctx):
    print(f"\n {Colors.yellow}== 📅 Ежедневные Контракты Торговца =={Colors.reset}\n")

    player = ctx.player
    daily = ctx.daily
    today = date.today()  # noqa: DTZ011

    now = datetime.now()  # noqa: DTZ005
    midnight = datetime.combine(today, datetime.max.time())
    time_left = midnight - now
    hours, remainder = divmod(time_left.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    timer_str = f"{hours:2d}ч {minutes:02d}м"

    available_contracts = [
        {"text": "Сыграть {target} раундов в Блекджек", "min": 3, "max": 7, "reward_base": 150},
        {"text": "Набрать ровно 21 очко {target} раз(а)", "min": 1, "max": 2, "reward_base": 300},
        {"text": "Разделить карты (Сплит) хотя бы {target} раз", "min": 1, "max": 1, "reward_base": 250},
    ]

    if daily.last_update != today:
        selected = random.choice(available_contracts)
        target_value = random.randint(selected["min"], selected["max"])
        
        daily.contract = selected["text"].format(target=target_value)
        daily.target = target_value
        daily.progress = 0
        daily.reward = target_value * selected["reward_base"]
        daily.last_update = today
        daily.completed = False
        
        print(f"{Colors.blue}🛒 Торговец обновил ассортимент контрактов на сегодня!{Colors.reset}\n")

    print(f"🕒 Время до обновления контракта:{Colors.red}{timer_str}{Colors.reset}")
    print(f"📜 Задание: {Colors.yellow}{daily.contract}{Colors.reset}")

    if daily.completed:
        print(f"📊 Прогресс: [{Colors.green}ВЫПОЛНЕНО{Colors.reset}] ({daily.progress}/{daily.target})")
        print("🎉 Вы уже забрали награду за этот контракт!")

    else:
        print(f"📊 Прогресс: {Colors.blue}{daily.progress}/{daily.target}{Colors.reset}")
        print(f"💰 Награда за выполнение: {Colors.yellow}{fmt(daily.reward)}{Colors.reset} монет")

        if daily.progress >= daily.target:
            print(f"\n{Colors.green}⭐ Контракт выполнен! Торговец готов заплатить. {Colors.reset}")

            if ask_confirmation("\nЗабрать награду?"):
                player.balance += daily.reward
                daily.completed = True

                print(f"\n💰 {Colors.green}Вы получили {fmt(daily.reward)} монет от Торговца!{Colors.reset}")

        else:
            print("\nВозвращайтесь за наградой, когда выполните условия контракта.")

    input("\nНажмите Enter, чтобы вернуться в меню...")
    print()
