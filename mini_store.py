import random
import os
import json

promo = "MrIcant"
shop_file = "mini_store_shop.txt"
default_shop_content = (
    "1. Множитель монет x2 — Цена: 100 монет (ID: 1)\n"
    "2. Множитель опыта x2 — Цена: 200 монет (ID: 2)\n"
    "3. Счастливый Амулет — Цена: 300 монет (ID: 3)"
)
save_file = "save.json"

# Загрузка игры
def load_game():
    if os.path.exists(save_file):
        with open(save_file, "r", encoding="utf-8") as file:
            data = json.load(file)

            return (
                data.get("balance", 0),
                data.get("balance_x2", False),
                data.get("promo_used", False),
                data.get("xp", 0),
                data.get("level", 1),
                data.get("xp_x2", False),
                data.get("lucky_amulet", False),
                data.get("secret_used", False)
            )

    return 0, False, False, 0, 1, False, False, False

# Сохранение игры
def save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used):
    data = {
        "balance": balance,
        "balance_x2": balance_x2,
        "promo_used": promo_used,
        "xp": xp,
        "level": level,
        "xp_x2": xp_x2,
        "lucky_amulet": lucky_amulet,
        "secret_used": secret_used
    }

    with open(save_file, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Создание магазина, если его нету
def create_shop_if_not_exists():
    if not os.path.exists(shop_file):
        with open(shop_file, "w", encoding="utf-8") as file:
            file.write(default_shop_content)

# Проверка опыта чтобы обновить лвл
def check_level_up(xp, level):
    xp_needed = level * 100

    if xp >= xp_needed:
        xp -= xp_needed
        level += 1

        print(f"🎉 ПОЗДРАВЛЯЕМ! Вы достигли {level} уровня! 🎉\n")

    return xp, level

# Игра: Угадай число
def game_guess_number(balance, balance_x2, xp, xp_x2, level, lucky_amulet):
    print("\n == Игра: Угадай число ==\n")

    try:
        choose = int(input("Выберите сложность Лёгкая (1), Средняя (2), Сложная (3): "))

        if choose == 1:

            number = random.randint(1, 15)

            if lucky_amulet:
                life = 4
            else:
                life = 3

            while life > 0:
                try:
                    user_number = int(input("Введите число (От 1 до 15): "))

                except ValueError:
                    print("Ошибка! Введите целое число.")
                    continue

                life -= 1

                if user_number == number:
                    base_reward = 25

                    level_multiplier = 1.0 + (level - 1) * 0.1

                    reward_coins = int(base_reward * level_multiplier * (2 if balance_x2 else 1))
                    reward_xp = 40 if xp_x2 else 20

                    print("\nПоздравляю! Вы победили!")
                    print(f"💰 Вы получили {reward_coins} монет (Множитель уровня: {level_multiplier:.1f}x)!")
                    print(f"📈 Вам начислено {reward_xp} XP!\n")

                    return balance + reward_coins, xp + reward_xp

                elif life == 0:
                    print(f"\nВы програли! Загаданное число было: {number}.\n")

                elif user_number > number:
                    print(f"\nЗагаданное число меньше! Осталось жизней: {life}\n")

                elif user_number < number:
                    print(f"\nЗагаданное число больше! Осталось жизней: {life}\n")

            return balance, xp

        elif choose == 2:
            number = random.randint(1, 25)

            if lucky_amulet:
                life = 4
            else:
                life = 3

            while life > 0:
                try:
                    user_number = int(input("Введите число (От 1 до 25): "))

                except ValueError:
                    print("Ошибка! Введите целое число.")
                    continue

                life -= 1

                if user_number == number:
                    base_reward = 50

                    level_multiplier = 1.0 + (level - 1) * 0.1

                    reward_coins = int(base_reward * level_multiplier * (2 if balance_x2 else 1))
                    reward_xp = 80 if xp_x2 else 40

                    print("\nПоздравляю! Вы победили!")
                    print(f"💰 Вы получили {reward_coins} монет (Множитель уровня: {level_multiplier:.1f}x)!")
                    print(f"📈 Вам начислено {reward_xp} XP!\n")

                    return balance + reward_coins, xp + reward_xp

                elif life == 0:
                    print(f"\nВы програли! Загаданное число было: {number}.\n")

                elif user_number > number:
                    print(f"\nЗагаданное число меньше! Осталось жизней: {life}\n")

                elif user_number < number:
                    print(f"\nЗагаданное число больше! Осталось жизней: {life}\n")

            return balance, xp

        elif choose == 3:
            number = random.randint(1, 50)

            if lucky_amulet:
                life = 4
            else:
                life = 3

            while life > 0:
                try:
                    user_number = int(input("Введите число (От 1 до 50): "))

                except ValueError:
                    print("Ошибка! Введите целое число.")
                    continue

                life -= 1

                if user_number == number:
                    base_reward = 75

                    level_multiplier = 1.0 + (level - 1) * 0.1

                    reward_coins = int(base_reward * level_multiplier * (2 if balance_x2 else 1))
                    reward_xp = 120 if xp_x2 else 60

                    print("\nПоздравляю! Вы победили!")
                    print(f"💰 Вы получили {reward_coins} монет (Множитель уровня: {level_multiplier:.1f}x)!")
                    print(f"📈 Вам начислено {reward_xp} XP!\n")

                    return balance + reward_coins, xp + reward_xp

                elif life == 0:
                    print(f"\nВы програли! Загаданное число было: {number}.\n")

                elif user_number > number:
                    print(f"\nЗагаданное число меньше! Осталось жизней: {life}\n")

                elif user_number < number:
                    print(f"\nЗагаданное число больше! Осталось жизней: {life}\n")

            return balance, xp

        else:
            print("Ошибка! Введите цифру от 1 до 3.")

    except ValueError:
        print("Ошибка! Введите корректное число.")

# Игра: Камень, ножницы, бумага
def game_rock_scissors_paper(balance, balance_x2, xp, xp_x2, level, lucky_amulet):
    print("\n == Игра: Камень, ножницы, бумага ==\n")

    variants = ["камень", "ножницы", "бумага"]

    if lucky_amulet:
        life = 4
    else:
        life = 3

    while life > 0:
        user_choice = input("Выберите (Камень, Ножницы, Бумага): ").lower().strip()

        if user_choice not in variants:
            print("Неверный выбор! Напишите: камень, ножницы или бумага.")
            continue

        bot_choice = random.choice(variants)

        print(f"Бот выбрал: {bot_choice}")

        if (user_choice == "камень" and bot_choice == "ножницы") or \
           (user_choice == "ножницы" and bot_choice == "бумага") or \
           (user_choice == "бумага" and bot_choice == "камень"):
            base_reward = 25

            level_multiplier = 1.0 + (level - 1) * 0.1

            reward_coins = int(base_reward * level_multiplier * (2 if balance_x2 else 1))
            reward_xp = 40 if xp_x2 else 20

            print(f"\nПоздравляю! Вы победили! У вас оставалось {life} жизней.")
            print(f"💰 Вы получили {reward_coins} монет (Множитель уровня: {level_multiplier:.1f}x)!")
            print(f"📈 Вам начислено {reward_xp} XP!\n")

            return balance + reward_coins, xp + reward_xp

        elif user_choice == bot_choice:
            print("Ничья! Продолжаем...\n")

        else:
            life -= 1

            print(f"Вы не угадали! У вас осталось {life} жизни!\n")

            if life == 0:
                print("Вы полностью проиграли в этой игре!\n")

    return balance, xp

# Игра: Игровой Автомат
def gaming_machine(balance, balance_x2, xp, xp_x2, level):
    print("\n == Игра: Игровой Автомат ==\n")

    variants = ["🍒", "🍒", "🍒", "🍒", "💎", "💎", "👑"]

    slot1 = random.choice(variants)
    slot2 = random.choice(variants)
    slot3 = random.choice(variants)

    balance_format = f"{balance:,}".replace(",", ".")
    money_player = int(input(f"Введите вашу ставку (Ваш баланс: {balance_format}): "))
    money_format = f"{money_player:,}".replace(",", ".")

    if money_player <= 0:
        print(f"\nОшибка! Ставка {money_format} монет невозможна! Нельзя играть на 0 или меньше.\n")
        return balance, xp

    elif money_player > balance:
        print("\nОшибка! Нельзя вводить ставку больше своего баланса!\n")
        return balance, xp

    balance -= money_player

    print("\n|  БAРAБAНЫ КРУТЯТСЯ...  |")
    print(f"  [ {slot1} ]  [ {slot2} ]  [ {slot3} ]  \n")

    if slot1 == slot2 == slot3 == "👑":
        win_coins = int(money_player * 7 * (2 if balance_x2 else 1))
        win_xp = 120 if xp_x2 else 60

        win_coins_f = f"{win_coins:,}".replace(",", ".")
        win_xp_f = f"{win_xp:,}".replace(",", ".")

        print("🔥 ДЖЕКПОТ! У вас выпали три КОРОНЫ! 🔥")
        print(f"💰 Вы выиграли {win_coins_f} монет и получили {win_xp_f} XP!\n")
        return balance + win_coins, xp + win_xp

    elif slot1 == slot2 == slot3 == "💎":
        win_coins = int(money_player * 4 * (2 if balance_x2 else 1))
        win_xp = 80 if xp_x2 else 40

        win_coins_f = f"{win_coins:,}".replace(",", ".")
        win_xp_f = f"{win_xp:,}".replace(",", ".")

        print("💎 КРИСТАЛЛЫ! Отличная комбинация!")
        print(f"💰 Вы выиграли {win_coins_f} монет и получили {win_xp_f} XP!\n")
        return balance + win_coins, xp + win_xp

    elif slot1 == slot2 == slot3 == "🍒":
        win_coins = int(money_player * 2 * (2 if balance_x2 else 1))
        win_xp = 40 if xp_x2 else 20

        win_coins_f = f"{win_coins:,}".replace(",", ".")
        win_xp_f = f"{win_xp:,}".replace(",", ".")

        print("🍒 Обычный выигрыш! Три вишни в ряд!")
        print(f"💰 Вы выиграли {win_coins_f} монет и получили {win_xp_f} XP!\n")
        return balance + win_coins, xp + win_xp

    else:
        print("🔴 Увы, комбинация пустая. Вы потеряли свою ставку. Попробуйте еще раз!\n")
        return balance, xp

# Главная функция игры
def main():
    create_shop_if_not_exists()

    balance = 0
    balance_x2 = False
    promo_used = False
    lucky_amulet = False
    secret_used = False

    balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used = load_game()

    print("\n === Добро пожаловать в \"Мини Магазин\" === \n")

    while True:
        print("1. Каталог")
        print("2. Игры")
        print("3. Профиль")
        print("4. Промокод")
        print("5. Выход")

        try:
            user_digit = int(input("\nВведите цифру: "))

        except ValueError:
            print("\nОшибка 666! Введите число!\n")
            continue

        # Пасхалка
        if user_digit == 666:
            if not secret_used:
                balance += 100
                secret_used = True
                save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used)
            continue

        if user_digit == 1:
            try:
                with open(shop_file, "r", encoding="utf-8") as file:
                    print("\n===============\n")
                    print(file.read())
                    print("\n===============\n")

                user_buy = input("Хотите ли вы что-то купить? (Yes or No): ").lower().strip()

                if user_buy == "yes":
                    try:
                        user_id_buy = int(input("Выберите ID продукта для покупки: "))

                        if user_id_buy == 1:
                            if balance_x2:
                                print("\nВы уже купили этот товар!\n")

                            elif balance >= 100:
                                balance -= 100
                                balance_x2 = True
                                save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used)

                                print("\nУспешно! Списано 100 монет, теперь у вас x2 бонус к выигрышу!\n")

                            else:
                                print(f"\nНедостаточно монет! Нужно 100, а у вас {balance}.\n")

                        elif user_id_buy == 2:
                            if xp_x2:
                                print("\nВы уже купили этот товар!\n")

                            elif balance >= 200:
                                balance -= 200
                                xp_x2 = True
                                save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used)

                                print("\nУспешно! Списано 200 монет, теперь у вас x2 бонус к опыту!\n")

                            else:
                                print(f"\nНедостаточно монет! Нужно 200, а у вас {balance}.\n")

                        elif user_id_buy == 3:
                            if lucky_amulet:
                                print("\nВы уже купили этот товар!\n")

                            elif balance >= 300:
                                balance -= 300
                                lucky_amulet = True
                                save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used)

                                print("\nУспешно! Списано 300 монет, теперь у вас есть Счастливый Амулет (+1 жизнь)!\n")

                            else:
                                print(f"\nНедостаточно монет! Нужно 300, а у вас {balance}.\n")

                        else:
                            print("\nТовара с таким ID не существует!\n")

                    except ValueError:
                        print("\nОшибка! Введите корректный ID числом!\n")

            except FileNotFoundError:
                print("\n[Магазин временно пуст]\n")

        elif user_digit == 2:
            print("\n1. Угадать число")
            print("2. Камень, ножницы, бумага")
            print("3. Игровой автомат (Слоты) 🎰")

            try:
                user_number_game = int(input("\nВведите число игры: "))

                if user_number_game == 1:
                    balance, xp = game_guess_number(balance, balance_x2, xp, xp_x2, level, lucky_amulet)
                    xp, level = check_level_up(xp, level)

                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used)

                elif user_number_game == 2:
                    balance, xp = game_rock_scissors_paper(balance, balance_x2, xp, xp_x2, level, lucky_amulet)
                    xp, level = check_level_up(xp, level)

                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used)

                elif user_number_game == 3:
                    balance, xp = gaming_machine(balance, balance_x2, xp, xp_x2, level)
                    xp, level = check_level_up(xp, level)

                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used)

                else:
                    print("\nТакой игры нет.\n")

            except ValueError:
                print("\nОшибка! Введите число!\n")

        elif user_digit == 3:
            level_multiplier = 1.0 + (level - 1) * 0.1
            level_bonus_percent = int((level_multiplier - 1.0) * 100)

            xp_f = f"{xp:,}".replace(",", ".")
            next_xp_f = f"{level * 100:,}".replace(",", ".")
            balance_f = f"{balance:,}".replace(",", ".")

            print("\n===== ВАШ ПРОФИЛЬ =====\n")
            print(f"Уровень: {level} ⭐")
            print(f"Опыт: {xp_f} / {next_xp_f} XP 📈")
            print(f"Бонус уровня: +{level_bonus_percent}% к доходу ({level_multiplier:.1f}x) ✨")
            print(f"Баланс: {balance_f} монет 💰")

            status_x2 = "🟢 Активирован" if balance_x2 else "🔴 Не куплен"
            print(f"Бустер монет: {status_x2}")

            status_xp_x2 = "🟢 Активирован" if xp_x2 else "🔴 Не куплен"
            print(f"Бустер опыта: {status_xp_x2}")

            status_amulet = "🟢 Экипирован (+1 жизнь)" if lucky_amulet else "🔴 Не куплен"
            print(f"Счастливый амулет: {status_amulet}")

            status_promo = "🟢 Использован" if promo_used else "🔴 Доступен для ввода"
            print(f"Промокод: {status_promo}")
            print("\n=======================\n")

        elif user_digit == 4:
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

                    xp, level = check_level_up(xp, level)
                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used)

                    print(f"\nУспешно, промокод был активирован! (Множитель уровня: {level_multiplier:.1f}x)")
                    print(f"💰 На ваш баланс пришло {coins_given} Монет!")
                    print(f"📈 Вам ещё пришло {xp_given} Опыта!\n")
                else:
                    print("\nПромокод не верен!\n")
            else:
                print("\nПромокод уже был введён!\n")

        elif user_digit == 5:
            save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used)
            print("\nПрогресс сохранен! Прощайте, удачи вам! \n")
            break

        else:
            print(f"\nНеизвестный пункт меню: {user_digit} \n")

# Запуск игры
if __name__ == "__main__":
    main()
