import random
import sys
import time
from collections.abc import Callable
from typing import Final

from mini_store.colors import Colors
from mini_store.context import GameContext
from mini_store.games import *
from mini_store.keyboard import is_pressed, wait
from mini_store.utils import *

PROMO: Final[str] = 'MrIcant'
SHOP_CONTENT: Final[str] = (
    '1. Множитель монет x2 — Цена: 100 монет\n'
    '2. Множитель опыта x2 — Цена: 200 монет\n'
    '3. Счастливый Амулет — Цена: 300 монет\n'
    '4. Майнинг-ферма — Цена: 300 монет\n'
    '5. Зелье удачи — Цена: 500 монет\n'
    '6. Cчастливый тикет — Цена: 400 монет\n'
    '7. Кофе — Цена: 700 монет\n'
    '8. Пассивный бизнес — Цена: 1200 монет\n'
    '9. Секретный кейс — Цена: 2500 монет'
)

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
        ],
        allow_cancel=True,
    )

    if game_type is None:
        return

    game: AbstractGame = game_type(ctx.player)
    game.play()


def shop(ctx: GameContext) -> None:
    cls()

    print(
        f'\nВаш баланс: {Colors.yellow}{fmt(ctx.player.balance)} монет{Colors.reset}.',
        '\n==============================\n',
        f'{SHOP_CONTENT}',
        '\n==============================\n',
        sep='\n',
    )

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

        match user_id_buy:
            case 1:
                if ctx.player.balance_multiplier == 5:
                    print(
                        f'\n{Colors.yellow}Вы уже имеете максимальный уровень прокачки этого улучшения!{Colors.reset}'
                    )
                    return

                upgrade_cost = 100 * 2**ctx.player.balance_multiplier

                if ctx.player.balance < upgrade_cost:
                    print(
                        f'\n{Colors.red}Недостаточно монет! Нужно {fmt(upgrade_cost)} монет, а у вас {fmt(ctx.player.balance)} монет.{Colors.reset}'
                    )
                    return

                if not confirm(
                    f'\nУлучшение множителя монет обойдётся вам в {Colors.yellow}{fmt(upgrade_cost)} монет{Colors.reset}. Купить?'
                ):
                    return

                ctx.player.balance -= upgrade_cost
                ctx.player.balance_multiplier += 1

                print(
                    f'\n{Colors.green}Успешно! Списано {fmt(upgrade_cost)} монет. Ваш множитель монет {ctx.player.balance_multiplier}x{Colors.reset}'
                )

                time.sleep(3)

            case 2:
                if ctx.player.xp_multiplier == 5:
                    print(
                        f'\n{Colors.yellow}Вы уже имеете максимальный уровень прокачки этого улучшения!{Colors.reset}'
                    )
                    return

                upgrade_cost = 100 * 2**ctx.player.xp_multiplier

                if ctx.player.balance < upgrade_cost:
                    print(
                        f'\n{Colors.red}Недостаточно монет! Нужно {fmt(upgrade_cost)} монет, а у вас {fmt(ctx.player.balance)} монет.{Colors.reset}'
                    )
                    return

                if not confirm(
                    f'\nУлучшение множителя опыта обойдётся вам в {Colors.yellow}{fmt(upgrade_cost)} монет{Colors.reset}. Купить?'
                ):
                    return

                ctx.player.balance -= upgrade_cost
                ctx.player.xp_multiplier += 1

                print(
                    f'\n{Colors.green}Успешно! Списано {fmt(upgrade_cost)} монет. Ваш множитель опыта {ctx.player.xp_multiplier}x{Colors.reset}'
                )

                time.sleep(3)

            case 3:
                if ctx.player.lucky_amulet:
                    print(f'\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}')

                elif ctx.player.balance >= 300:
                    ctx.player.balance -= 300
                    ctx.player.lucky_amulet = True

                    print(
                        f'\n{Colors.green}Успешно! Списано 300 монет, теперь у вас есть Счастливый Амулет (+1 жизнь)!{Colors.reset}'
                    )

                else:
                    print(
                        f'\n{Colors.red}Недостаточно монет! Нужно 300, а у вас {ctx.player.balance}.{Colors.reset}'
                    )

            case 4:
                if ctx.player.mining_lvl >= 10:
                    print(
                        f'\n{Colors.yellow}Вы уже купили Майнинг-ферму по максималке!{Colors.reset}'
                    )

                else:
                    result_mining_lvl_mon = (
                        300 * (ctx.player.mining_lvl + 1)
                        if ctx.player.mining_lvl != 0
                        else 300
                    )

                    if ctx.player.balance >= result_mining_lvl_mon:
                        ctx.player.balance -= result_mining_lvl_mon
                        ctx.player.mining_lvl += 1

                        print(
                            f'\n{Colors.green}Успешно! Списано {fmt(result_mining_lvl_mon)} монет, теперь у вас есть Майнинг ферма (лвл: {ctx.player.mining_lvl})!'
                            f'Следующая прокачка будет стоить: {f"{fmt(300 * (ctx.player.mining_lvl + 1))} монет." if ctx.player.mining_lvl != 10 else "MAX прокачка."}'
                            f'\nУ вас на балансе: {fmt(ctx.player.balance)} монет.{Colors.reset}'
                        )

                    else:
                        print(
                            f'\n{Colors.red}Недостаточно монет! Нужно {fmt(result_mining_lvl_mon)}, а у вас {fmt(ctx.player.balance)}.{Colors.reset}'
                        )

            case 5:
                if ctx.player.potion_luck:
                    print(f'\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}')

                elif ctx.player.balance >= 500:
                    ctx.player.balance -= 500
                    ctx.player.potion_luck = True

                    print(
                        f'\n{Colors.green}Успешно! Списано 500 монет, теперь у вас есть Счастливое Зелье (Больше шансов в Казино)!{Colors.reset}'
                    )

                else:
                    print(
                        f'\n{Colors.red}Недостаточно монет! Нужно 500, а у вас {ctx.player.balance}.{Colors.reset}'
                    )

            case 6:
                if ctx.player.lucky_ticket:
                    print(f'\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}')

                elif ctx.player.balance >= 400:
                    ctx.player.balance -= 400
                    ctx.player.lucky_ticket = True

                    print(
                        f'\n{Colors.green}Успешно! Списано 400 монет, теперь у вас есть Счастливый Тикет (Не вычитается жизнь при первой попыткой)!{Colors.reset}'
                    )

                else:
                    print(
                        f'\n{Colors.red}Недостаточно монет! Нужно 400, а у вас {ctx.player.balance}.{Colors.reset}'
                    )

            case 7:
                if ctx.player.mining_multiplier == 2:
                    print(f'\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}')
                    return

                if ctx.player.balance < 700:
                    print(
                        f'\n{Colors.red}Недостаточно монет! Нужно 700, а у вас {ctx.player.balance}.{Colors.reset}'
                    )
                    return

                user_confirm = confirm(
                    f'\nНезнакомец: {Colors.blue_dark}Хм... Кофе? Ты уверен? Это не обычный напиток. Его аромат способен разогнать до предела любую электронику... Точно берешь?{Colors.reset}'
                )

                if not user_confirm:
                    return

                print(
                    f'\nНезнакомец: {Colors.blue_dark}Отличный выбор. Твоя Майнинг-ферма скажет тебе спасибо. Работа пойдет в два раза быстрее!{Colors.reset}'
                )

                ctx.player.balance -= 700
                ctx.player.mining_multiplier = 2

                print(
                    f'\n{Colors.green}Успешно! Списано 700 монет, теперь у вас есть Кофе (Майнинг ускорен)!{Colors.reset}'
                )

            case 8:
                if ctx.player.business:
                    print(f'\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}')

                elif ctx.player.balance >= 1200:
                    ctx.player.balance -= 1200
                    ctx.player.business = True

                    print(
                        f'\n{Colors.green}Успешно! Списано 1.200 монет, теперь у вас есть Пассивный бизнес (За каждый ход в меню +25 монет на баланс)!{Colors.reset}'
                    )

                else:
                    print(
                        f'\n{Colors.red}Недостаточно монет! Нужно 1.200, а у вас {fmt(ctx.player.balance)}.{Colors.reset}'
                    )

            case 9:
                if ctx.player.balance >= 2500:
                    ctx.player.balance -= 2500
                    ctx.player.secret_case += 1

                    case_list = [1250, 2500, 5000]
                    win_money = random.choice(case_list)

                    ctx.player.balance += win_money

                    print(
                        f'\n{Colors.green}Успешно! Куплен Секретный кейс за 2.500 монет.{Colors.reset}'
                    )

                    time.sleep(1)

                    print(
                        f'Вы открываете кейс... и внутри оказывается: {Colors.yellow}{fmt(win_money)} монет{Colors.reset}! 🔓'
                    )

                    if win_money == 5000:
                        print(
                            f'{Colors.green}🔥 ЛУЧШИЙ ДРОП! Вы сорвали куш кейса!{Colors.reset}'
                        )
                    elif win_money == 1250:
                        print(
                            f'{Colors.red}Эх, Незнакомец подсунул дешёвку. Повезёт в следующий раз!{Colors.reset}'
                        )
                    else:
                        print(f'{Colors.yellow}Нормально, вернули своё!{Colors.reset}')

                else:
                    print(
                        f'\n{Colors.red}Недостаточно монет! Нужно 2.500, а у вас {fmt(ctx.player.balance)}.{Colors.reset}'
                    )

            case _:
                print(f'\n{Colors.red}Товара с таким ID не существует!{Colors.reset}')

    elif user_action == 2:
        user_id_return = int(input('\nВыберите ID продукта для возращение товара: '))

        match user_id_return:
            case 1:
                if ctx.player.balance_multiplier == 5:
                    print(
                        f'\n{Colors.green}Успешно! Вы вернули "x5 бонус к монетам"! К вашему балансу было прибавлено 1.500 монет!{Colors.reset}'
                    )

                    ctx.player.balance_multiplier = 1
                    ctx.player.balance += 1500

                else:
                    print(
                        f'\n{Colors.red}У вас не куплено "x5 бонус к монетам"!{Colors.reset}'
                    )

            case 2:
                if ctx.player.xp_multiplier == 5:
                    print(
                        f'\n{Colors.green}Успешно! Вы вернули "x5 бонус к опыту"! К вашему балансу было прибавлено 1.500 монет!{Colors.reset}'
                    )

                    ctx.player.xp_multiplier = 1
                    ctx.player.balance += 1500

                else:
                    print(
                        f'\n{Colors.red}У вас не куплено "x5 бонус к опыту"!{Colors.reset}\n'
                    )

            case 3:
                if ctx.player.lucky_amulet:
                    print(
                        f'\n{Colors.green}Успешно! Вы вернули "Счастливый Амулет"! К вашему балансу было прибавлено 150 монет!{Colors.reset}'
                    )

                    ctx.player.lucky_amulet = False
                    ctx.player.balance += 150

                else:
                    print(
                        f'\n{Colors.red}У вас не куплен "Счастливый Амулет"!{Colors.reset}'
                    )

            case 4:
                if ctx.player.mining_lvl == 10 and ctx.player.balance >= 5000:
                    print(
                        f'\nНезнакомец: {Colors.blue_dark}Ферма 10 лвл демонтирована. За электричество и простой снято 5.000 монет.{Colors.reset}\n'
                    )

                    ctx.player.balance -= 5000
                    ctx.player.mining_lvl = 0
                    ctx.player.mining_multiplier = 1
                    ctx.player.buy_num_boost = 0

                    time.sleep(1)

                    print(
                        f'{Colors.red}Штраф оплачен! С баланса списано 5.000 монет. Ферма полностью демонтирована.{Colors.reset}'
                    )

                elif ctx.player.mining_lvl > 0 and ctx.player.mining_lvl < 10:
                    print(
                        f'\nНезнакомец: {Colors.blue_dark}Хех, у тебя ферма всего {Colors.yellow}{ctx.player.mining_lvl}-го уровня{Colors.blue_dark}. Мелкие долги по свету меня не интересуют. Разгони её до максимума (10 LVL), вот тогда и поговорим о демонтаже!{Colors.reset}'
                    )

                else:
                    print(
                        f'\n{Colors.red}У вас не куплена "Майнинг-ферма"!{Colors.reset}'
                    )

            case 5:
                if ctx.player.potion_luck:
                    print(
                        f'\n{Colors.green}Успешно! Вы вернули "Зелье Удачи"! К вашему балансу было прибавлено 250 монет!{Colors.reset}'
                    )

                    ctx.player.potion_luck = False
                    ctx.player.balance += 250

                else:
                    print(f'\n{Colors.red}У вас не куплено "Зелье Удачи"!{Colors.reset}')

            case 6:
                if ctx.player.lucky_ticket:
                    print(
                        f'\n{Colors.green}Успешно! Вы вернули "Cчастливый Тикет"! К вашему балансу было прибавлено 200 монет!{Colors.reset}'
                    )

                    ctx.player.lucky_ticket = False
                    ctx.player.balance += 200

                else:
                    print(
                        f'\n{Colors.red}У вас не куплено "Счастливый Тикет"!{Colors.reset}'
                    )

            case 7:
                if ctx.player.mining_multiplier == 2:
                    print(
                        f'\n{Colors.green}Успешно! Вы вернули "Кофе"! К вашему балансу было прибавлено 350 монет!{Colors.reset}'
                    )

                    ctx.player.mining_multiplier = 1
                    ctx.player.balance += 350

                else:
                    print(f'\n{Colors.red}У вас не куплено "Кофе"!{Colors.reset}')

            case 8:
                if ctx.player.business:
                    print(
                        f'\nНезнакомец: {Colors.blue_dark}Пассивный бизнес продан за полцены. Вам возвращено 600 монет.{Colors.reset}\n'
                    )

                    ctx.player.balance += 600
                    ctx.player.business = False

                    time.sleep(1)

                    print(
                        f'{Colors.green}Успешно! Пассивный бизнес закрыт, вам начислено +600 монет!{Colors.reset}'
                    )

                else:
                    print(
                        f'\n{Colors.red}У вас не куплен "Пассивный Бизнес"!{Colors.reset}'
                    )

            case 9:
                print(
                    f'\n{Colors.red}Ошибка! Секретный кейс нельзя вернуть!{Colors.reset}'
                )

            case _:
                print(
                    f'\n{Colors.red}Товара с таким ID не существует в системе возврата!{Colors.reset}'
                )


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
                print(f'\n{Colors.green}Майнинг приостановлен...{Colors.reset}\n')
                break

    else:
        print(f'\n{Colors.red}Сначала купите ферму в каталоге!{Colors.reset}\n')

        time.sleep(3)


def stranger(ctx: GameContext) -> None:
    cls()

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

        time.sleep(3)


def promocode(ctx: GameContext) -> None:
    user_promo = input('\nВведите промокод: ').strip()

    if user_promo == PROMO:
        ctx.player.promo_used = True

        print(
            f'\n🎉 {Colors.green}Успешно, промокод был активирован!{Colors.reset}'
            f'\n{ctx.player.add_coins_and_xp(coins=50, xp=30)}'
        )

    else:
        print(f'\n{Colors.red}Промокод не верен! {Colors.reset}')


def game_exit(ctx: GameContext) -> None:
    ctx.db.save_player(ctx.player)
    print('\nПрогресс сохранен! Прощайте, удачи вам! \n')
    sys.exit()


def reset(ctx: GameContext) -> None:
    if not confirm(
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
            f'\n{ctx.player.add_coins(10000000000)}'
        )

        ctx.player.secret_used = True

    else:
        print(f'\n{Colors.red}Ошибка 666! Вы уже нашли пасхалку!{Colors.reset}\n')
