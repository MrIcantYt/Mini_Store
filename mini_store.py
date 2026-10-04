from colorama import init

import random
import os
import sqlite3
import time
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')

init()

promo = "MrIcant"
shop_file = "mini_store_shop.txt"
default_shop_content = (
    "1. Множитель монет x2 — Цена: 100 монет (ID: 1)\n"
    "2. Множитель опыта x2 — Цена: 200 монет (ID: 2)\n"
    "3. Счастливый Амулет — Цена: 300 монет (ID: 3)\n"
    "4. Майнинг-ферма — Цена: 300 монет (ID: 4)\n"
    "5. Зелье удачи — Цена: 500 монет (ID: 5)\n"
    "6. Cчастливый тикет — Цена: 400 монет (ID: 6)\n"
    "7. Кофе — Цена: 700 монет (ID: 7)\n"
    "8. Пассивный бизнес — Цена: 1200 монет (ID: 8)"
)
db_file = "game.db"

# Цвета
red = "\033[31m" # Красный
green = "\033[32m" # Зелёный
yellow = "\033[33m" # Жёлтый
blue_dark = "\033[34m" # Синий
blue = "\033[36m" # Голубой
reset = "\033[0m" # Сбрасывает цвет

# Загрузка БД если её нету
def init_db():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            balance INTEGER DEFAULT 0,
            balance_x2 BOOLEAN DEFAULT 0,
            promo_used BOOLEAN DEFAULT 0,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            xp_x2 BOOLEAN DEFAULT 0,
            lucky_amulet BOOLEAN DEFAULT 0,
            secret_used BOOLEAN DEFAULT 0,
            bought INTEGER DEFAULT 0,
            mining_lvl INTEGER DEFAULT 0,
            potion_luck BOOLEAN DEFAULT 0,
            lucky_ticket BOOLEAN DEFAULT 0,
            mining_boost BOOLEAN DEFAULT 0,
            buy_num_boost INTEGER DEFAULT 0,
            business BOOLEAN DEFAULT 0
        )
    """)

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN rebirths INTEGER DEFAULT 0")

    except sqlite3.OperationalError:
        pass

    cursor.execute("SELECT COUNT(*) FROM users")

    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (id) VALUES (1)")

    conn.commit()
    conn.close()

# Загрузка игры
def load_game():
    init_db()

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("SELECT balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business FROM users WHERE id = 1")
    row = cursor.fetchone()
    conn.close()

    return (
        row[0], bool(row[1]), bool(row[2]), row[3], row[4],
        bool(row[5]), bool(row[6]), bool(row[7]), row[8], row[9],
        bool(row[10]), bool(row[11]), bool(row[12]), row[13], bool(row[14])
    )

# Сохранение игры
def save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users SET
            balance = ?, balance_x2 = ?, promo_used = ?, xp = ?, level = ?,
            xp_x2 = ?, lucky_amulet = ?, secret_used = ?, bought = ?, mining_lvl = ?,
            potion_luck = ?, lucky_ticket = ?, mining_boost = ?, buy_num_boost = ?, business = ?
        WHERE id = 1
    """, (balance, int(balance_x2), int(promo_used), xp, level, int(xp_x2), int(lucky_amulet), int(secret_used), bought, mining_lvl, int(potion_luck), int(lucky_ticket), int(mining_boost), buy_num_boost, int(business)))

    conn.commit()
    conn.close()

# Создание магазина, если его нету
def create_shop_if_not_exists():
    if not os.path.exists(shop_file):
        with open(shop_file, "w", encoding="utf-8") as file:
            file.write(default_shop_content)

# Проверка опыта, чтобы обновить лвл
def check_level_up(xp, level, balance, green, reset, yellow):
    if level >= 100:
        if xp > 0:
            gold_bonus = xp * 2  # 1 XP = 2 монеты

            balance += gold_bonus

            print(f"{yellow}⭐ МАКСИМАЛЬНЫЙ УРОВЕНЬ! {fmt(xp)} XP были конвертированы в +{fmt(gold_bonus)} монет!{reset}\n")

        return 0, 100, balance

    xp_needed = level * 100

    while xp >= xp_needed:
        xp -= xp_needed
        level += 1

        print(f"{green}🎉 ПОЗДРАВЛЯЕМ! Вы достигли {level} уровня! 🎉 {reset}\n")

        time.sleep(0.5)

        if level >= 100:
            print(f"{yellow}⭐ Вы достигли МАКСИМАЛЬНОГО 100 уровня! Теперь опыт превращается в монеты!{reset}\n")

            return 0, 100, balance

        xp_needed = level * 100

    return xp, level, balance

# Игра: Угадай число
def game_guess_number(balance, balance_x2, xp, xp_x2, level, lucky_amulet, green, reset, red, lucky_ticket, potion_luck):
    print(f"\n {yellow}== Игра: Угадай число == {reset}\n")

    try:
        choose = int(input(f"Выберите сложность {green}Лёгкая (1){reset}, {yellow}Средняя (2){reset}, {red}Сложная (3){reset}: "))

        if choose == 1:
            number, num = random.randint(1, 15), 15

        elif choose == 2:
            number, num = random.randint(1, 25), 25

        elif choose == 3:
            number, num = random.randint(1, 50), 50

        else:
            print(f"\n{red}Ошибка! Выбрана несуществующая сложность. Возврат в меню.{reset}\n")

            return balance, xp

        life = 4 if lucky_amulet else 3

        while life > 0:
            try:
                user_number = int(input(f"Введите число (От 1 до {num}): "))

            except ValueError:
                print(f"\n{red}Ошибка! Введите целое число. {reset}\n")
                continue

            life -= 1

            if lucky_ticket:
                lucky_ticket = False
                life += 1

                print(f"\n🎫 {yellow}Счастливый тикет сработал и спас вашу жизнь!{reset}")

            if user_number == number:
                luck = random.randint(1, 100)
                chance = 35 if potion_luck else 15

                if choose == 1:
                    base_reward = 50 if luck <= chance else 25

                elif choose == 2:
                    base_reward = 100 if luck <= chance else 50

                elif choose == 3:
                    base_reward = 150 if luck <= chance else 75

                level_multiplier = 1.0 + (level - 1) * 0.1

                reward_coins = int(base_reward * level_multiplier * (2 if balance_x2 else 1))

                if choose == 1:
                    reward_xp = 80 if xp_x2 else 40

                elif choose == 2:
                    reward_xp = 160 if xp_x2 else 80

                elif choose == 3:
                    reward_xp = 320 if xp_x2 else 160

                if luck <= chance:
                    reward_xp *= 2

                    print("\n💥 КРИТИЧЕСКИЙ УДАР! Вы разнесли систему в пух и прах! Награда умножена!")

                print(f"\n🎉 {green}Поздравляю! Вы победили! {reset}")
                print(f"💰 Вы получили {yellow}{fmt(reward_coins)}{reset} монет (Множитель уровня: {yellow}{level_multiplier:.1f}x{reset})!")
                print(f"📈 Вам начислено {yellow}{fmt(reward_xp)}{reset} XP!\n")

                return balance + reward_coins, xp + reward_xp

            elif life == 0:
                print(f"\n{red}Вы програли! Загаданное число было: {number}. {reset}\n")
                return balance, xp

            elif user_number > number:
                print(f"\nЗагаданное число меньше! Осталось жизней: {life}\n")

            elif user_number < number:
                print(f"\nЗагаданное число больше! Осталось жизней: {life}\n")

        return balance, xp

    except (ValueError, TypeError):
        print(f"\n{red}Ошибка! Введите корректное число. {reset}\n")

        return balance, xp

# Игра: Камень, ножницы, бумага
def game_rock_scissors_paper(balance, balance_x2, xp, xp_x2, level, lucky_amulet, green, yellow, reset, red, lucky_ticket, potion_luck):
    print(f"\n {yellow}== Игра: Камень, ножницы, бумага == {reset}\n")

    variants = ["камень", "ножницы", "бумага"]

    life = 4 if lucky_amulet else 3

    while life > 0:
        user_choice = input("Выберите (Камень, Ножницы, Бумага): ").lower().strip()

        if user_choice not in variants:
            print(f"\n{red}Неверный выбор! Напишите: камень, ножницы или бумага. {reset}\n")
            continue

        bot_choice = random.choice(variants)

        print(f"\nБот выбрал: {bot_choice}\n")

        if (user_choice == "камень" and bot_choice == "ножницы") or \
           (user_choice == "ножницы" and bot_choice == "бумага") or \
           (user_choice == "бумага" and bot_choice == "камень"):
            luck = random.randint(1, 100)
            chance = 35 if potion_luck else 15

            base_reward = 50 if luck <= chance else 25
            reward_xp = 40 if xp_x2 else 20

            level_multiplier = 1.0 + (level - 1) * 0.1
            reward_coins = int(base_reward * level_multiplier * (2 if balance_x2 else 1))

            if luck <= chance:
                reward_xp *= 2

                print("💥 КРИТИЧЕСКИЙ УДАР! Вы разнесли систему в пух и прах! Награда умножена!\n")

            print(f"🎉 {green}Поздравляю! Вы победили! {reset}")
            print(f"💰 Вы получили {yellow}{fmt(reward_coins)}{reset} монет (Множитель уровня: {yellow}{level_multiplier:.1f}x{reset})!")
            print(f"📈 Вам начислено {yellow}{fmt(reward_xp)}{reset} XP!\n")

            return balance + reward_coins, xp + reward_xp

        elif user_choice == bot_choice:
            print(f"{yellow}Ничья! Продолжаем... {reset}\n")

        else:
            life -= 1

            if lucky_ticket:
                lucky_ticket = False
                life += 1

                print(f"🎫 {yellow}Счастливый тикет сработал и спас вашу жизнь!{reset}\n")

            print(f"Вы не угадали! У вас осталось {life} жизни!\n")

            if life == 0:
                print(f"{red}Вы полностью проиграли в этой игре! {reset}\n")

    return balance, xp

# Игра: Игровой Автомат
def gaming_machine(balance, balance_x2, xp, xp_x2, green, yellow, reset, red, potion_luck):
    print(f"\n {yellow}== Игра: Игровой Автомат =={reset}\n")

    if not potion_luck:
        variants = ["🍒", "🍒", "🍒", "🍒", "💎", "💎", "👑"]

        slot1 = random.choice(variants)
        slot2 = random.choice(variants)
        slot3 = random.choice(variants)

    elif potion_luck:
        variants = ["🍒", "🍒", "🍒", "🍒", "💎", "💎", "💎", "👑", "👑"]

        slot1 = random.choice(variants)
        slot2 = random.choice(variants)
        slot3 = random.choice(variants)

    user_input = input(f"Введите вашу ставку или 'all'/'все' (Ваш баланс: {fmt(balance)}): ").strip().lower()

    try:
        if user_input == "all" or user_input == "все":
            money_player = balance

        else:
            money_player = int(user_input)

    except ValueError:
        print(f"\n{red}Ошибка! Введите корректное число или слово 'all'/'все'.{reset}\n")
        return balance, xp

    if money_player <= 0:
        print(f"\n{red}Ошибка! Ставка {fmt(balance)} монет невозможна! Нельзя играть на 0 или меньше.{reset}\n")
        return balance, xp

    elif money_player > balance:
        print(f"\n{red}Ошибка! Нельзя вводить ставку больше своего баланса! {reset}\n")
        return balance, xp

    balance -= money_player

    if money_player == 777 and balance >= 777:
        print(f"\n{yellow}⚡ ВНИМАНИЕ! Активирован VIP-режим ХАЙРОЛЛЕРА «777»!⚡{reset}")
        print(f"{red}Ставки максимальны. Риск удвоен. Выигрыш колоссален!{reset}")

        print("\n| 🎰 БAРAБAНЫ VIP-AВТОМAТA СТРЕМИТЕЛЬНО ВРAЩAЮТСЯ... 🎰 |")

    else:
        print("\n| 🎰 БAРAБAНЫ КРУТЯТСЯ... 🎰 |")

    time.sleep(0.4)
    print(f" [{slot1}] ")
    time.sleep(0.4)
    print(f" [{slot1}] [{slot2}] ")
    time.sleep(0.4)
    print(f" [{slot1}] [{slot2}] [{slot3}] \n")
    time.sleep(0.4)

    if slot1 == slot2 == slot3 == "👑":
        if money_player == 777 and balance >= 777:
            win_coins = int(money_player * 15 * (2 if balance_x2 else 1))
            win_xp = 240 if xp_x2 else 120

            print(f"\n{green}🔥 ЛЕГЕНДАРНЫЙ VIP-ДЖЕКПОТ! 15x МНОЖИТЕЛЬ СРАБОТАЛ! 🔥{reset}")
            print(f"💰 Вы выиграли {yellow}{fmt(win_coins)}{reset} монет и получили {yellow}{fmt(win_xp)}{reset} XP!\n")

            return balance + win_coins, xp + win_xp

        else:
            win_coins = int(money_player * 7 * (2 if balance_x2 else 1))
            win_xp = 120 if xp_x2 else 60

            print(f"{green}🔥 ДЖЕКПОТ! У вас выпали три КОРОНЫ! 🔥 {reset}")
            print(f"💰 Вы выиграли {yellow}{fmt(win_coins)}{reset} монет и получили {yellow}{fmt(win_xp)}{reset} XP!\n")

            return balance + win_coins, xp + win_xp

    elif slot1 == slot2 == slot3 == "💎":
        if money_player == 777 and balance >= 777:
            win_coins = int(money_player * 8 * (2 if balance_x2 else 1))
            win_xp = 160 if xp_x2 else 80

            print(f"{green}💎 VIP-КРИСТАЛЛЫ! Отличная комбинация хайроллера! {reset}")
            print(f"💰 Вы выиграли {yellow}{fmt(win_coins)}{reset} монет и получили {yellow}{fmt(win_xp)}{reset} XP!\n")

            return balance + win_coins, xp + win_xp

        else:
            win_coins = int(money_player * 4 * (2 if balance_x2 else 1))
            win_xp = 80 if xp_x2 else 40

            print(f"{green}💎 КРИСТАЛЛЫ! Отличная комбинация! {reset}")
            print(f"💰 Вы выиграли {yellow}{fmt(win_coins)}{reset} монет и получили {yellow}{fmt(win_xp)}{reset} XP!\n")

            return balance + win_coins, xp + win_xp

    elif slot1 == slot2 == slot3 == "🍒":
        if money_player == 777 and balance >= 777:
            win_coins = int(money_player * 4 * (2 if balance_x2 else 1))
            win_xp = 80 if xp_x2 else 40

            print(f"{green}🍒 VIP-Выигрыш на вишнях! Награда увеличена до 4х! {reset}")
            print(f"💰 Вы выиграли {yellow}{fmt(win_coins)}{reset} монет и получили {yellow}{fmt(win_xp)}{reset} XP!\n")

            return balance + win_coins, xp + win_xp

        else:
            win_coins = int(money_player * 2 * (2 if balance_x2 else 1))
            win_xp = 40 if xp_x2 else 20

            print(f"{green}🍒 Обычный выигрыш! Три вишни в ряд! {reset}")
            print(f"💰 Вы выиграли {yellow}{fmt(win_coins)}{reset} монет и получили {yellow}{fmt(win_xp)}{reset} XP!\n")

            return balance + win_coins, xp + win_xp

    else:
        if money_player == 777 and balance >= 777:
            print(f"{red}💥 КРАХ ХАЙРОЛЛЕРА! Слот заблокирован. С вашего баланса списан ДВОЙНОЙ штраф за риск!{reset}\n")

            balance -= money_player

        else:
            print("🔴 Увы, комбинация пустая. Вы потеряли свою ставку. Попробуйте еще раз!\n")

        return balance, xp

# Игра: Блекджек (21 очко)
def blackjack(balance, balance_x2, xp, xp_x2, level, green, yellow, reset, red):
    print(f"\n {yellow}== Игра: Блекджек (21 очко) =={reset}\n")

    cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
    player_score = 0
    bot_score = 0

    user_input = input(f"Введите вашу ставку или 'all'/'все', чтобы поставить всё (Ваш баланс: {fmt(balance)}): ").strip().lower()

    try:
        if user_input == "all" or user_input == "все":
            money_player = balance

        else:
            money_player = int(user_input)

    except ValueError:
        print(f"\n{red}Ошибка! Введите корректное число или слово 'all'/'все'.{reset}\n")
        return balance, xp

    if money_player <= 0:
        print(f"\n{red}Ошибка! Ставка {fmt(balance)} монет невозможна! Нельзя играть на 0 или меньше.{reset}\n")
        return balance, xp

    elif money_player > balance:
        print(f"\n{red}Ошибка! Нельзя вводить ставку больше своего баланса!{reset}\n")
        return balance, xp

    balance -= money_player

    player_score += random.choice(cards)
    player_score += random.choice(cards)
    player_overflow = False

    while player_score < 21:
        print(f"\nУ вас на руках: {yellow}{player_score}{reset} очков")

        try:
            user_choice = int(input("1. Взять ещё карту | 2. Остановиться: "))

        except ValueError:
            print(f"\n{red}Ошибка! Введите 1 или 2.{reset}")
            continue

        if user_choice == 1:
            random_cart = random.choice(cards)
            player_score += random_cart

            print(f"Вы вытянули карту: {yellow}{random_cart}{reset}")

            if player_score > 21:
                print(f"\nУ вас на руках: {red}{player_score}{reset} очков")
                print(f"\n{red}💥 Перебор! Вы проиграли свою ставку!{reset}\n")

                player_overflow = True
                break

        elif user_choice == 2:
            break

        else:
            print(f"\n{red}Неверный пункт! Выберите 1 или 2.{reset}\n")

    if player_overflow:
        return balance, xp

    if player_score == 21:
        print(f"\n🎉 {green}ОГО! У вас ровно 21 очко!{reset}")

    print(f"\n{blue}🤖 Очередь Дилера (Бота)...{reset}\n")

    bot_score += random.choice(cards)
    bot_score += random.choice(cards)

    print(f"Стартовые очки бота: {blue}{bot_score}{reset}")

    time.sleep(0.6)

    while bot_score < 17:
        bot_card = random.choice(cards)
        bot_score += bot_card

        print(f"🤖 Бот вытянул карту: {yellow}{bot_card}{reset} (Всего у бота: {bot_score})")

        time.sleep(0.6)

    print(f"\nФинальный счёт дилера: {blue}{bot_score}{reset} очков")

    time.sleep(0.4)

    level_multiplier = 1.0 + (level - 1) * 0.1

    if bot_score > 21 or player_score > bot_score:
        reward_coins = int(money_player * level_multiplier * (2 if balance_x2 else 1))
        reward_xp = 60 if xp_x2 else 30

        balance += (money_player + reward_coins)
        xp += reward_xp

        if bot_score > 21:
            print(f"\n🎉 {green}Бот перебрал ({bot_score} очков)! Вы победили!{reset}")

        else:
            print(f"\n🎉 {green}Поздравляю! У вас больше очков. Вы победили дилера!{reset}")

        print(f"💰 Вы получили {yellow}{fmt(reward_coins)}{reset} монет (Множитель уровня: {yellow}{level_multiplier:.1f}x{reset})!")
        print(f"📈 Вам начислено {yellow}{fmt(reward_xp)}{reset} XP!\n")

    elif player_score == bot_score:
        balance += money_player

        print(f"\n{yellow}🤝 Ничья! Очков поровну ({player_score} vs {bot_score}). Ставка возвращена на баланс.{reset}\n")

    else:
        print(f"\n{red}🔴 У дилера больше очков ({bot_score}). Вы проиграли свою ставку!{reset}\n")

    return balance, xp

# Форматирование чисел
def fmt(value):
    return f"{value:,}".replace(",", ".")

# Главная функция игры
def main():
    create_shop_if_not_exists()

    balance = 0
    balance_x2 = False
    promo_used = False
    lucky_amulet = False
    secret_used = False
    bought = 0
    mining_lvl = 0
    potion_luck = False
    lucky_ticket = False
    mining_boost = False
    buy_num_boost = 0
    business = False
    reset_num = 0

    balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business = load_game()

    print("\n === Добро пожаловать в \"Мини Магазин\" === \n")

    while True:
        print("1. Каталог")
        print("2. Игры")
        print("3. Профиль")
        print("4. Промокод")
        print("5. Майнинг ферма")
        print("6. Выход")
        print(f"\n{red}7. Сброс игры{reset}")

        try:
            user_digit = int(input("\nВведите цифру: "))

        except ValueError:
            print(f"\n{red}Ошибка 666! Введите число!{reset}\n")
            continue

        # Пасхалка
        if user_digit == 666:
            reset_num = 0

            if not secret_used:
                balance += 100
                secret_used = True

                save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                print()

            continue

        # Пассивный бизнес
        if business:
            print(f"\nНезнакомец: {blue_dark}Стартап принёс доход: {yellow}+25 монет{blue_dark}.{reset}")

            balance += 25

            save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

            pass

        # Максимальный баланс
        if balance > 999999999:
            balance = 999999999

            save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

        # Магазин
        if user_digit == 1:
            reset_num = 0

            try:
                with open(shop_file, "r", encoding="utf-8") as file:
                    print("\n===============\n")
                    print(file.read())
                    print("\n===============\n")

                try:
                    user_id_buy_or_return = int(input("Купить или вернуть? (1 or 2): "))

                    if user_id_buy_or_return == 1:
                        try:
                            user_id_buy = int(input("\nВыберите ID продукта для покупки: "))

                            if user_id_buy == 1:
                                if balance_x2:
                                    print(f"\n{yellow}Вы уже купили этот товар!{reset}\n")

                                elif balance >= 100:
                                    balance -= 100
                                    balance_x2 = True

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                                    print(f"\n{green}Успешно! Списано 100 монет, теперь у вас x2 бонус к выигрышу!{reset}\n")

                                else:
                                    print(f"\n{red}Недостаточно монет! Нужно 100, а у вас {balance}.{reset}\n")

                            elif user_id_buy == 2:
                                if xp_x2:
                                    print(f"\n{yellow}Вы уже купили этот товар!{reset}\n")

                                    bought += 1

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                                    if bought == 3:
                                        print("Незнакомец: Вам не надоело тыкать на купленный товар?\n")

                                        save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                                    elif bought == 5:
                                        print("Незнакомец: Всё, хорошо, держите 100 монет. Если ещё раз тыкнете, то с вас спишется 100 монет!\n")

                                        balance += 100

                                        save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                                    elif bought == 6:
                                        print("Незнакомец: Я вас предупреждал!\n")

                                        balance -= 100

                                        save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                                elif balance >= 200:
                                    balance -= 200
                                    xp_x2 = True

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                                    print(f"\n{green}Успешно! Списано 200 монет, теперь у вас x2 бонус к опыту!{reset}\n")

                                else:
                                    print(f"\n{red}Недостаточно монет! Нужно 200, а у вас {balance}.{reset}\n")

                            elif user_id_buy == 3:
                                if lucky_amulet:
                                    print(f"\n{yellow}Вы уже купили этот товар!{reset}\n")

                                elif balance >= 300:
                                    balance -= 300
                                    lucky_amulet = True

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                                    print(f"\n{green}Успешно! Списано 300 монет, теперь у вас есть Счастливый Амулет (+1 жизнь)!{reset}\n")

                                else:
                                    print(f"\n{red}Недостаточно монет! Нужно 300, а у вас {balance}.{reset}\n")

                            elif user_id_buy == 4:
                                if mining_lvl >= 10:
                                    print(f"\n{yellow}Вы уже купили Майнинг-ферму по максималке!{reset}\n")

                                else:
                                    result_mining_lvl_mon = 300 * (mining_lvl + 1) if mining_lvl != 0 else 300

                                    if balance >= result_mining_lvl_mon:
                                        balance -= result_mining_lvl_mon
                                        mining_lvl += 1

                                        save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                                        print(f"\n{green}Успешно! Списано {fmt(result_mining_lvl_mon)} монет, теперь у вас есть Майнинг ферма (лвл: {mining_lvl})!")
                                        print(f"Следующая прокачка будет стоить: {f"{fmt(300 * (mining_lvl + 1))} монет." if mining_lvl != 10 else "MAX прокачка."}")
                                        print(f"\nУ вас на балансе: {fmt(balance)} монет.{reset}\n")

                                    else:
                                        print(f"\n{red}Недостаточно монет! Нужно {fmt(result_mining_lvl_mon)}, а у вас {fmt(balance)}.{reset}\n")

                            elif user_id_buy == 5:
                                if potion_luck:
                                    print(f"\n{yellow}Вы уже купили этот товар!{reset}\n")

                                elif balance >= 500:
                                    balance -= 500
                                    potion_luck = True

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                                    print(f"\n{green}Успешно! Списано 500 монет, теперь у вас есть Счастливое Зелье (Больше шансов в Казино)!{reset}\n")

                                else:
                                    print(f"\n{red}Недостаточно монет! Нужно 500, а у вас {balance}.{reset}\n")

                            elif user_id_buy == 6:
                                if lucky_ticket:
                                    print(f"\n{yellow}Вы уже купили этот товар!{reset}\n")

                                elif balance >= 400:
                                    balance -= 400
                                    lucky_ticket = True

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                                    print(f"\n{green}Успешно! Списано 400 монет, теперь у вас есть Счастливый Тикет (Не вычитается жизнь при первой попыткой)!{reset}\n")

                                else:
                                    print(f"\n{red}Недостаточно монет! Нужно 400, а у вас {balance}.{reset}\n")

                            elif user_id_buy == 7:
                                if mining_boost:
                                    print(f"\n{yellow}Вы уже купили этот товар!{reset}\n")

                                elif balance >= 700:
                                    if buy_num_boost == 0:
                                        print(f"\nНезнакомец: {blue_dark}Хм... Кофе? Ты уверен? Это не обычный напиток. Его аромат способен разогнать до предела любую электронику... Точно берешь?{reset}\n")
                                        time.sleep(5)

                                        buy_num_boost = 1

                                        save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                                    elif buy_num_boost == 1:
                                        print(f"\nНезнакомец: {blue_dark}Отличный выбор. Твоя Майнинг-ферма скажет тебе спасибо. Работа пойдет в два раза быстрее!{reset}\n")
                                        balance -= 700
                                        mining_boost = True

                                        save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                                        time.sleep(5)

                                        print(f"{green}Успешно! Списано 700 монет, теперь у вас есть Кофе (Майнинг ускорен)!{reset}\n")

                                else:
                                    print(f"\n{red}Недостаточно монет! Нужно 700, а у вас {balance}.{reset}\n")

                            elif user_id_buy == 8:
                                if business:
                                    print(f"\n{yellow}Вы уже купили этот товар!{reset}\n")

                                elif balance >= 1200:
                                    balance -= 1200
                                    business = True

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                                    print(f"\n{green}Успешно! Списано 1.200 монет, теперь у вас есть Пассивный бизнес (За каждый ход в меню +25 монет на баланс)!{reset}\n")

                                else:
                                    print(f"\n{red}Недостаточно монет! Нужно 1.200, а у вас {fmt(balance)}.{reset}\n")

                            else:
                                print(f"\n{red}Товара с таким ID не существует!{reset}\n")

                        except ValueError:
                            print(f"\n{red}Ошибка! Введите корректный ID числом!\n{reset}")

                    elif user_id_buy_or_return == 2:
                        user_id_return = int(input("\nВыберите ID продукта для возращение товара: "))

                        if user_id_return == 1:
                            if balance_x2:
                                print(f"\n{green}Успешно! Вы вернули \"x2 бонус к монетам\"! К вашему балансу было прибавлено 50 монет!{reset}\n")

                                balance_x2 = False
                                balance += 50

                                save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                            else:
                                print(f"\n{red}У вас не куплено \"x2 бонус к монетам\"!{reset}\n")

                        elif user_id_return == 2:
                            if xp_x2:
                                print(f"\n{green}Успешно! Вы вернули \"x2 бонус к опыту\"! К вашему балансу было прибавлено 100 монет!{reset}\n")

                                xp_x2 = False
                                balance += 100

                                save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                            else:
                                print(f"\n{red}У вас не куплено \"x2 бонус к опыту\"!{reset}\n")

                        elif user_id_return == 3:
                            if lucky_amulet:
                                print(f"\n{green}Успешно! Вы вернули \"Счастливый Амулет\"! К вашему балансу было прибавлено 150 монет!{reset}\n")

                                lucky_amulet = False
                                balance += 150

                                save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                            else:
                                print(f"\n{red}У вас не куплен \"Счастливый Амулет\"!{reset}\n")

                        elif user_id_return == 4:
                            if mining_lvl == 10 and balance >= 5000:
                                print(f"\nНезнакомец: {blue_dark}Ферма 10 лвл демонтирована. За электричество и простой снято {red}5.000 монет{blue_dark}.{reset}\n")

                                balance -= 5000
                                mining_lvl = 0
                                mining_boost = False
                                buy_num_boost = 0

                                save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                                time.sleep(3)

                                print(f"{red}Штраф оплачен! С баланса списано 5.000 монет. Ферма полностью демонтирована.{reset}\n")

                            elif mining_lvl > 0 and mining_lvl < 10:
                                print(f"\nНезнакомец: {blue_dark}Хех, у тебя ферма всего {yellow}{mining_lvl}-го уровня{blue_dark}. Мелкие долги по свету меня не интересуют. Разгони её до максимума (10 LVL), вот тогда и поговорим о демонтаже!{reset}\n")

                            else:
                                print(f"\n{red}У вас не куплена \"Майнинг-ферма\"!{reset}\n")

                        elif user_id_return == 5:
                            if potion_luck:
                                print(f"\n{green}Успешно! Вы вернули \"Зелье Удачи\"! К вашему балансу было прибавлено 250 монет!{reset}\n")

                                potion_luck = False
                                balance += 250

                                save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                            else:
                                print(f"\n{red}У вас не куплено \"Зелье Удачи\"!{reset}\n")

                        elif user_id_return == 6:
                            if lucky_ticket:
                                print(f"\n{green}Успешно! Вы вернули \"Cчастливый Тикет\"! К вашему балансу было прибавлено 200 монет!{reset}\n")

                                lucky_ticket = False
                                balance += 200

                                save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                            else:
                                print(f"\n{red}У вас не куплено \"Счастливый Тикет\"!{reset}\n")

                        elif user_id_return == 7:
                            if mining_boost:
                                print(f"\n{green}Успешно! Вы вернули \"Кофе\"! К вашему балансу было прибавлено 350 монет!{reset}\n")

                                mining_boost = False
                                balance += 350

                                save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                            else:
                                print(f"\n{red}У вас не куплено \"Кофе\"!{reset}\n")

                        elif user_id_return == 8:
                            if business:
                                print(f"\nНезнакомец: {blue_dark}Пассивный бизнес продан за полцены. Вам возвращено {yellow}600 монет{blue_dark}.{reset}\n")

                                balance += 600
                                business = False

                                save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                                time.sleep(3)

                                print(f"{green}Успешно! Пассивный бизнес закрыт, вам начислено +600 монет!{reset}\n")

                            else:
                                print(f"\n{red}У вас не куплен \"Пассивный Бизнес\"!{reset}\n")

                        else:
                            print(f"\n{red}Товара с таким ID не существует в системе возврата!{reset}\n")

                    else:
                        print("\nВозврат в главное меню...\n")
                        continue

                except (ValueError, TypeError):
                    print(f"\n{red}Ошибка! Введите корректное число. {reset}\n")

            except FileNotFoundError:
                print("\n[Магазин временно пуст]\n")

        # Игры
        elif user_digit == 2:
            reset_num = 0

            print("\n1. Угадать число")
            print("2. Камень, ножницы, бумага")
            print("3. Игровой автомат (Слоты) 🎰")
            print("4. Блекджек (21 очко)")

            try:
                user_number_game = int(input("\nВведите число игры: "))

                if user_number_game == 1:
                    balance, xp = game_guess_number(balance, balance_x2, xp, xp_x2, level, lucky_amulet, green, reset, red, lucky_ticket, potion_luck)
                    xp, level, balance = check_level_up(xp, level, balance, green, reset, yellow)

                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                elif user_number_game == 2:
                    balance, xp = game_rock_scissors_paper(balance, balance_x2, xp, xp_x2, level, lucky_amulet, green, yellow, reset, red, lucky_ticket, potion_luck)
                    xp, level, balance = check_level_up(xp, level, balance, green, reset, yellow)

                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                elif user_number_game == 3:
                    balance, xp = gaming_machine(balance, balance_x2, xp, xp_x2, green, yellow, reset, red, potion_luck)
                    xp, level, balance = check_level_up(xp, level, balance, green, reset, yellow)

                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                elif user_number_game == 4:
                    balance, xp = blackjack(balance, balance_x2, xp, xp_x2, level, green, yellow, reset, red)
                    xp, level, balance = check_level_up(xp, level, balance, green, reset, yellow)

                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                else:
                    print(f"\n{red}Такой игры нет.{reset}\n")

            except ValueError:
                print(f"\n{red}Ошибка! Введите число!{reset}\n")

        # Профиль
        elif user_digit == 3:
            reset_num = 0

            level_multiplier = 1.0 + (level - 1) * 0.1
            level_bonus_percent = int((level_multiplier - 1.0) * 100)

            print("\n--- ПРОФИЛЬ ИГРОКА ---\n")
            print(f"Уровень: {yellow}{level}{reset} ⭐")
            print(f"Опыт: {yellow}{fmt(xp)}{reset} / {yellow}{fmt(level * 100)}{reset} XP 📈")
            print(f"Бонус уровня: {yellow}+{level_bonus_percent}%{reset} к доходу ({yellow}{level_multiplier:.1f}x{reset})")
            print(f"Баланс: {yellow}{fmt(balance)}{reset} монет 💰")

            print("\nКупленные предметы:")
            has_items = False

            if balance_x2:
                print(f" - Множитель монет x2 {green}[Активен]{reset}")
                has_items = True

            if xp_x2:
                print(f" - Множитель опыта x2 {green}[Активен]{reset}")
                has_items = True

            if lucky_amulet:
                print(f" - Счастливый Амулет {green}[+1 жизнь]{reset}")
                has_items = True

            if potion_luck:
                print(f" - Зелье Удачи {green}[Шанс в казино повышен]{reset}")
                has_items = True

            if lucky_ticket:
                print(f" - Счастливый Тикет {green}[Защита от 1 проигрыша]{reset}")
                has_items = True

            if mining_lvl > 0:
                status_coffee = f" {blue}[Кофе ускорил в 2 раза]{reset}" if mining_boost else ""
                print(f" - Майнинг-ферма: {yellow}{mining_lvl} лвл{reset}{status_coffee}")
                has_items = True

            if business:
                print(f" - Пассивный бизнес {green}[+25 монет за ход]{reset}")
                has_items = True

            if not has_items:
                print(f" {red}Рюкзак пуст. Купите что-нибудь в каталоге!{reset}")

            print("\n----------------------\n")

        # Промокод
        elif user_digit == 4:
            reset_num = 0

            if not promo_used:
                user_promo = input("\nВведите промокод: ").strip()

                if user_promo == promo:
                    base_coins = 50
                    base_xp = 30
                    level_multiplier = 1.0 + (level - 1) * 0.1

                    coins_given = int(base_coins * level_multiplier * (2 if balance_x2 else 1))
                    xp_given = int(base_xp * level_multiplier * (2 if xp_x2 else 1))

                    balance += coins_given
                    xp += xp_given
                    promo_used = True

                    print(f"\n🎉 {green}Успешно, промокод был активирован!{reset} ")
                    print(f"💰 Вы получили {yellow}{fmt(coins_given)}{reset} монет (Множитель уровня: {yellow}{level_multiplier:.1f}x{reset})!")
                    print(f"📈 Вам начислено {yellow}{fmt(xp_given)}{reset} XP!\n")

                    xp, level, balance = check_level_up(xp, level, balance, green, reset, yellow)

                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

                else:
                    print(f"\n{red}Промокод не верен! {reset}\n")

            else:
                print(f"\n{yellow}Промокод уже был введён!{reset}\n")

        # Майнинг-ферма
        elif user_digit == 5:
            reset_num = 0

            import msvcrt

            if mining_lvl > 0:
                print(f"\n⛏️ {green}Майнинг-ферма запущена! [Нажмите Q для выхода]{reset}\n")

                while True:
                    balance += 5 * mining_lvl

                    if balance > 999999999:
                        balance = 999999999

                    print(f"Добыча... Ваш баланс: {yellow}{fmt(balance)}{reset} монет 💰", end="\r")

                    sleep_time = 0.5 if mining_boost else 1.0
                    time.sleep(sleep_time)

                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode("utf-8", errors="ignore").lower()

                        if key in "q":
                            print()
                            print(f"\n{green}Майнинг приостановлен. Возврат в меню...{reset}\n")

                            save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)
                            break

            else:
                print(f"\n{red}Сначала купите ферму в каталоге!{reset}\n")

        # Выход
        elif user_digit == 6:
            save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, reset_num)

            print("\nПрогресс сохранен! Прощайте, удачи вам! \n")

            break

        # Удаления БД
        elif user_digit == 7:
            if reset_num == 0:
                print(f"\nНезнакомец: {blue_dark}Вы уверенны, что хотите сбросить весь свой прогресс? (Нажмите 7 ещё раз для подтверждения){reset}\n")

                reset_num = 1

                time.sleep(2)

            elif reset_num == 1:
                print(f"\nНезнакомец: {blue_dark}Хорошо! Ваше решение принято.{reset}\n")

                time.sleep(1)

                if os.path.exists(db_file):
                    try:
                        os.remove(db_file)

                        print(f"{green}Успешно! Все сохранения стёрты. База данных game.db удалена.{reset}\n")

                        sys.exit()

                    except PermissionError:
                        print(f"{red}Ошибка! Не удалось удалить базу данных. Закройте сторонние программы/клиенты БД и попробуйте снова.{reset}\n")

                        reset_num = 0

                else:
                    print(f"{red}Ошибка! Файл базы данных game.db не найден.{reset}\n")

                    reset_num = 0

        # Неизвестный пункт
        else:
            reset_num = 0

            print(f"\n{red}Неизвестный пункт меню: {user_digit}{reset} \n")

# Запуск игры
if __name__ == "__main__":
    main()
