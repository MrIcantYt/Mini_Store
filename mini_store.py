from colorama import init

from games.guess_number import game_guess_number
from games.rock_scissors_paper import game_rock_scissors_paper
from games.gaming_machine import gaming_machine
from games.blackjack import blackjack
from games.roulette import play_roulette

import random
import os
import sqlite3
import time
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')

init()

PROMO = "MrIcant"
DEFAULT_SHOP_CONTENT = (
    "1. Множитель монет x2 — Цена: 100 монет (ID: 1)\n"
    "2. Множитель опыта x2 — Цена: 200 монет (ID: 2)\n"
    "3. Счастливый Амулет — Цена: 300 монет (ID: 3)\n"
    "4. Майнинг-ферма — Цена: 300 монет (ID: 4)\n"
    "5. Зелье удачи — Цена: 500 монет (ID: 5)\n"
    "6. Cчастливый тикет — Цена: 400 монет (ID: 6)\n"
    "7. Кофе — Цена: 700 монет (ID: 7)\n"
    "8. Пассивный бизнес — Цена: 1200 монет (ID: 8)\n"
    "9. Секретный Кейс (Лутбокс) — Цена: 2500 монет (ID: 9)"
)
db_file = "game.db"

# Цвета
class Colors:
    red = "\033[31m"
    green = "\033[32m"
    yellow = "\033[33m"
    blue_dark = "\033[34m"
    blue = "\033[36m"
    reset = "\033[0m"

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
            business BOOLEAN DEFAULT 0,
            quest_id INTEGER DEFAULT 1,
            quest_progress INTEGER DEFAULT 0
        )
    """)

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN quest_id INTEGER DEFAULT 1")
        cursor.execute("ALTER TABLE users ADD COLUMN quest_progress INTEGER DEFAULT 0")

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

    cursor.execute("SELECT balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress FROM users WHERE id = 1")
    row = cursor.fetchone()
    conn.close()

    return (
        row[0], bool(row[1]), bool(row[2]), row[3], row[4],
        bool(row[5]), bool(row[6]), bool(row[7]), row[8], row[9],
        bool(row[10]), bool(row[11]), bool(row[12]), row[13], bool(row[14]),
        row[15], row[16]
    )

# Сохранение игры
def save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE users SET
            balance = ?, balance_x2 = ?, promo_used = ?, xp = ?, level = ?,
            xp_x2 = ?, lucky_amulet = ?, secret_used = ?, bought = ?, mining_lvl = ?,
            potion_luck = ?, lucky_ticket = ?, mining_boost = ?, buy_num_boost = ?, business = ?,
            quest_id = ?, quest_progress = ?
        WHERE id = 1
    """, (balance, int(balance_x2), int(promo_used), xp, level, int(xp_x2), int(lucky_amulet), int(secret_used), bought, mining_lvl, int(potion_luck), int(lucky_ticket), int(mining_boost), buy_num_boost, int(business), quest_id, quest_progress))
    
    conn.commit()
    conn.close()

# Проверка опыта, чтобы обновить лвл
def check_level_up(xp, level, balance):
    if level >= 100:
        if xp > 0:
            gold_bonus = xp * 2  # 1 XP = 2 монеты

            balance += gold_bonus

            print(f"{Colors.yellow}⭐ МАКСИМАЛЬНЫЙ УРОВЕНЬ! {fmt(xp)} XP были конвертированы в +{fmt(gold_bonus)} монет!{Colors.reset}\n")

        return 0, 100, balance

    xp_needed = level * 100

    while xp >= xp_needed:
        xp -= xp_needed
        level += 1

        print(f"{Colors.green}🎉 ПОЗДРАВЛЯЕМ! Вы достигли {level} уровня! 🎉 {Colors.reset}\n")

        time.sleep(0.5)

        if level >= 100:
            print(f"{Colors.yellow}⭐ Вы достигли МАКСИМАЛЬНОГО 100 уровня! Теперь опыт превращается в монеты!{Colors.reset}\n")

            return 0, 100, balance

        xp_needed = level * 100

    return xp, level, balance

# Форматирование чисел
def fmt(value):
    return f"{value:,}".replace(",", ".")

# Главная функция игры
def main():
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

    balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress = load_game()

    print("\n === Добро пожаловать в \"Мини Магазин\" === \n")

    while True:
        print("1. Каталог")
        print("2. Игры")
        print("3. Профиль")
        print("4. Промокод")
        print("5. Майнинг ферма")
        print("6. Задания Незнакомца")
        print("7. Выход")
        print(f"\n{Colors.red}8. Сброс игры{Colors.reset}")

        try:
            user_digit = int(input("\nВведите цифру: "))

        except ValueError:
            print(f"\n{Colors.red}Ошибка 666! Введите число!{Colors.reset}\n")
            continue

        # Пасхалка
        if user_digit == 666:
            reset_num = 0

            if not secret_used:
                balance += 100
                secret_used = True

                save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                print()

            continue

        # Пассивный бизнес
        if business:
            print(f"\nНезнакомец: {Colors.blue_dark}Стартап принёс доход: {Colors.yellow}+25 монет{Colors.blue_dark}.{Colors.reset}")

            balance += 25

            save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

            pass

        # Максимальный баланс
        if balance > 999999999:
            balance = 999999999

            save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

        # Магазин
        if user_digit == 1:
            reset_num = 0

            print(f"\nВаш баланс: {Colors.yellow}{fmt(balance)} монет{Colors.reset}.")
            print("\n===============\n")
            print(DEFAULT_SHOP_CONTENT)
            print("\n===============\n")

            try:
                user_id_buy_or_return = int(input("Купить или вернуть? (1 or 2): "))

                match user_id_buy_or_return:
                    case 1:
                        user_id_buy = int(input("\nВыберите ID продукта для покупки: "))

                        match user_id_buy:
                            case 1:
                                if balance_x2:
                                    print(f"\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}\n")

                                elif balance >= 100:
                                    balance -= 100
                                    balance_x2 = True

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                                    print(f"\n{Colors.green}Успешно! Списано 100 монет, теперь у вас x2 бонус к выигрышу!{Colors.reset}\n")

                                else:
                                    print(f"\n{Colors.red}Недостаточно монет! Нужно 100, а у вас {balance}.{Colors.reset}\n")

                            case 2:
                                if xp_x2:
                                    print(f"\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}\n")

                                    bought += 1

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                                    if bought == 3:
                                        print("Незнакомец: Вам не надоело тыкать на купленный товар?\n")

                                        save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                                    elif bought == 5:
                                        print("Незнакомец: Всё, хорошо, держите 100 монет. Если ещё раз тыкнете, то с вас спишется 100 монет!\n")

                                        balance += 100

                                        save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                                    elif bought == 6:
                                        print("Незнакомец: Я вас предупреждал!\n")

                                        balance -= 100

                                        save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                                elif balance >= 200:
                                    balance -= 200
                                    xp_x2 = True

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                                    print(f"\n{Colors.green}Успешно! Списано 200 монет, теперь у вас x2 бонус к опыту!{Colors.reset}\n")

                                else:
                                    print(f"\n{Colors.red}Недостаточно монет! Нужно 200, а у вас {balance}.{Colors.reset}\n")

                            case 3:
                                if lucky_amulet:
                                    print(f"\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}\n")

                                elif balance >= 300:
                                    balance -= 300
                                    lucky_amulet = True

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                                    print(f"\n{Colors.green}Успешно! Списано 300 монет, теперь у вас есть Счастливый Амулет (+1 жизнь)!{Colors.reset}\n")

                                else:
                                    print(f"\n{Colors.red}Недостаточно монет! Нужно 300, а у вас {balance}.{Colors.reset}\n")

                            case 4:
                                if mining_lvl >= 10:
                                    print(f"\n{Colors.yellow}Вы уже купили Майнинг-ферму по максималке!{Colors.reset}\n")

                                else:
                                    result_mining_lvl_mon = 300 * (mining_lvl + 1) if mining_lvl != 0 else 300

                                    if balance >= result_mining_lvl_mon:
                                        balance -= result_mining_lvl_mon
                                        mining_lvl += 1

                                        save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                                        print(f"\n{Colors.green}Успешно! Списано {fmt(result_mining_lvl_mon)} монет, теперь у вас есть Майнинг ферма (лвл: {mining_lvl})!")
                                        print(f"Следующая прокачка будет стоить: {f"{fmt(300 * (mining_lvl + 1))} монет." if mining_lvl != 10 else "MAX прокачка."}")
                                        print(f"\nУ вас на балансе: {fmt(balance)} монет.{Colors.reset}\n")

                                    else:
                                        print(f"\n{Colors.red}Недостаточно монет! Нужно {fmt(result_mining_lvl_mon)}, а у вас {fmt(balance)}.{Colors.reset}\n")

                            case 5:
                                if potion_luck:
                                    print(f"\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}\n")

                                elif balance >= 500:
                                    balance -= 500
                                    potion_luck = True

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                                    print(f"\n{Colors.green}Успешно! Списано 500 монет, теперь у вас есть Счастливое Зелье (Больше шансов в Казино)!{Colors.reset}\n")

                                else:
                                    print(f"\n{Colors.red}Недостаточно монет! Нужно 500, а у вас {balance}.{Colors.reset}\n")

                            case 6:
                                if lucky_ticket:
                                    print(f"\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}\n")

                                elif balance >= 400:
                                    balance -= 400
                                    lucky_ticket = True

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                                    print(f"\n{Colors.green}Успешно! Списано 400 монет, теперь у вас есть Счастливый Тикет (Не вычитается жизнь при первой попыткой)!{Colors.reset}\n")

                                else:
                                    print(f"\n{Colors.red}Недостаточно монет! Нужно 400, а у вас {balance}.{Colors.reset}\n")

                            case 7:
                                if mining_boost:
                                    print(f"\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}\n")

                                elif balance >= 700:
                                    if buy_num_boost == 0:
                                        print(f"\nНезнакомец: {Colors.blue_dark}Хм... Кофе? Ты уверен? Это не обычный напиток. Его аромат способен разогнать до предела любую электронику... Точно берешь?{Colors.reset}\n")
                                            
                                        time.sleep(3)

                                        buy_num_boost = 1

                                        save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                                    elif buy_num_boost == 1:
                                        print(f"\nНезнакомец: {Colors.blue_dark}Отличный выбор. Твоя Майнинг-ферма скажет тебе спасибо. Работа пойдет в два раза быстрее!{Colors.reset}\n")

                                        balance -= 700
                                        mining_boost = True

                                        save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                                        time.sleep(3)

                                        print(f"{Colors.green}Успешно! Списано 700 монет, теперь у вас есть Кофе (Майнинг ускорен)!{Colors.reset}\n")

                                else:
                                    print(f"\n{Colors.red}Недостаточно монет! Нужно 700, а у вас {balance}.{Colors.reset}\n")

                            case 8:
                                if business:
                                    print(f"\n{Colors.yellow}Вы уже купили этот товар!{Colors.reset}\n")

                                elif balance >= 1200:
                                    balance -= 1200
                                    business = True

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                                    print(f"\n{Colors.green}Успешно! Списано 1.200 монет, теперь у вас есть Пассивный бизнес (За каждый ход в меню +25 монет на баланс)!{Colors.reset}\n")

                                else:
                                    print(f"\n{Colors.red}Недостаточно монет! Нужно 1.200, а у вас {fmt(balance)}.{Colors.reset}\n")
                            
                            case 9:
                                if balance >= 2500:
                                    balance -= 2500

                                    case_rewards = [1250, 2500, 5000]
                                    win_money = random.choice(case_rewards)
                                    balance += win_money

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                                    print(f"\n{Colors.green}Успешно! Куплен Секретный Кейс за 2.500 монет. Открываем...{Colors.reset}")
                                    time.sleep(1.5)
                                    print(f"\n📦 Внутри кейса оказалось: {Colors.yellow}{fmt(win_money)} монет{Colors.reset}!")
                                    
                                    if win_money == 5000:
                                        print(f"{Colors.green}🔥 ОГО! ЛУЧШИЙ ДРОП! Вы удвоили свои вложения!{Colors.reset}\n")
                                    
                                    elif win_money == 1250:
                                        print(f"{Colors.red}Эх, Незнакомец подсунул дешёвку. Повезёт в следующий раз!{Colors.reset}\n")
                                    
                                    else:
                                        print(f"{Colors.yellow}Нормально, вернули своё в ноль!{Colors.reset}\n")
                                
                                else:
                                    print(f"\n{Colors.red}Недостаточно монет! Нужно 2.500, а у вас {fmt(balance)}.{Colors.reset}\n")

                            case _:
                                print(f"\n{Colors.red}Товара с таким ID не существует!{Colors.reset}\n")

                    case 2:
                        user_id_return = int(input("\nВыберите ID продукта для возращение товара: "))

                        match user_id_return:
                            case 1:
                                if balance_x2:
                                    print(f"\n{Colors.green}Успешно! Вы вернули \"x2 бонус к монетам\"! К вашему балансу было прибавлено 50 монет!{Colors.reset}\n")

                                    balance_x2 = False
                                    balance += 50

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                                else:
                                    print(f"\n{Colors.red}У вас не куплено \"x2 бонус к монетам\"!{Colors.reset}\n")

                            case 2:
                                if xp_x2:
                                    print(f"\n{Colors.green}Успешно! Вы вернули \"x2 бонус к опыту\"! К вашему балансу было прибавлено 100 монет!{Colors.reset}\n")

                                    xp_x2 = False
                                    balance += 100

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                                else:
                                    print(f"\n{Colors.red}У вас не куплено \"x2 бонус к опыту\"!{Colors.reset}\n")

                            case 3:
                                if lucky_amulet:
                                    print(f"\n{Colors.green}Успешно! Вы вернули \"Счастливый Амулет\"! К вашему балансу было прибавлено 150 монет!{Colors.reset}\n")

                                    lucky_amulet = False
                                    balance += 150

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                                else:
                                    print(f"\n{Colors.red}У вас не куплен \"Счастливый Амулет\"!{Colors.reset}\n")

                            case 4:
                                if mining_lvl == 10 and balance >= 5000:
                                    print(f"\nНезнакомец: {Colors.blue_dark}Ферма 10 лвл демонтирована. За электричество и простой снято {Colors.red}5.000 монет{Colors.blue_dark}.{Colors.reset}\n")

                                    balance -= 5000
                                    mining_lvl = 0
                                    mining_boost = False
                                    buy_num_boost = 0

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                                    time.sleep(3)

                                    print(f"{Colors.red}Штраф оплачен! С баланса списано 5.000 монет. Ферма полностью демонтирована.{Colors.reset}\n")

                                elif mining_lvl > 0 and mining_lvl < 10:
                                    print(f"\nНезнакомец: {Colors.blue_dark}Хех, у тебя ферма всего {Colors.yellow}{mining_lvl}-го уровня{Colors.blue_dark}. Мелкие долги по свету меня не интересуют. Разгони её до максимума (10 LVL), вот тогда и поговорим о демонтаже!{Colors.reset}\n")

                                else:
                                    print(f"\n{Colors.red}У вас не куплена \"Майнинг-ферма\"!{Colors.reset}\n")

                            case 5:
                                if potion_luck:
                                    print(f"\n{Colors.green}Успешно! Вы вернули \"Зелье Удачи\"! К вашему балансу было прибавлено 250 монет!{Colors.reset}\n")

                                    potion_luck = False
                                    balance += 250

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                                else:
                                    print(f"\n{Colors.red}У вас не куплено \"Зелье Удачи\"!{Colors.reset}\n")

                            case 6:
                                if lucky_ticket:
                                    print(f"\n{Colors.green}Успешно! Вы вернули \"Cчастливый Тикет\"! К вашему балансу было прибавлено 200 монет!{Colors.reset}\n")

                                    lucky_ticket = False
                                    balance += 200

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                                else:
                                    print(f"\n{Colors.red}У вас не куплено \"Счастливый Тикет\"!{Colors.reset}\n")

                            case 7:
                                if mining_boost:
                                    print(f"\n{Colors.green}Успешно! Вы вернули \"Кофе\"! К вашему балансу было прибавлено 350 монет!{Colors.reset}\n")

                                    mining_boost = False
                                    balance += 350

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                                else:
                                    print(f"\n{Colors.red}У вас не куплено \"Кофе\"!{Colors.reset}\n")

                            case 8:
                                if business:
                                    print(f"\nНезнакомец: {Colors.blue_dark}Пассивный бизнес продан за полцены. Вам возвращено {Colors.yellow}600 монет{Colors.blue_dark}.{Colors.reset}\n")

                                    balance += 600
                                    business = False

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                                    time.sleep(3)

                                    print(f"{Colors.green}Успешно! Пассивный бизнес закрыт, вам начислено +600 монет!{Colors.reset}\n")

                                else:
                                    print(f"\n{Colors.red}У вас не куплен \"Пассивный Бизнес\"!{Colors.reset}\n")

                            case _:
                                print(f"\n{Colors.red}Товара с таким ID не существует в системе возврата!{Colors.reset}\n")

                    case _:
                        print("\nВозврат в главное меню...\n")
                        continue

            except (ValueError, TypeError):
                print(f"\n{Colors.red}Ошибка! Введите корректное число. {Colors.reset}\n")

        # Игры
        elif user_digit == 2:
            reset_num = 0

            print("\n1. Угадать число")
            print("2. Камень, ножницы, бумага")
            print("3. Игровой автомат (Слоты) 🎰")
            print("4. Блекджек (21 очко)")
            print("5. Колесо Рулетки 🎡")

            try:
                user_number_game = int(input("\nВведите число игры: "))

                if user_number_game == 1:
                    balance, xp = game_guess_number(balance, balance_x2, xp, xp_x2, level, lucky_amulet, lucky_ticket, potion_luck)
                    xp, level, balance = check_level_up(xp, level, balance)

                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                elif user_number_game == 2:
                    balance, xp = game_rock_scissors_paper(balance, balance_x2, xp, xp_x2, level, lucky_amulet, lucky_ticket, potion_luck)
                    xp, level, balance = check_level_up(xp, level, balance)

                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                elif user_number_game == 3:
                    if quest_id == 3:
                        quest_progress += 1

                    balance, xp = gaming_machine(balance, balance_x2, xp, xp_x2, potion_luck)
                    xp, level, balance = check_level_up(xp, level, balance)

                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                elif user_number_game == 4:
                    balance, xp = blackjack(balance, balance_x2, xp, xp_x2, level)
                    xp, level, balance = check_level_up(xp, level, balance)

                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                elif user_number_game == 5:
                    balance, xp = play_roulette(balance, balance_x2, xp, xp_x2, level, potion_luck)
                    xp, level, balance = check_level_up(xp, level, balance)
                    
                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                else:
                    print(f"\n{Colors.red}Такой игры нет.{Colors.reset}\n")

            except ValueError:
                print(f"\n{Colors.red}Ошибка! Введите число!{Colors.reset}\n")

        # Профиль
        elif user_digit == 3:
            reset_num = 0

            level_multiplier = 1.0 + (level - 1) * 0.1
            level_bonus_percent = int((level_multiplier - 1.0) * 100)

            print("\n--- ПРОФИЛЬ ИГРОКА ---\n")
            print(f"Уровень: {Colors.yellow}{level}{Colors.reset} ⭐")
            print(f"Опыт: {Colors.yellow}{fmt(xp)}{Colors.reset} / {Colors.yellow}{fmt(level * 100)}{Colors.reset} XP 📈")
            print(f"Бонус уровня: {Colors.yellow}+{level_bonus_percent}%{Colors.reset} к доходу ({Colors.yellow}{level_multiplier:.1f}x{Colors.reset})")
            print(f"Баланс: {Colors.yellow}{fmt(balance)}{Colors.reset} монет 💰")

            print("\nКупленные предметы:")
            has_items = False

            if balance_x2:
                print(f" - Множитель монет x2 {Colors.green}[Активен]{Colors.reset}")
                has_items = True

            if xp_x2:
                print(f" - Множитель опыта x2 {Colors.green}[Активен]{Colors.reset}")
                has_items = True

            if lucky_amulet:
                print(f" - Счастливый Амулет {Colors.green}[+1 жизнь]{Colors.reset}")
                has_items = True

            if potion_luck:
                print(f" - Зелье Удачи {Colors.green}[Шанс в казино повышен]{Colors.reset}")
                has_items = True

            if lucky_ticket:
                print(f" - Счастливый Тикет {Colors.green}[Защита от 1 проигрыша]{Colors.reset}")
                has_items = True

            if mining_lvl > 0:
                status_coffee = f" {Colors.blue}[Кофе ускорил в 2 раза]{Colors.reset}" if mining_boost else ""
                print(f" - Майнинг-ферма: {Colors.yellow}{mining_lvl} лвл{Colors.reset}{status_coffee}")
                has_items = True

            if business:
                print(f" - Пассивный бизнес {Colors.green}[+25 монет за ход]{Colors.reset}")
                has_items = True

            if not has_items:
                print(f" {Colors.red}Рюкзак пуст. Купите что-нибудь в каталоге!{Colors.reset}")

            print("\n----------------------\n")

        # Промокод
        elif user_digit == 4:
            reset_num = 0

            if not promo_used:
                user_promo = input("\nВведите промокод: ").strip()

                if user_promo == PROMO:
                    base_coins = 50
                    base_xp = 30
                    level_multiplier = 1.0 + (level - 1) * 0.1

                    coins_given = int(base_coins * level_multiplier * (2 if balance_x2 else 1))
                    xp_given = int(base_xp * level_multiplier * (2 if xp_x2 else 1))

                    balance += coins_given
                    xp += xp_given
                    promo_used = True

                    print(f"\n🎉 {Colors.green}Успешно, промокод был активирован!{Colors.reset} ")
                    print(f"💰 Вы получили {Colors.yellow}{fmt(coins_given)}{Colors.reset} монет (Множитель уровня: {Colors.yellow}{level_multiplier:.1f}x{Colors.reset})!")
                    print(f"📈 Вам начислено {Colors.yellow}{fmt(xp_given)}{Colors.reset} XP!\n")

                    xp, level, balance = check_level_up(xp, level, balance)

                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

                else:
                    print(f"\n{Colors.red}Промокод не верен! {Colors.reset}\n")

            else:
                print(f"\n{Colors.yellow}Промокод уже был введён!{Colors.reset}\n")

        # Майнинг-ферма
        elif user_digit == 5:
            reset_num = 0

            import msvcrt

            if mining_lvl > 0:
                print(f"\n⛏️ {Colors.green}Майнинг-ферма запущена! [Нажмите Q для выхода]{Colors.reset}\n")

                while True:
                    balance += 5 * mining_lvl

                    if balance > 999999999:
                        balance = 999999999

                    print(f"Добыча... Ваш баланс: {Colors.yellow}{fmt(balance)}{Colors.reset} монет 💰", end="\r")

                    sleep_time = 0.5 if mining_boost else 1.0
                    time.sleep(sleep_time)

                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode("utf-8", errors="ignore").lower()

                        if key in "q":
                            print()
                            print(f"\n{Colors.green}Майнинг приостановлен. Возврат в меню...{Colors.reset}\n")

                            save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)
                            break

            else:
                print(f"\n{Colors.red}Сначала купите ферму в каталоге!{Colors.reset}\n")

        # Задания Незнакомца
        elif user_digit == 6:
            reset_num = 0

            print("\n--- 📜 ЗАДАНИЯ НЕЗНАКОМЦА ---\n")

            # Квест 1: Стартовый капитал
            if quest_id == 1:
                print(f"Задание 1: {Colors.blue}«Первые шаги»{Colors.reset}")
                print(f"Цель: Накопить {Colors.yellow}500 монет{Colors.reset}. (У вас сейчас: {Colors.yellow}{fmt(balance)} монет{Colors.reset})")
                
                if balance >= 500:
                    xp += 150
                    quest_id = 2
                    
                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)
                    
                    print(f"\n{Colors.green}🎉 Квест выполнен! Награда: +150 XP. Открыто новое задание!{Colors.reset}\n")
                    
                    xp, level, balance = check_level_up(xp, level, balance)
                
                else:
                    print(f"\n{Colors.red}Задание не выполнено. Копи монеты.{Colors.reset}\n")
            
                time.sleep(3)

            # Квест 2: Прокачка железа
            elif quest_id == 2:
                print(f"Задание 2: {Colors.blue}«Разгон фермы»{Colors.reset}")
                print(f"Цель: Прокачать Майнинг-ферму до {Colors.yellow}3 уровня{Colors.reset} или выше. (Ваш уровень: {Colors.yellow}{mining_lvl} лвл{Colors.reset})")
                
                if mining_lvl >= 3:
                    balance += 1000
                    quest_id = 3
                    
                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)
                    
                    print(f"\n{Colors.green}🎉 Квест выполнен! Награда: +1.000 монет. Открыто новое задание!{Colors.reset}\n")
                
                else:
                    print(f"\n{Colors.red}Задание не выполнено. Улучши ферму в Каталоге до 3 лвл.{Colors.reset}\n")
                
                time.sleep(3)
                
            # Квест 3: Испытать удачу в Слотах
            elif quest_id == 3:
                print(f"Задание 3: {Colors.blue}«Азартный тиктокер»{Colors.reset}")
                print(f"Цель: Сыграть в Игровой Автомат (Слоты) {Colors.yellow}5 раз{Colors.reset}. (Прогресс: {Colors.yellow}{quest_progress} / 5{Colors.reset})")
                
                if quest_progress >= 5:
                    balance += 500
                    xp += 300
                    quest_id = 4
                    quest_progress = 0
                    
                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)
                    
                    print(f"\n{Colors.green}🎉 Все задания Незнакомца выполнены! Награда: +500 монет и +300 XP!{Colors.reset}\n")

                    xp, level, balance = check_level_up(xp, level, balance)
                
                else:
                    print(f"\n{Colors.red}Задание выполняется в казино (Пункт 2 -> Игра 3).{Colors.reset}\n")

                time.sleep(3)

            else:
                print(f"{Colors.yellow}Незнакомец: Контракты закончились. Ты выполнил всё, что я просил. Жди обновлений!{Colors.reset}\n")

                time.sleep(3)
                
        # Выход
        elif user_digit == 7:
            save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business, quest_id, quest_progress)

            print("\nПрогресс сохранен! Прощайте, удачи вам! \n")

            break

        # Удаления БД
        elif user_digit == 8:
            if reset_num == 0:
                print(f"\nНезнакомец: {Colors.blue_dark}Вы уверенны, что хотите сбросить весь свой прогресс? (Нажмите 8 ещё раз для подтверждения){Colors.reset}\n")

                reset_num = 1

                time.sleep(2)

            elif reset_num == 1:
                print(f"\nНезнакомец: {Colors.blue_dark}Хорошо! Ваше решение принято.{Colors.reset}\n")

                time.sleep(1)

                if os.path.exists(db_file):
                    try:
                        os.remove(db_file)

                        print(f"{Colors.green}Успешно! Все сохранения стёрты. База данных game.db удалена.{Colors.reset}\n")

                        sys.exit()

                    except PermissionError:
                        print(f"{Colors.red}Ошибка! Не удалось удалить базу данных. Закройте сторонние программы/клиенты БД и попробуйте снова.{Colors.reset}\n")

                        reset_num = 0

                else:
                    print(f"{Colors.red}Ошибка! Файл базы данных game.db не найден.{Colors.reset}\n")

                    reset_num = 0

        # Неизвестный пункт
        else:
            reset_num = 0

            print(f"\n{Colors.red}Неизвестный пункт меню: {user_digit}{Colors.reset} \n")

# Запуск игры
if __name__ == "__main__":
    main()
