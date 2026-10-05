import os
import random
import sys
import time

from colorama import init as colorama_init

from colors import Colors
from db import SqliteDataBase
from games import *
from player import Player
from utils import fmt

colorama_init()

PROMO = 'MrIcant'
SHOP_CONTENT = (
    '1. Множитель монет x2 — Цена: 100 монет (ID: 1)\n'
    '2. Множитель опыта x2 — Цена: 200 монет (ID: 2)\n'
    '3. Счастливый Амулет — Цена: 300 монет (ID: 3)\n'
    '4. Майнинг-ферма — Цена: 300 монет (ID: 4)\n'
    '5. Зелье удачи — Цена: 500 монет (ID: 5)\n'
    '6. Cчастливый тикет — Цена: 400 монет (ID: 6)\n'
    '7. Кофе — Цена: 700 монет (ID: 7)\n'
    '8. Пассивный бизнес — Цена: 1200 монет (ID: 8)'
)


# Игра: Блекджек (21 очко)
def blackjack(balance, balance_x2, xp, xp_x2, level):
    print(f'\n {Colors.yellow}== Игра: Блекджек (21 очко) =={Colors.reset}\n')

    cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
    player_score = 0
    bot_score = 0

    user_input = (
        input(
            f"Введите вашу ставку или 'all'/'все', чтобы поставить всё (Ваш баланс: {fmt(balance)}): "
        )
        .strip()
        .lower()
    )

    try:
        if user_input == 'all' or user_input == 'все':
            money_player = balance

        else:
            money_player = int(user_input)

    except ValueError:
        print(
            f"\n{Colors.red}Ошибка! Введите корректное число или слово 'all'/'все'.{Colors.reset}\n"
        )
        return balance, xp

    if money_player <= 0:
        print(
            f'\n{Colors.red}Ошибка! Ставка {fmt(balance)} монет невозможна! Нельзя играть на 0 или меньше.{Colors.reset}\n'
        )
        return balance, xp

    elif money_player > balance:
        print(f'\n{Colors.red}Ошибка! Нельзя вводить ставку больше своего баланса!{Colors.reset}\n')
        return balance, xp

    balance -= money_player

    player_score += random.choice(cards)
    player_score += random.choice(cards)
    player_overflow = False

    while player_score < 21:
        print(f'\nУ вас на руках: {Colors.yellow}{player_score}{Colors.reset} очков')

        try:
            user_choice = int(input('1. Взять ещё карту | 2. Остановиться: '))

        except ValueError:
            print(f'\n{Colors.red}Ошибка! Введите 1 или 2.{Colors.reset}')
            continue

        if user_choice == 1:
            random_cart = random.choice(cards)
            player_score += random_cart

            print(f'Вы вытянули карту: {Colors.yellow}{random_cart}{Colors.reset}')

            if player_score > 21:
                print(f'\nУ вас на руках: {Colors.red}{player_score}{Colors.reset} очков')
                print(f'\n{Colors.red}💥 Перебор! Вы проиграли свою ставку!{Colors.reset}\n')

                player_overflow = True
                break

        elif user_choice == 2:
            break

        else:
            print(f'\n{Colors.red}Неверный пункт! Выберите 1 или 2.{Colors.reset}\n')

    if player_overflow:
        return balance, xp

    if player_score == 21:
        print(f'\n🎉 {Colors.green}ОГО! У вас ровно 21 очко!{Colors.reset}')

    print(f'\n{Colors.blue}🤖 Очередь Дилера (Бота)...{Colors.reset}\n')

    bot_score += random.choice(cards)
    bot_score += random.choice(cards)

    print(f'Стартовые очки бота: {Colors.blue}{bot_score}{Colors.reset}')

    time.sleep(0.6)

    while bot_score < 17:
        bot_card = random.choice(cards)
        bot_score += bot_card

        print(
            f'🤖 Бот вытянул карту: {Colors.yellow}{bot_card}{Colors.reset} (Всего у бота: {bot_score})'
        )

        time.sleep(0.6)

    print(f'\nФинальный счёт дилера: {Colors.blue}{bot_score}{Colors.reset} очков')

    time.sleep(0.4)

    level_multiplier = 1.0 + (level - 1) * 0.1

    if bot_score > 21 or player_score > bot_score:
        reward_coins = int(money_player * level_multiplier * (2 if balance_x2 else 1))
        reward_xp = 60 if xp_x2 else 30

        balance += money_player + reward_coins
        xp += reward_xp

        if bot_score > 21:
            print(
                f'\n🎉 {Colors.green}Бот перебрал ({bot_score} очков)! Вы победили!{Colors.reset}'
            )

        else:
            print(
                f'\n🎉 {Colors.green}Поздравляю! У вас больше очков. Вы победили дилера!{Colors.reset}'
            )

        print(
            f'💰 Вы получили {Colors.yellow}{fmt(reward_coins)}{Colors.reset} монет (Множитель уровня: {Colors.yellow}{level_multiplier:.1f}x{Colors.reset})!'
        )
        print(f'📈 Вам начислено {Colors.yellow}{fmt(reward_xp)}{Colors.reset} XP!\n')

    elif player_score == bot_score:
        balance += money_player

        print(
            f'\n{Colors.yellow}🤝 Ничья! Очков поровну ({player_score} vs {bot_score}). Ставка возвращена на баланс.{Colors.reset}\n'
        )

    else:
        print(
            f'\n{Colors.red}🔴 У дилера больше очков ({bot_score}). Вы проиграли свою ставку!{Colors.reset}\n'
        )

    return balance, xp


def load_game(player_id):
    player = Player(player_id)
    db = SqliteDataBase()
    db.init_db()

    db_player = db.get_player_by_id(player_id)
    if db_player is None:
        db.save_player(player)

    return db, player


def main():
    player_id = 1
    db, player = load_game(player_id)
    if player is None:
        print(f'\n{Colors.red}Ошибка! Игрок с ID {player_id} не найден.{Colors.reset}\n')
        return

    print('\n === Добро пожаловать в "Мини Магазин" === \n')

    while True:
        print('1. Каталог')
        print('2. Игры')
        print('3. Профиль')
        print('4. Промокод')
        print('5. Майнинг ферма')
        print('6. Выход')
        print(f'\n{Colors.red}7. Сброс игры{Colors.reset}')

        try:
            user_digit = int(input('\nВведите цифру: '))

        except ValueError:
            print(f'\n{Colors.red}Ошибка 666! Введите число!{Colors.reset}\n')
            continue

        # Пасхалка
        if user_digit == 666:
            player.reset_num = 0

            if not player.secret_used:
                player.balance += 100
                player.secret_used = True

                db.save_player(player)

                print()

            continue

        # Пассивный бизнес
        if player.business:
            print(
                f'\nНезнакомец: {Colors.blue_dark}Стартап принёс доход: {Colors.yellow}+25 монет{Colors.blue_dark}.{Colors.reset}'
            )

            player.balance += 25

            db.save_player(player)

        # Максимальный баланс
        player.balance = min(player.balance, 999999999)
        db.save_player(player)

        # Магазин
        if user_digit == 1:
            player.reset_num = 0

            try:  # FIXME
                with open(SHOP_CONTENT, 'r', encoding='utf-8') as file:
                    print('\n===============\n')
                    print(file.read())
                    print('\n===============\n')

                try:
                    user_id_buy_or_return = int(input('Купить или вернуть? (1 or 2): '))

                    if user_id_buy_or_return == 1:
                        try:
                            user_id_buy = int(input('\nВыберите ID продукта для покупки: '))
                            match user_id_buy:
                                case 1:
                                    if balance_x2:
                                        print(
                                            f'\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}\n'
                                        )

                                    elif player.balance >= 100:
                                        player.balance -= 100
                                        balance_x2 = True

                                        db.save_player(player)

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

                                        db.save_player(player)

                                        if bought == 3:
                                            print(
                                                'Незнакомец: Вам не надоело тыкать на купленный товар?\n'
                                            )

                                            db.save_player(player)

                                        elif bought == 5:
                                            print(
                                                'Незнакомец: Всё, хорошо, держите 100 монет. Если ещё раз тыкнете, то с вас спишется 100 монет!\n'
                                            )

                                            player.balance += 100

                                            db.save_player(player)

                                        elif bought == 6:
                                            print('Незнакомец: Я вас предупреждал!\n')

                                            player.balance -= 100

                                            db.save_player(player)

                                    elif player.balance >= 200:
                                        player.balance -= 200
                                        xp_x2 = True

                                        db.save_player(player)

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

                                        db.save_player(player)

                                        print(
                                            f'\n{Colors.green}Успешно! Списано 300 монет, теперь у вас есть Счастливый Амулет (+1 жизнь)!{Colors.reset}\n'
                                        )

                                    else:
                                        print(
                                            f'\n{Colors.red}Недостаточно монет! Нужно 300, а у вас {player.balance}.{Colors.reset}\n'
                                        )

                                case 4:
                                    if mining_lvl >= 10:
                                        print(
                                            f'\n{Colors.yellow}Вы уже купили Майнинг-ферму по максималке!{Colors.reset}\n'
                                        )

                                    else:
                                        result_mining_lvl_mon = (
                                            300 * (mining_lvl + 1) if mining_lvl != 0 else 300
                                        )

                                        if player.balance >= result_mining_lvl_mon:
                                            player.balance -= result_mining_lvl_mon
                                            mining_lvl += 1

                                            db.save_player(player)

                                            print(
                                                f'\n{Colors.green}Успешно! Списано {fmt(result_mining_lvl_mon)} монет, теперь у вас есть Майнинг ферма (лвл: {mining_lvl})!'
                                            )
                                            print(
                                                f'Следующая прокачка будет стоить: {f"{fmt(300 * (mining_lvl + 1))} монет." if mining_lvl != 10 else "MAX прокачка."}'
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

                                        db.save_player(player)

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

                                        db.save_player(player)

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

                                            db.save_player(player)

                                        elif buy_num_boost == 1:
                                            print(
                                                f'\nНезнакомец: {Colors.blue_dark}Отличный выбор. Твоя Майнинг-ферма скажет тебе спасибо. Работа пойдет в два раза быстрее!{Colors.reset}\n'
                                            )
                                            player.balance -= 700
                                            mining_boost = True

                                            db.save_player(player)

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

                                        db.save_player(player)

                                        print(
                                            f'\n{Colors.green}Успешно! Списано 1.200 монет, теперь у вас есть Пассивный бизнес (За каждый ход в меню +25 монет на баланс)!{Colors.reset}\n'
                                        )

                                    else:
                                        print(
                                            f'\n{Colors.red}Недостаточно монет! Нужно 1.200, а у вас {fmt(balance)}.{Colors.reset}\n'
                                        )

                                case _:
                                    print(
                                        f'\n{Colors.red}Товара с таким ID не существует!{Colors.reset}\n'
                                    )

                        except ValueError:
                            print(
                                f'\n{Colors.red}Ошибка! Введите корректный ID числом!\n{Colors.reset}'
                            )

                    elif user_id_buy_or_return == 2:
                        user_id_return = int(
                            input('\nВыберите ID продукта для возращение товара: ')
                        )
                        match user_id_return:
                            case 1:
                                if balance_x2:
                                    print(
                                        f'\n{Colors.green}Успешно! Вы вернули "x2 бонус к монетам"! К вашему балансу было прибавлено 50 монет!{Colors.reset}\n'
                                    )

                                    balance_x2 = False
                                    player.balance += 50

                                    db.save_player(player)

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

                                    db.save_player(player)

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

                                    db.save_player(player)

                                else:
                                    print(
                                        f'\n{Colors.red}У вас не куплен "Счастливый Амулет"!{Colors.reset}\n'
                                    )

                            case 4:
                                if mining_lvl == 10 and player.balance >= 5000:
                                    print(
                                        f'\nНезнакомец: {Colors.blue_dark}Ферма 10 лвл демонтирована. За электричество и простой снято {Colors.red}5.000 монет{Colors.blue_dark}.{Colors.reset}\n'
                                    )

                                    player.balance -= 5000
                                    mining_lvl = 0
                                    mining_boost = False
                                    buy_num_boost = 0

                                    db.save_player(player)

                                    time.sleep(3)

                                    print(
                                        f'{Colors.red}Штраф оплачен! С баланса списано 5.000 монет. Ферма полностью демонтирована.{Colors.reset}\n'
                                    )

                                elif mining_lvl > 0 and mining_lvl < 10:
                                    print(
                                        f'\nНезнакомец: {Colors.blue_dark}Хех, у тебя ферма всего {Colors.yellow}{mining_lvl}-го уровня{Colors.blue_dark}. Мелкие долги по свету меня не интересуют. Разгони её до максимума (10 LVL), вот тогда и поговорим о демонтаже!{Colors.reset}\n'
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

                                    db.save_player(player)

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

                                    db.save_player(player)

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

                                    db.save_player(player)

                                else:
                                    print(f'\n{Colors.red}У вас не куплено "Кофе"!{Colors.reset}\n')

                            case 8:
                                if business:
                                    print(
                                        f'\nНезнакомец: {Colors.blue_dark}Пассивный бизнес продан за полцены. Вам возвращено {Colors.yellow}600 монет{Colors.blue_dark}.{Colors.reset}\n'
                                    )

                                    player.balance += 600
                                    business = False

                                    db.save_player(player)

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

                    else:
                        print('\nВозврат в главное меню...\n')
                        continue

                except ValueError, TypeError:
                    print(f'\n{Colors.red}Ошибка! Введите корректное число. {Colors.reset}\n')

            except FileNotFoundError:
                print('\n[Магазин временно пуст]\n')

        # Игры
        elif user_digit == 2:
            player.reset_num = 0

            print(
                '\n1. Угадать число'
                '\n2. Камень, ножницы, бумага'
                '\n3. Игровой автомат (Слоты) 🎰'
                '\n4. Блекджек (21 очко)'
            )

            try:
                user_number_game = int(input('\nВведите число игры: '))
                game: AbstractGame

                match user_number_game:
                    case 1:
                        game = GuessNumberGame(player)
                    case 2:
                        game = RockScissorsPaperGame(player)
                    case 3:
                        game = SlotsGame(player)
                    case 4:
                        # TODO
                        # game = Blackjack()
                        pass
                    case _:
                        print(f'\n{Colors.red}Такой игры нет.{Colors.reset}\n')
                        continue

                game.play(player)
                db.save_player(player)

            except ValueError:
                print(f'\n{Colors.red}Ошибка! Введите число!{Colors.reset}\n')

        # Профиль
        elif user_digit == 3:
            player.reset_num = 0

            level_multiplier = 1.0 + (player.lvl - 1) * 0.1
            level_bonus_percent = int((level_multiplier - 1.0) * 100)

            print('\n--- ПРОФИЛЬ ИГРОКА ---\n')
            print(f'Уровень: {Colors.yellow}{player.lvl}{Colors.reset} ⭐')
            print(
                f'Опыт: {Colors.yellow}{fmt(player.xp)}{Colors.reset} / {Colors.yellow}{fmt(player.lvl * 100)}{Colors.reset} XP 📈'
            )
            print(
                f'Бонус уровня: {Colors.yellow}+{level_bonus_percent}%{Colors.reset} к доходу ({Colors.yellow}{level_multiplier:.1f}x{Colors.reset})'
            )
            print(f'Баланс: {Colors.yellow}{fmt(player.balance)}{Colors.reset} монет 💰')

            print('\nКупленные предметы:')
            has_items = False

            print(
                f' - Множитель монет {player.balance_multiplier} {Colors.green}[Активен]{Colors.reset}'
                f' - Множитель опыта {player.xp_multiplier} {Colors.green}[Активен]{Colors.reset}'
            )

            if player.lucky_amulet:
                print(f' - Счастливый Амулет {Colors.green}[+1 жизнь]{Colors.reset}')
                has_items = True

            if player.potion_luck:
                print(f' - Зелье Удачи {Colors.green}[Шанс в казино повышен]{Colors.reset}')
                has_items = True

            if player.lucky_ticket:
                print(f' - Счастливый Тикет {Colors.green}[Защита от 1 проигрыша]{Colors.reset}')
                has_items = True

            if mining_lvl > 0:
                status_coffee = (
                    f' {Colors.blue}[Кофе ускорил в 2 раза]{Colors.reset}' if mining_boost else ''
                )
                print(
                    f' - Майнинг-ферма: {Colors.yellow}{mining_lvl} лвл{Colors.reset}{status_coffee}'
                )
                has_items = True

            if player.business:
                print(f' - Пассивный бизнес {Colors.green}[+25 монет за ход]{Colors.reset}')
                has_items = True

            if not has_items:
                print(f' {Colors.red}Рюкзак пуст. Купите что-нибудь в каталоге!{Colors.reset}')

            print('\n----------------------\n')

        # Промокод
        elif user_digit == 4:
            player.reset_num = 0

            if not player.promo_used:
                user_promo = input('\nВведите промокод: ').strip()

                if user_promo == PROMO:
                    base_coins = 50
                    base_xp = 30
                    level_multiplier = 1.0 + (player.lvl - 1) * 0.1

                    coins_given = int(base_coins * level_multiplier * player.balance_multiplier)
                    xp_given = int(base_xp * level_multiplier * player.xp_multiplier)

                    player.balance += coins_given
                    player.xp += xp_given
                    player.promo_used = True

                    print(f'\n🎉 {Colors.green}Успешно, промокод был активирован!{Colors.reset} ')
                    print(
                        f'💰 Вы получили {Colors.yellow}{fmt(coins_given)}{Colors.reset} монет (Множитель уровня: {Colors.yellow}{level_multiplier:.1f}x{Colors.reset})!'
                    )
                    print(f'📈 Вам начислено {Colors.yellow}{fmt(xp_given)}{Colors.reset} XP!\n')

                    # xp, level, balance = check_level_up(
                    #     xp, level, balance, Colors.green, Colors.reset, Colors.yellow
                    # )

                    db.save_player(player)

                else:
                    print(f'\n{Colors.red}Промокод не верен! {Colors.reset}\n')

            else:
                print(f'\n{Colors.yellow}Промокод уже был введён!{Colors.reset}\n')

        # Майнинг-ферма
        elif user_digit == 5:
            player.reset_num = 0

            import msvcrt

            if mining_lvl > 0:
                print(
                    f'\n⛏️ {Colors.green}Майнинг-ферма запущена! [Нажмите Q для выхода]{Colors.reset}\n'
                )

                while True:
                    player.balance += 5 * mining_lvl
                    player.balance = min(player.balance, 999999999)

                    print(
                        f'Добыча... Ваш баланс: {Colors.yellow}{fmt(player.balance)}{Colors.reset} монет 💰',
                        end='\r',
                    )

                    sleep_time = 0.5 if mining_boost else 1.0
                    time.sleep(sleep_time)

                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8', errors='ignore').lower()

                        if key in 'q':
                            print()
                            print(
                                f'\n{Colors.green}Майнинг приостановлен. Возврат в меню...{Colors.reset}\n'
                            )

                            db.save_player(player)
                            break

            else:
                print(f'\n{Colors.red}Сначала купите ферму в каталоге!{Colors.reset}\n')

        # Выход
        elif user_digit == 6:
            db.save_player(player)

            print('\nПрогресс сохранен! Прощайте, удачи вам! \n')

            break

        # Удаления БД
        elif user_digit == 7:
            if player.reset_num == 0:
                print(
                    f'\nНезнакомец: {Colors.blue_dark}Вы уверенны, что хотите сбросить весь свой прогресс? (Нажмите 7 ещё раз для подтверждения){Colors.reset}\n'
                )

                player.reset_num = 1

                time.sleep(2)

            elif player.reset_num == 1:
                print(
                    f'\nНезнакомец: {Colors.blue_dark}Хорошо! Ваше решение принято.{Colors.reset}\n'
                )

                time.sleep(1)

                if os.path.exists(db_file):  # FIXME: DB_FILE
                    try:
                        os.remove(db_file)

                        print(
                            f'{Colors.green}Успешно! Все сохранения стёрты. База данных game.db удалена.{Colors.reset}\n'
                        )

                        sys.exit()

                    except PermissionError:
                        print(
                            f'{Colors.red}Ошибка! Не удалось удалить базу данных. Закройте сторонние программы/клиенты БД и попробуйте снова.{Colors.reset}\n'
                        )

                        player.reset_num = 0

                else:
                    print(
                        f'{Colors.red}Ошибка! Файл базы данных game.db не найден.{Colors.reset}\n'
                    )

                    player.reset_num = 0

        # Неизвестный пункт
        else:
            player.reset_num = 0

            print(f'\n{Colors.red}Неизвестный пункт меню: {user_digit}{Colors.reset} \n')


# Запуск игры
if __name__ == '__main__':
    main()
