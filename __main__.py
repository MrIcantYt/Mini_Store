import time
from typing import Final

from colorama import init as colorama_init
from keyboard import is_pressed

from colors import Colors
from db import JsonDataBase
from exceptions import SignCheckError
from games import *
from player import Player
from utils import fmt

colorama_init()

PROMO: Final[str] = 'MrIcant'
SHOP_CONTENT: Final[str] = (
    '1. Множитель монет x2 — Цена: 100 монет\n'
    '2. Множитель опыта x2 — Цена: 200 монет\n'
    '3. Счастливый Амулет — Цена: 300 монет\n'
    '4. Майнинг-ферма — Цена: 300 монет\n'
    '5. Зелье удачи — Цена: 500 монет\n'
    '6. Cчастливый тикет — Цена: 400 монет\n'
    '7. Кофе — Цена: 700 монет\n'
    '8. Пассивный бизнес — Цена: 1200 монет'
)


def init_game(player_id: int) -> tuple[JsonDataBase, Player]:
    db = JsonDataBase()
    db.init_db()

    try:
        player = db.get_player_by_id(player_id)
    except SignCheckError as e:
        print(f'\n{Colors.red}{e.message}. Ваш прогресс сброшен!{Colors.reset}')
        player = None

    if player is None:
        player = Player(id=player_id)
        db.save_player(player)

    return db, player


def main():
    player_id = 1
    db, player = init_game(player_id)

    if player is None:
        print(f'\n{Colors.red}Ошибка! Игрок с ID {player_id} не найден.{Colors.reset}\n')
        return

    print('\n === Добро пожаловать в "Мини Магазин" === \n')

    while True:
        print(
            '1. Магазин',
            '2. Игры',
            '3. Профиль',
            '4. Майнинг ферма',
            '5. Выход',
            f'\n{Colors.red}6. Сброс игры{Colors.reset}',
            sep='\n',
        )
        if not player.promo_used:
            print(f'\n{Colors.yellow}7. Промокод{Colors.reset}')

        try:
            user_digit = int(input('\nВведите цифру: '))
        except ValueError:
            print(f'\n{Colors.red}Ошибка! Введите число!{Colors.reset}\n')
            continue

        # Пассивный бизнес
        if player.business:
            print(
                f'\nНезнакомец: {Colors.blue_dark}Стартап принёс доход: {Colors.yellow}+25 монет{Colors.blue_dark}.{Colors.reset}'
            )

            player.balance += 25

        # Пасхалка
        if user_digit == 666:
            if not player.secret_used:
                print(f'\nВы нашли пасхалку!\n{player.add_coins(100)}\n')
                player.secret_used = True
            else:
                print(f'\n{Colors.red}Ошибка 666! Вы уже нашли пасхалку!{Colors.reset}\n')

            continue

        # Магазин
        # TODO: move shop to separate function/class
        elif user_digit == 1:
            print(f'\nВаш баланс: {Colors.yellow}{fmt(player.balance)}{Colors.reset}\n')
            print('\n===============\n')
            print(SHOP_CONTENT)
            print('\n===============\n')

            try:
                user_action = int(input('Купить или вернуть? (1 или 2, 3 для выхода): '))

                if user_action == 1:
                    try:
                        user_id_buy = int(input('\nВыберите номер продукта для покупки: '))
                        match user_id_buy:
                            case 1:
                                # TODO: buy multiple upgrade (+1x, max 5x). Cost: 100*2^multiplier
                                if balance_x2:
                                    print(
                                        f'\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}\n'
                                    )

                                elif player.balance >= 100:
                                    player.balance -= 100
                                    balance_x2 = True

                                    print(
                                        f'\n{Colors.green}Успешно! Списано 100 монет, теперь у вас x2 бонус к выигрышу!{Colors.reset}\n'
                                    )

                                else:
                                    print(
                                        f'\n{Colors.red}Недостаточно монет! Нужно 100, а у вас {player.balance}.{Colors.reset}\n'
                                    )

                            case 2:
                                if xp_x2:
                                    print(
                                        f'\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}\n'
                                    )

                                    bought += 1

                                    if bought == 3:
                                        print(
                                            'Незнакомец: Вам не надоело тыкать на купленный товар?\n'
                                        )

                                    elif bought == 5:
                                        print(
                                            'Незнакомец: Всё, хорошо, держите 100 монет. Если ещё раз тыкнете, то с вас спишется 100 монет!\n'
                                        )

                                        player.balance += 100

                                    elif bought == 6:
                                        print('Незнакомец: Я вас предупреждал!\n')

                                        player.balance -= 100

                                elif player.balance >= 200:
                                    player.balance -= 200
                                    xp_x2 = True

                                    print(
                                        f'\n{Colors.green}Успешно! Списано 200 монет, теперь у вас x2 бонус к опыту!{Colors.reset}\n'
                                    )

                                else:
                                    print(
                                        f'\n{Colors.red}Недостаточно монет! Нужно 200, а у вас {player.balance}.{Colors.reset}\n'
                                    )

                            case 3:
                                if player.lucky_amulet:
                                    print(
                                        f'\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}\n'
                                    )

                                elif player.balance >= 300:
                                    player.balance -= 300
                                    player.lucky_amulet = True

                                    print(
                                        f'\n{Colors.green}Успешно! Списано 300 монет, теперь у вас есть Счастливый Амулет (+1 жизнь)!{Colors.reset}\n'
                                    )

                                else:
                                    print(
                                        f'\n{Colors.red}Недостаточно монет! Нужно 300, а у вас {player.balance}.{Colors.reset}\n'
                                    )

                            case 4:
                                if player.mining_lvl >= 10:
                                    print(
                                        f'\n{Colors.yellow}Вы уже купили Майнинг-ферму по максималке!{Colors.reset}\n'
                                    )

                                else:
                                    result_mining_lvl_mon = (
                                        300 * (player.mining_lvl + 1)
                                        if player.mining_lvl != 0
                                        else 300
                                    )

                                    if player.balance >= result_mining_lvl_mon:
                                        player.balance -= result_mining_lvl_mon
                                        player.mining_lvl += 1

                                        print(
                                            f'\n{Colors.green}Успешно! Списано {fmt(result_mining_lvl_mon)} монет, теперь у вас есть Майнинг ферма (лвл: {player.mining_lvl})!'
                                        )
                                        print(
                                            f'Следующая прокачка будет стоить: {f"{fmt(300 * (player.mining_lvl + 1))} монет." if player.mining_lvl != 10 else "MAX прокачка."}'
                                        )
                                        print(
                                            f'\nУ вас на балансе: {fmt(player.balance)} монет.{Colors.reset}\n'
                                        )

                                    else:
                                        print(
                                            f'\n{Colors.red}Недостаточно монет! Нужно {fmt(result_mining_lvl_mon)}, а у вас {fmt(player.balance)}.{Colors.reset}\n'
                                        )

                            case 5:
                                if player.potion_luck:
                                    print(
                                        f'\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}\n'
                                    )

                                elif player.balance >= 500:
                                    player.balance -= 500
                                    potion_luck = True

                                    print(
                                        f'\n{Colors.green}Успешно! Списано 500 монет, теперь у вас есть Счастливое Зелье (Больше шансов в Казино)!{Colors.reset}\n'
                                    )

                                else:
                                    print(
                                        f'\n{Colors.red}Недостаточно монет! Нужно 500, а у вас {player.balance}.{Colors.reset}\n'
                                    )

                            case 6:
                                if player.lucky_ticket:
                                    print(
                                        f'\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}\n'
                                    )

                                elif player.balance >= 400:
                                    player.balance -= 400
                                    lucky_ticket = True

                                    print(
                                        f'\n{Colors.green}Успешно! Списано 400 монет, теперь у вас есть Счастливый Тикет (Не вычитается жизнь при первой попыткой)!{Colors.reset}\n'
                                    )

                                else:
                                    print(
                                        f'\n{Colors.red}Недостаточно монет! Нужно 400, а у вас {player.balance}.{Colors.reset}\n'
                                    )

                            case 7:
                                if mining_boost:
                                    print(
                                        f'\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}\n'
                                    )

                                elif player.balance >= 700:
                                    if buy_num_boost == 0:
                                        print(
                                            f'\nНезнакомец: {Colors.blue_dark}Хм... Кофе? Ты уверен? Это не обычный напиток. Его аромат способен разогнать до предела любую электронику... Точно берешь?{Colors.reset}\n'
                                        )
                                        time.sleep(5)

                                        buy_num_boost = 1

                                    elif buy_num_boost == 1:
                                        print(
                                            f'\nНезнакомец: {Colors.blue_dark}Отличный выбор. Твоя Майнинг-ферма скажет тебе спасибо. Работа пойдет в два раза быстрее!{Colors.reset}\n'
                                        )
                                        player.balance -= 700
                                        mining_boost = True

                                        time.sleep(5)

                                        print(
                                            f'{Colors.green}Успешно! Списано 700 монет, теперь у вас есть Кофе (Майнинг ускорен)!{Colors.reset}\n'
                                        )

                                else:
                                    print(
                                        f'\n{Colors.red}Недостаточно монет! Нужно 700, а у вас {player.balance}.{Colors.reset}\n'
                                    )

                            case 8:
                                if business:
                                    print(
                                        f'\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}\n'
                                    )

                                elif player.balance >= 1200:
                                    player.balance -= 1200
                                    business = True

                                    print(
                                        f'\n{Colors.green}Успешно! Списано 1.200 монет, теперь у вас есть Пассивный бизнес (За каждый ход в меню +25 монет на баланс)!{Colors.reset}\n'
                                    )

                                else:
                                    print(
                                        f'\n{Colors.red}Недостаточно монет! Нужно 1.200, а у вас {fmt(player.balance)}.{Colors.reset}\n'
                                    )

                            case _:
                                print(
                                    f'\n{Colors.red}Товара с таким ID не существует!{Colors.reset}\n'
                                )

                    except ValueError:
                        print(
                            f'\n{Colors.red}Ошибка! Введите корректный ID числом!\n{Colors.reset}'
                        )

                elif user_action == 2:
                    user_id_return = int(input('\nВыберите ID продукта для возращение товара: '))
                    match user_id_return:
                        case 1:
                            if balance_x2:
                                print(
                                    f'\n{Colors.green}Успешно! Вы вернули "x2 бонус к монетам"! К вашему балансу было прибавлено 50 монет!{Colors.reset}\n'
                                )

                                balance_x2 = False
                                player.balance += 50

                            else:
                                print(
                                    f'\n{Colors.red}У вас не куплено "x2 бонус к монетам"!{Colors.reset}\n'
                                )

                        case 2:
                            if xp_x2:
                                print(
                                    f'\n{Colors.green}Успешно! Вы вернули "x2 бонус к опыту"! К вашему балансу было прибавлено 100 монет!{Colors.reset}\n'
                                )

                                xp_x2 = False
                                player.balance += 100

                            else:
                                print(
                                    f'\n{Colors.red}У вас не куплено "x2 бонус к опыту"!{Colors.reset}\n'
                                )

                        case 3:
                            if player.lucky_amulet:
                                print(
                                    f'\n{Colors.green}Успешно! Вы вернули "Счастливый Амулет"! К вашему балансу было прибавлено 150 монет!{Colors.reset}\n'
                                )

                                player.lucky_amulet = False
                                player.balance += 150

                            else:
                                print(
                                    f'\n{Colors.red}У вас не куплен "Счастливый Амулет"!{Colors.reset}\n'
                                )

                        case 4:
                            if player.mining_lvl == 10 and player.balance >= 5000:
                                print(
                                    f'\nНезнакомец: {Colors.blue_dark}Ферма 10 лвл демонтирована. За электричество и простой снято {Colors.red}5.000 монет{Colors.blue_dark}.{Colors.reset}\n'
                                )

                                player.balance -= 5000
                                player.mining_lvl = 0
                                mining_boost = False
                                buy_num_boost = 0

                                time.sleep(3)

                                print(
                                    f'{Colors.red}Штраф оплачен! С баланса списано 5.000 монет. Ферма полностью демонтирована.{Colors.reset}\n'
                                )

                            elif player.mining_lvl > 0 and player.mining_lvl < 10:
                                print(
                                    f'\nНезнакомец: {Colors.blue_dark}Хех, у тебя ферма всего {Colors.yellow}{player.mining_lvl}-го уровня{Colors.blue_dark}. Мелкие долги по свету меня не интересуют. Разгони её до максимума (10 LVL), вот тогда и поговорим о демонтаже!{Colors.reset}\n'
                                )

                            else:
                                print(
                                    f'\n{Colors.red}У вас не куплена "Майнинг-ферма"!{Colors.reset}\n'
                                )

                        case 5:
                            if potion_luck:
                                print(
                                    f'\n{Colors.green}Успешно! Вы вернули "Зелье Удачи"! К вашему балансу было прибавлено 250 монет!{Colors.reset}\n'
                                )

                                potion_luck = False
                                player.balance += 250

                            else:
                                print(
                                    f'\n{Colors.red}У вас не куплено "Зелье Удачи"!{Colors.reset}\n'
                                )

                        case 6:
                            if lucky_ticket:
                                print(
                                    f'\n{Colors.green}Успешно! Вы вернули "Cчастливый Тикет"! К вашему балансу было прибавлено 200 монет!{Colors.reset}\n'
                                )

                                lucky_ticket = False
                                player.balance += 200

                            else:
                                print(
                                    f'\n{Colors.red}У вас не куплено "Счастливый Тикет"!{Colors.reset}\n'
                                )

                        case 7:
                            if mining_boost:
                                print(
                                    f'\n{Colors.green}Успешно! Вы вернули "Кофе"! К вашему балансу было прибавлено 350 монет!{Colors.reset}\n'
                                )

                                mining_boost = False
                                player.balance += 350

                            else:
                                print(f'\n{Colors.red}У вас не куплено "Кофе"!{Colors.reset}\n')

                        case 8:
                            if business:
                                print(
                                    f'\nНезнакомец: {Colors.blue_dark}Пассивный бизнес продан за полцены. Вам возвращено {Colors.yellow}600 монет{Colors.blue_dark}.{Colors.reset}\n'
                                )

                                player.balance += 600
                                business = False

                                time.sleep(3)

                                print(
                                    f'{Colors.green}Успешно! Пассивный бизнес закрыт, вам начислено +600 монет!{Colors.reset}\n'
                                )

                            else:
                                print(
                                    f'\n{Colors.red}У вас не куплен "Пассивный Бизнес"!{Colors.reset}\n'
                                )

                        case _:
                            print(
                                f'\n{Colors.red}Товара с таким ID не существует в системе возврата!{Colors.reset}\n'
                            )

                elif user_action == 3:
                    continue

            except ValueError, TypeError:
                print(f'\n{Colors.red}Ошибка! Введите корректное число. {Colors.reset}\n')

        # Игры
        elif user_digit == 2:
            print(
                '\n1. Угадать число'
                '\n2. Камень, ножницы, бумага'
                '\n3. Игровой автомат (Слоты) 🎰'
                '\n4. Блекджек (21 очко)'
            )

            try:
                user_number_game = int(input('\nВведите число игры: '))
                game_type: type[AbstractGame]

                match user_number_game:
                    case 1:
                        game_type = GuessNumberGame
                    case 2:
                        game_type = RockScissorsPaperGame
                    case 3:
                        game_type = SlotsGame
                    case 4:
                        game_type = Blackjack
                    case _:
                        print(f'\n{Colors.red}Такой игры нет.{Colors.reset}\n')
                        continue

                game = game_type(player)
                game.play()

            except ValueError:
                print(f'\n{Colors.red}Ошибка! Введите число!{Colors.reset}\n')

        # Профиль
        elif user_digit == 3:
            print(
                f'\n--- ПРОФИЛЬ ИГРОКА ---\n'
                f'⭐ Уровень: {Colors.yellow}{player.lvl}{Colors.reset} '
                f'(до следующего уровня {Colors.yellow}{player.next_lvl_xp_needed - player.xp}{Colors.reset} XP)\n'
                f'📈 Опыт: {Colors.yellow}{fmt(player.xp)}{Colors.reset} / '
                f'{Colors.yellow}{fmt(player.lvl * 100)}{Colors.reset} XP\n'
                f'💰 Баланс: {Colors.yellow}{fmt(player.balance)}{Colors.reset} монет'
            )

            print(
                '\nМножители:\n'
                f' - Множитель уровня {Colors.yellow}{player.level_multiplier:.1f}x{Colors.reset}\n'
                f' - Множитель монет {Colors.yellow}{player.balance_multiplier:.1f}x{Colors.reset}\n'
                f' - Множитель опыта {Colors.yellow}{player.xp_multiplier:.1f}x{Colors.reset}\n'
            )

            print('Купленные предметы:')
            items = []

            if player.lucky_amulet:
                items.append(f' - Счастливый Амулет {Colors.green}[+1 жизнь]{Colors.reset}')
            if player.potion_luck:
                items.append(f' - Зелье Удачи {Colors.green}[Шанс в казино повышен]{Colors.reset}')
            if player.lucky_ticket:
                items.append(
                    f' - Счастливый Тикет {Colors.green}[Защита от 1 проигрыша]{Colors.reset}'
                )

            if player.mining_lvl > 0:
                msg = f' - Майнинг-ферма: {Colors.yellow}{player.mining_lvl} лвл{Colors.reset}.'

                if player.mining_multiplier != 1.0:
                    msg += f' {Colors.blue}[Кофе ускорил вас в {player.mining_multiplier:.1f} раза]{Colors.reset}'

                items.append(msg)

            if player.business:
                items.append(f' - Пассивный бизнес {Colors.green}[+25 монет за ход]{Colors.reset}')

            if not items:
                print(f'{Colors.red}Рюкзак пуст. Купите что-нибудь в каталоге!{Colors.reset}')
            else:
                print('\n\t'.join(items))
            print('-' * 20)

        # Майнинг-ферма
        elif user_digit == 4:
            if player.mining_lvl > 0:
                print(
                    f'\n⛏️ {Colors.green}Майнинг-ферма запущена! [Нажмите Q для выхода]{Colors.reset}\n'
                )

                while True:
                    player.balance += 1 * player.mining_lvl

                    print(
                        f'Добыча... Ваш баланс: {Colors.yellow}{fmt(player.balance)}{Colors.reset} монет 💰',
                        end='\r',
                    )

                    sleep_time = 1 // player.mining_multiplier
                    time.sleep(sleep_time)

                    if is_pressed('q'):
                        print(f'\n{Colors.green}Майнинг приостановлен...{Colors.reset}\n')
                        break

            else:
                print(f'\n{Colors.red}Сначала купите ферму в каталоге!{Colors.reset}\n')

        # Выход
        elif user_digit == 5:
            print('\nПрогресс сохранен! Прощайте, удачи вам!\n')
            break

        # Удаления БД
        elif user_digit == 6:
            confirm = input(
                f'\nНезнакомец: {Colors.blue_dark}Вы уверенны, что хотите сбросить весь свой прогресс? (Нажмите 6 ещё раз для подтверждения){Colors.reset}\n'
            )

            if confirm.lower() != '6':
                continue

            print(f'\nНезнакомец: {Colors.blue_dark}Хорошо! Ваше решение принято.{Colors.reset}\n')

            db.reset_player(player_id)

        # Промокод
        elif user_digit == 7:
            if not player.promo_used:
                user_promo = input('\nВведите промокод: ').strip()

                if user_promo == PROMO:
                    player.promo_used = True

                    print(
                        f'\n🎉 {Colors.green}Успешно, промокод был активирован!{Colors.reset}'
                        f'\n{player.add_coins_and_xp(coins=50, xp=30)}\n'
                    )

                else:
                    print(f'\n{Colors.red}Промокод не верен! {Colors.reset}\n')

            else:
                print(f'\n{Colors.yellow}Промокод уже был введён!{Colors.reset}\n')

        # Неизвестный пункт
        else:
            print(f'\n{Colors.red}Неизвестный пункт меню: {user_digit}{Colors.reset} \n')

        db.save_player(player)


# Запуск игры
if __name__ == '__main__':
    main()
