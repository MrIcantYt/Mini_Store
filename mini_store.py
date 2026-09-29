import random
import os
import json
import time

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
save_file = "save.json"

# Цвета
red = "\033[31m" # Красный
green = "\033[32m" # Зелёный
yellow = "\033[33m" # Жёлтый
blue_dark = "\033[34m" # Синий
blue = "\033[36m" # Голубой
reset = "\033[0m" # Сбрасывает цвет

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
                data.get("secret_used", False),
                data.get("bought", 0),
                data.get("mining_lvl", 0),
                data.get("potion_luck", False),
                data.get("lucky_ticket", False),
                data.get("mining_boost", False),
                data.get("buy_num_boost", 0),
                data.get("business", False)
            )

    return 0, False, False, 0, 1, False, False, False, 0, 0, False, False, False, 0, False

# Сохранение игры
def save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business):
    data = {
        "balance": balance,
        "balance_x2": balance_x2,
        "promo_used": promo_used,
        "xp": xp,
        "level": level,
        "xp_x2": xp_x2,
        "lucky_amulet": lucky_amulet,
        "secret_used": secret_used,
        "bought": bought,
        "mining_lvl": mining_lvl,
        "potion_luck": potion_luck,
        "lucky_ticket": lucky_ticket,
        "mining_boost": mining_boost,
        "buy_num_boost": buy_num_boost,
        "business": business
    }

    with open(save_file, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Создание магазина, если его нету
def create_shop_if_not_exists():
    if not os.path.exists(shop_file):
        with open(shop_file, "w", encoding="utf-8") as file:
            file.write(default_shop_content)

# Проверка опыта чтобы обновить лвл
def check_level_up(xp, level, green, reset):
    xp_needed = level * 100

    if xp >= xp_needed:
        xp -= xp_needed
        level += 1

        print(f"{green}🎉 ПОЗДРАВЛЯЕМ! Вы достигли {level} уровня! 🎉 {reset}\n")

    return xp, level

# Игра: Угадай число
def game_guess_number(balance, balance_x2, xp, xp_x2, level, lucky_amulet, green, reset, red, lucky_ticket, potion_luck):
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
                    print(f"\n{red}Ошибка! Введите целое число. {reset}\n")
                    continue

                life -= 1

                if lucky_ticket:
                    lucky_ticket = False
                    life += 1
                    print(f"\n🎫 {yellow}Счастливый тикет сработал и спас вашу жизнь!{reset}")

                if user_number == number:
                    luck = random.randint(1, 100)

                    if potion_luck:
                        if luck <= 35:
                            base_reward = 50

                            level_multiplier = 1.0 + (level - 1) * 0.1

                            reward_coins = int(base_reward * level_multiplier * (2 if balance_x2 else 1))
                            reward_xp = 80 if xp_x2 else 40

                            print("\n💥 КРИТИЧЕСКИЙ УДАР! Вы разнесли систему в пух и прах! Награда умножена!")
                            print(f"\n🎉 {green}Поздравляю! Вы победили! {reset}")
                            print(f"💰 Вы получили {yellow}{reward_coins}{reset} монет (Множитель уровня: {yellow}{level_multiplier:.1f}x{reset})!")
                            print(f"📈 Вам начислено {yellow}{reward_xp}{reset} XP!\n")

                            return balance + reward_coins, xp + reward_xp

                        else:
                            base_reward = 25

                            level_multiplier = 1.0 + (level - 1) * 0.1

                            reward_coins = int(base_reward * level_multiplier * (2 if balance_x2 else 1))
                            reward_xp = 40 if xp_x2 else 20

                            print(f"\n🎉 {green}Поздравляю! Вы победили! {reset}")
                            print(f"💰 Вы получили {yellow}{reward_coins}{reset} монет (Множитель уровня: {yellow}{level_multiplier:.1f}x{reset})!")
                            print(f"📈 Вам начислено {yellow}{reward_xp}{reset} XP!\n")

                            return balance + reward_coins, xp + reward_xp

                    else:
                        if luck <= 15:
                            base_reward = 50

                            level_multiplier = 1.0 + (level - 1) * 0.1

                            reward_coins = int(base_reward * level_multiplier * (2 if balance_x2 else 1))
                            reward_xp = 80 if xp_x2 else 40

                            print("\n💥 КРИТИЧЕСКИЙ УДАР! Вы разнесли систему в пух и прах! Награда умножена!")
                            print(f"\n🎉 {green}Поздравляю! Вы победили! {reset}")
                            print(f"💰 Вы получили {yellow}{reward_coins}{reset} монет (Множитель уровня: {yellow}{level_multiplier:.1f}x{reset})!")
                            print(f"📈 Вам начислено {yellow}{reward_xp}{reset} XP!\n")

                            return balance + reward_coins, xp + reward_xp

                        else:
                            base_reward = 25

                            level_multiplier = 1.0 + (level - 1) * 0.1

                            reward_coins = int(base_reward * level_multiplier * (2 if balance_x2 else 1))
                            reward_xp = 40 if xp_x2 else 20

                            print(f"\n🎉 {green}Поздравляю! Вы победили! {reset}")
                            print(f"💰 Вы получили {yellow}{reward_coins}{reset} монет (Множитель уровня: {yellow}{level_multiplier:.1f}x{reset})!")
                            print(f"📈 Вам начислено {yellow}{reward_xp}{reset} XP!\n")

                            return balance + reward_coins, xp + reward_xp

                elif life == 0:
                    print(f"\n{red}Вы програли! Загаданное число было: {number}. {reset}\n")

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
                    print(f"{red}Ошибка! Введите целое число. {reset}")
                    continue

                life -= 1

                if lucky_ticket:
                    lucky_ticket = False
                    life += 1
                    print(f"\n🎫 {yellow}Счастливый тикет сработал и спас вашу жизнь!{reset}")

                if user_number == number:
                    luck = random.randint(1, 100)

                    if potion_luck:
                        if luck <= 35:
                            base_reward = 100

                            level_multiplier = 1.0 + (level - 1) * 0.1

                            reward_coins = int(base_reward * level_multiplier * (2 if balance_x2 else 1))
                            reward_xp = 160 if xp_x2 else 80

                            print("\n💥 КРИТИЧЕСКИЙ УДАР! Вы разнесли систему в пух и прах! Награда умножена!")
                            print(f"\n🎉 {green}Поздравляю! Вы победили! {reset}")
                            print(f"💰 Вы получили {yellow}{reward_coins}{reset} монет (Множитель уровня: {yellow}{level_multiplier:.1f}x{reset})!")
                            print(f"📈 Вам начислено {yellow}{reward_xp}{reset} XP!\n")

                            return balance + reward_coins, xp + reward_xp

                        else:
                            base_reward = 50

                            level_multiplier = 1.0 + (level - 1) * 0.1

                            reward_coins = int(base_reward * level_multiplier * (2 if balance_x2 else 1))
                            reward_xp = 80 if xp_x2 else 40

                            print(f"\n🎉 {green}Поздравляю! Вы победили! {reset}")
                            print(f"💰 Вы получили {yellow}{reward_coins}{reset} монет (Множитель уровня: {yellow}{level_multiplier:.1f}x{reset})!")
                            print(f"📈 Вам начислено {yellow}{reward_xp}{reset} XP!\n")

                            return balance + reward_coins, xp + reward_xp

                    else:
                        if luck <= 15:
                            base_reward = 100

                            level_multiplier = 1.0 + (level - 1) * 0.1

                            reward_coins = int(base_reward * level_multiplier * (2 if balance_x2 else 1))
                            reward_xp = 160 if xp_x2 else 80

                            print("\n💥 КРИТИЧЕСКИЙ УДАР! Вы разнесли систему в пух и прах! Награда умножена!")
                            print(f"\n🎉 {green}Поздравляю! Вы победили! {reset}")
                            print(f"💰 Вы получили {yellow}{reward_coins}{reset} монет (Множитель уровня: {yellow}{level_multiplier:.1f}x{reset})!")
                            print(f"📈 Вам начислено {yellow}{reward_xp}{reset} XP!\n")

                            return balance + reward_coins, xp + reward_xp

                        else:
                            base_reward = 50

                            level_multiplier = 1.0 + (level - 1) * 0.1

                            reward_coins = int(base_reward * level_multiplier * (2 if balance_x2 else 1))
                            reward_xp = 80 if xp_x2 else 40

                            print(f"\n🎉 {green}Поздравляю! Вы победили! {reset}")
                            print(f"💰 Вы получили {yellow}{reward_coins}{reset} монет (Множитель уровня: {yellow}{level_multiplier:.1f}x{reset})!")
                            print(f"📈 Вам начислено {yellow}{reward_xp}{reset} XP!\n")

                            return balance + reward_coins, xp + reward_xp

                elif life == 0:
                    print(f"\n{red}Вы програли! Загаданное число было: {number}. {reset}\n")

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
                    print(f"{red}Ошибка! Введите целое число.{reset}")
                    continue

                life -= 1

                if lucky_ticket:
                    lucky_ticket = False
                    life += 1
                    print(f"\n🎫 {yellow}Счастливый тикет сработал и спас вашу жизнь!{reset}")

                if user_number == number:
                    luck = random.randint(1, 100)

                    if potion_luck:
                        if luck <= 35:
                            base_reward = 150

                            level_multiplier = 1.0 + (level - 1) * 0.1

                            reward_coins = int(base_reward * level_multiplier * (2 if balance_x2 else 1))
                            reward_xp = 240 if xp_x2 else 120

                            print("\n💥 КРИТИЧЕСКИЙ УДАР! Вы разнесли систему в пух и прах! Награда умножена!")
                            print(f"\n🎉 {green}Поздравляю! Вы победили! {reset}")
                            print(f"💰 Вы получили {yellow}{reward_coins}{reset} монет (Множитель уровня: {yellow}{level_multiplier:.1f}x{reset})!")
                            print(f"📈 Вам начислено {yellow}{reward_xp}{reset} XP!\n")

                            return balance + reward_coins, xp + reward_xp

                        else:
                            base_reward = 75

                            level_multiplier = 1.0 + (level - 1) * 0.1

                            reward_coins = int(base_reward * level_multiplier * (2 if balance_x2 else 1))
                            reward_xp = 120 if xp_x2 else 60

                            print(f"\n🎉 {green}Поздравляю! Вы победили! {reset}")
                            print(f"💰 Вы получили {yellow}{reward_coins}{reset} монет (Множитель уровня: {yellow}{level_multiplier:.1f}x{reset})!")
                            print(f"📈 Вам начислено {yellow}{reward_xp}{reset} XP!\n")

                            return balance + reward_coins, xp + reward_xp

                    else:
                        if luck <= 15:
                            base_reward = 150

                            level_multiplier = 1.0 + (level - 1) * 0.1

                            reward_coins = int(base_reward * level_multiplier * (2 if balance_x2 else 1))
                            reward_xp = 240 if xp_x2 else 120

                            print("\n💥 КРИТИЧЕСКИЙ УДАР! Вы разнесли систему в пух и прах! Награда умножена!")
                            print(f"\n🎉 {green}Поздравляю! Вы победили! {reset}")
                            print(f"💰 Вы получили {yellow}{reward_coins}{reset} монет (Множитель уровня: {yellow}{level_multiplier:.1f}x{reset})!")
                            print(f"📈 Вам начислено {yellow}{reward_xp}{reset} XP!\n")

                            return balance + reward_coins, xp + reward_xp

                        else:
                            base_reward = 75

                            level_multiplier = 1.0 + (level - 1) * 0.1

                            reward_coins = int(base_reward * level_multiplier * (2 if balance_x2 else 1))
                            reward_xp = 120 if xp_x2 else 60

                            print(f"\n🎉 {green}Поздравляю! Вы победили! {reset}")
                            print(f"💰 Вы получили {yellow}{reward_coins}{reset} монет (Множитель уровня: {yellow}{level_multiplier:.1f}x{reset})!")
                            print(f"📈 Вам начислено {yellow}{reward_xp}{reset} XP!\n")

                            return balance + reward_coins, xp + reward_xp

                elif life == 0:
                    print(f"\n{red}Вы програли! Загаданное число было: {number}. {reset}\n")

                elif user_number > number:
                    print(f"\nЗагаданное число меньше! Осталось жизней: {life}\n")

                elif user_number < number:
                    print(f"\nЗагаданное число больше! Осталось жизней: {life}\n")

            return balance, xp

        else:
            print(f"\n{red}Ошибка! Введите цифру от 1 до 3. {reset}\n")

            return balance, xp

    except (ValueError, TypeError):
        print(f"\n{red}Ошибка! Введите корректное число. {reset}\n")

        return balance, xp

# Игра: Камень, ножницы, бумага
def game_rock_scissors_paper(balance, balance_x2, xp, xp_x2, level, lucky_amulet, green, yellow, reset, red, lucky_ticket, potion_luck):
    print("\n == Игра: Камень, ножницы, бумага ==\n")

    variants = ["камень", "ножницы", "бумага"]

    if lucky_amulet:
        life = 4
    else:
        life = 3

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

            if potion_luck:
                if luck <= 35:
                    base_reward = 50

                    level_multiplier = 1.0 + (level - 1) * 0.1

                    reward_coins = int(base_reward * level_multiplier * (2 if balance_x2 else 1))
                    reward_xp = 80 if xp_x2 else 40

                    print("💥 КРИТИЧЕСКИЙ УДАР! Вы разнесли систему в пух и прах! Награда умножена!")
                    print(f"\n🎉 {green}Поздравляю! Вы победили! {reset}")
                    print(f"💰 Вы получили {yellow}{reward_coins}{reset} монет (Множитель уровня: {yellow}{level_multiplier:.1f}x{reset})!")
                    print(f"📈 Вам начислено {yellow}{reward_xp}{reset} XP!\n")

                    return balance + reward_coins, xp + reward_xp

                else:
                    base_reward = 50

                    level_multiplier = 1.0 + (level - 1) * 0.1

                    reward_coins = int(base_reward * level_multiplier * (2 if balance_x2 else 1))
                    reward_xp = 80 if xp_x2 else 40

                    print(f"🎉 {green}Поздравляю! Вы победили! {reset}")
                    print(f"💰 Вы получили {yellow}{reward_coins}{reset} монет (Множитель уровня: {yellow}{level_multiplier:.1f}x{reset})!")
                    print(f"📈 Вам начислено {yellow}{reward_xp}{reset} XP!\n")

                    return balance + reward_coins, xp + reward_xp

            else:
                if luck <= 15:
                    base_reward = 50

                    level_multiplier = 1.0 + (level - 1) * 0.1

                    reward_coins = int(base_reward * level_multiplier * (2 if balance_x2 else 1))
                    reward_xp = 80 if xp_x2 else 40

                    print("💥 КРИТИЧЕСКИЙ УДАР! Вы разнесли систему в пух и прах! Награда умножена!")
                    print(f"\n🎉 {green}Поздравляю! Вы победили! {reset}")
                    print(f"💰 Вы получили {yellow}{reward_coins}{reset} монет (Множитель уровня: {yellow}{level_multiplier:.1f}x{reset})!")
                    print(f"📈 Вам начислено {yellow}{reward_xp}{reset} XP!\n")

                    return balance + reward_coins, xp + reward_xp

                else:
                    base_reward = 25

                    level_multiplier = 1.0 + (level - 1) * 0.1

                    reward_coins = int(base_reward * level_multiplier * (2 if balance_x2 else 1))
                    reward_xp = 40 if xp_x2 else 20

                    print(f"🎉 {green}Поздравляю! Вы победили! {reset}")
                    print(f"💰 Вы получили {yellow}{reward_coins}{reset} монет (Множитель уровня: {yellow}{level_multiplier:.1f}x{reset})!")
                    print(f"📈 Вам начислено {yellow}{reward_xp}{reset} XP!\n")

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
    print("\n == Игра: Игровой Автомат ==\n")

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

    balance_format = f"{balance:,}".replace(",", ".")
    
    money_player = int(input(f"Введите вашу ставку (Ваш баланс: {balance_format}): "))

    money_format = f"{money_player:,}".replace(",", ".")

    if money_player <= 0:
        print(f"\n{red}Ошибка! Ставка {money_format} монет невозможна! Нельзя играть на 0 или меньше.{reset}\n")
        return balance, xp

    elif money_player > balance:
        print(f"\n{red}Ошибка! Нельзя вводить ставку больше своего баланса! {reset}\n")
        return balance, xp
    
    balance -= money_player

    if money_player == 777 and balance >= 1554:
        print(f"\n{yellow}⚡ ВНИМАНИЕ! Активирован VIP-режим ХАЙРОЛЛЕРА «777»!⚡{reset}")
        print(f"{red}Ставки максимальны. Риск удвоен. Выигрыш колоссален!{reset}")

    if money_player == 777 and balance >= 1554:
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
        if money_player == 777 and balance >= 1554:
            win_coins = int(money_player * 15 * (2 if balance_x2 else 1))
            win_xp = 120 if xp_x2 else 60

            win_coins_f = f"{win_coins:,}".replace(",", ".")
            win_xp_f = f"{win_xp:,}".replace(",", ".")

            print(f"\n{green}🔥 ЛЕГЕНДАРНЫЙ VIP-ДЖЕКПОТ! 15x МНОЖИТЕЛЬ СРАБОТАЛ! 🔥{reset}")
            print(f"💰 Вы выиграли {yellow}{win_coins_f}{reset} монет и получили {yellow}{win_xp_f}{reset} XP!\n")
            
            return balance + win_coins, xp + win_xp
        
        else:
            win_coins = int(money_player * 7 * (2 if balance_x2 else 1))
            win_xp = 120 if xp_x2 else 60

            win_coins_f = f"{win_coins:,}".replace(",", ".")
            win_xp_f = f"{win_xp:,}".replace(",", ".")

            print(f"{green}🔥 ДЖЕКПОТ! У вас выпали три КОРОНЫ! 🔥 {reset}")
            print(f"💰 Вы выиграли {yellow}{win_coins_f}{reset} монет и получили {yellow}{win_xp_f}{reset} XP!\n")
            
            return balance + win_coins, xp + win_xp

    elif slot1 == slot2 == slot3 == "💎":
        if money_player == 777 and balance >= 1554:
            win_coins = int(money_player * 8 * (2 if balance_x2 else 1))
            win_xp = 80 if xp_x2 else 40

            win_coins_f = f"{win_coins:,}".replace(",", ".")
            win_xp_f = f"{win_xp:,}".replace(",", ".")

            print(f"{green}💎 VIP-КРИСТАЛЛЫ! Отличная комбинация хайроллера! {reset}")
            print(f"💰 Вы выиграли {yellow}{win_coins_f}{reset} монет и получили {yellow}{win_xp_f}{reset} XP!\n")

            return balance + win_coins, xp + win_xp

        else:
            win_coins = int(money_player * 4 * (2 if balance_x2 else 1))
            win_xp = 80 if xp_x2 else 40

            win_coins_f = f"{win_coins:,}".replace(",", ".")
            win_xp_f = f"{win_xp:,}".replace(",", ".")

            print(f"{green}💎 КРИСТАЛЛЫ! Отличная комбинация! {reset}")
            print(f"💰 Вы выиграли {yellow}{win_coins_f}{reset} монет и получили {yellow}{win_xp_f}{reset} XP!\n")

            return balance + win_coins, xp + win_xp

    elif slot1 == slot2 == slot3 == "🍒":
        if money_player == 777 and balance >= 1554:
            win_coins = int(money_player * 4 * (2 if balance_x2 else 1))
            win_xp = 40 if xp_x2 else 20

            win_coins_f = f"{win_coins:,}".replace(",", ".")
            win_xp_f = f"{win_xp:,}".replace(",", ".")

            print(f"{green}🍒 VIP-Выигрыш на вишнях! Награда увеличена до 4х! {reset}")
            print(f"💰 Вы выиграли {yellow}{win_coins_f}{reset} монет и получили {yellow}{win_xp_f}{reset} XP!\n")
            
            return balance + win_coins, xp + win_xp

        else:
            win_coins = int(money_player * 2 * (2 if balance_x2 else 1))
            win_xp = 40 if xp_x2 else 20

            win_coins_f = f"{win_coins:,}".replace(",", ".")
            win_xp_f = f"{win_xp:,}".replace(",", ".")

            print(f"{green}🍒 Обычный выигрыш! Три вишни в ряд! {reset}")
            print(f"💰 Вы выиграли {yellow}{win_coins_f}{reset} монет и получили {yellow}{win_xp_f}{reset} XP!\n")
            
            return balance + win_coins, xp + win_xp

    else:
        if money_player == 777 and balance >= 1554:
            print(f"{red}💥 КРАХ ХАЙРОЛЛЕРА! Слот заблокирован. С вашего баланса списан ДВОЙНОЙ штраф за риск!{reset}\n")

            balance -= money_player
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
    bought = 0
    mining_lvl = 0
    potion_luck = False
    lucky_ticket = False
    mining_boost = False
    buy_num_boost = 0
    business = False

    balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business = load_game()

    print("\n === Добро пожаловать в \"Мини Магазин\" === \n")

    while True:
        print("1. Каталог")
        print("2. Игры")
        print("3. Профиль")
        print("4. Промокод")
        print("5. Майнинг ферма")
        print("6. Выход")

        try:
            user_digit = int(input("\nВведите цифру: "))

        except ValueError:
            print(f"\n{red}Ошибка 666! Введите число!{reset}\n")
            continue

        # Пасхалка
        if user_digit == 666:
            if not secret_used:
                balance += 100
                secret_used = True

                save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

                print()

            continue

        if business:
            print(f"\nНезнакомец: {blue_dark}Твой стартап расширяется! Инвесторы в восторге. Баланс увеличился на {yellow}+25 монет{blue_dark}!{reset}")

            balance += 25

            save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

            pass

        # Магазин
        if user_digit == 1:
            try:
                with open(shop_file, "r", encoding="utf-8") as file:
                    print("\n===============\n")
                    print(file.read())
                    print("\n===============\n")

                user_buy = input("Хотите ли вы что-то купить или вернуть? (Yes or No): ").lower().strip()

                if "yes" in user_buy:
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

                                        save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

                                        print(f"\n{green}Успешно! Списано 100 монет, теперь у вас x2 бонус к выигрышу!{reset}\n")

                                    else:
                                        print(f"\n{red}Недостаточно монет! Нужно 100, а у вас {balance}.{reset}\n")

                                elif user_id_buy == 2:
                                    if xp_x2:
                                        print(f"\n{yellow}Вы уже купили этот товар!{reset}\n")

                                        bought += 1

                                        save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

                                        if bought == 3:
                                            print("Незнакомец: Вам не надоело тыкать на купленный товар?\n")

                                            save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

                                        elif bought == 5:
                                            print("Незнакомец: Всё, хорошо, держите 100 монет. Если ещё раз тыкнете, то с вас спишется 100 монет!\n")

                                            balance += 100

                                            save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

                                        elif bought == 6:
                                            print("Незнакомец: Я вас предупреждал!\n")

                                            balance -= 100

                                            save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

                                    elif balance >= 200:
                                        balance -= 200
                                        xp_x2 = True

                                        save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

                                        print(f"\n{green}Успешно! Списано 200 монет, теперь у вас x2 бонус к опыту!{reset}\n")

                                    else:
                                        print(f"\n{red}Недостаточно монет! Нужно 200, а у вас {balance}.{reset}\n")

                                elif user_id_buy == 3:
                                    if lucky_amulet:
                                        print(f"\n{yellow}Вы уже купили этот товар!{reset}\n")

                                    elif balance >= 300:
                                        balance -= 300
                                        lucky_amulet = True

                                        save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

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

                                            save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

                                            print(f"\n{green}Успешно! Списано {result_mining_lvl_mon} монет, теперь у вас есть Майнинг ферма (лвл: {mining_lvl})!{reset}\n")

                                        else:
                                            print(f"\n{red}Недостаточно монет! Нужно {result_mining_lvl_mon}, а у вас {balance}.{reset}\n")

                                elif user_id_buy == 5:
                                    if potion_luck:
                                        print(f"\n{yellow}Вы уже купили этот товар!{reset}\n")

                                    elif balance >= 500:
                                        balance -= 500
                                        potion_luck = True

                                        save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

                                        print(f"\n{green}Успешно! Списано 500 монет, теперь у вас есть Счастливое Зелье (Больше шансов в Казино)!{reset}\n")

                                    else:
                                        print(f"\n{red}Недостаточно монет! Нужно 500, а у вас {balance}.{reset}\n")

                                elif user_id_buy == 6:
                                    if lucky_ticket:
                                        print(f"\n{yellow}Вы уже купили этот товар!{reset}\n")

                                    elif balance >= 400:
                                        balance -= 400
                                        lucky_ticket = True

                                        save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

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

                                        buy_num_boost += 1

                                        if buy_num_boost == 2:
                                            print(f"\nНезнакомец: {blue_dark}Отличный выбор. Твоя Майнинг-ферма скажет тебе спасибо. Работа пойдет в два раза быстрее!{reset}\n")
                                            balance -= 700
                                            mining_boost = True

                                            save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

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

                                        save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

                                        print(f"\n{green}Успешно! Списано 1200 монет, теперь у вас есть Пассивный бизнес (За каждый ход в меню +25 монет на баланс)!{reset}\n")

                                    else:
                                        print(f"\n{red}Недостаточно монет! Нужно 1200, а у вас {balance}.{reset}\n")

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

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

                                else:
                                    print(f"\n{red}У вас не куплено \"x2 бонус к монетам\"!{reset}\n")

                            elif user_id_return == 2:
                                if xp_x2:
                                    print(f"\n{green}Успешно! Вы вернули \"x2 бонус к опыту\"! К вашему балансу было прибавлено 100 монет!{reset}\n")

                                    xp_x2 = False
                                    balance += 100

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

                                else:
                                    print(f"\n{red}У вас не куплено \"x2 бонус к опыту\"!{reset}\n")

                            elif user_id_return == 3:
                                if lucky_amulet:
                                    print(f"\n{green}Успешно! Вы вернули \"Счастливый Амулет\"! К вашему балансу было прибавлено 150 монет!{reset}\n")

                                    lucky_amulet = False
                                    balance += 150

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

                                else:
                                    print(f"\n{red}У вас не куплен \"Счастливый Амулет\"!{reset}\n")

                            elif user_id_return == 4:
                                if mining_lvl >= 1:
                                    print(f"\n{red}Этот товар нельзя вернуть (Будет доступно в версии BETA-0.5)!{reset}\n")

                                else:
                                    print(f"\n{red}У вас не куплено \"Майнинг-ферма\"!{reset}\n")

                            elif user_id_return == 5:
                                if potion_luck:
                                    print(f"\n{green}Успешно! Вы вернули \"Зелье Удачи\"! К вашему балансу было прибавлено 250 монет!{reset}\n")

                                    potion_luck = False
                                    balance += 250

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

                                else:
                                    print(f"\n{red}У вас не куплено \"Зелье Удачи\"!{reset}\n")

                            elif user_id_return == 6:
                                if lucky_ticket:
                                    print(f"\n{green}Успешно! Вы вернули \"Cчастливый Тикет\"! К вашему балансу было прибавлено 200 монет!{reset}\n")

                                    lucky_ticket = False
                                    balance += 200

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

                                else:
                                    print(f"\n{red}У вас не куплено \"Счастливый Тикет\"!{reset}\n")

                            elif user_id_return == 7:
                                if mining_boost:
                                    print(f"\n{green}Успешно! Вы вернули \"Кофе\"! К вашему балансу было прибавлено 350 монет!{reset}\n")

                                    mining_boost = False
                                    balance += 350

                                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

                                else:
                                    print(f"\n{red}У вас не куплено \"Кофе\"!{reset}\n")

                            elif user_id_return == 8:
                                if business:
                                    print(f"\n{red}Этот товар нельзя вернуть (Будет доступно в версии BETA-0.5)!{reset}\n")

                                else:
                                    print(f"\n{red}У вас не куплен \"Пассивный Бизнес\"!{reset}\n")

                            else:
                                print(f"\n{red}Товара с таким ID не существует в системе возврата!{reset}\n")

                    except (ValueError, TypeError):
                        print(f"\n{red}Ошибка! Введите корректное число. {reset}\n")

                else:
                    print("\nХорошо.\n")

            except FileNotFoundError:
                print("\n[Магазин временно пуст]\n")
        
        # Игры
        elif user_digit == 2:
            print("\n1. Угадать число")
            print("2. Камень, ножницы, бумага")
            print("3. Игровой автомат (Слоты) 🎰")

            try:
                user_number_game = int(input("\nВведите число игры: "))

                if user_number_game == 1:
                    balance, xp = game_guess_number(balance, balance_x2, xp, xp_x2, level, lucky_amulet, green, reset, red, lucky_ticket, potion_luck)
                    xp, level = check_level_up(xp, level, green, reset)

                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

                elif user_number_game == 2:
                    balance, xp = game_rock_scissors_paper(balance, balance_x2, xp, xp_x2, level, lucky_amulet, green, yellow, reset, red, lucky_ticket, potion_luck)
                    xp, level = check_level_up(xp, level, green, reset)

                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

                elif user_number_game == 3:
                    balance, xp = gaming_machine(balance, balance_x2, xp, xp_x2, green, yellow, reset, red, potion_luck)
                    xp, level = check_level_up(xp, level, green, reset)

                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

                else:
                    print(f"\n{red}Такой игры нет.{reset}\n")

            except ValueError:
                print(f"\n{red}Ошибка! Введите число!{reset}\n")
        
        # Профиль
        elif user_digit == 3:

            level_multiplier = 1.0 + (level - 1) * 0.1
            level_bonus_percent = int((level_multiplier - 1.0) * 100)

            xp_f = f"{xp:,}".replace(",", ".")
            next_xp_f = f"{level * 100:,}".replace(",", ".")
            balance_f = f"{balance:,}".replace(",", ".")

            print("\n===== ВАШ ПРОФИЛЬ =====\n")
            print(f"Уровень: {yellow}{level}{reset} ⭐")
            print(f"Опыт: {yellow}{xp_f}{reset} / {yellow}{next_xp_f} XP {reset}📈")
            print(f"Бонус уровня: {yellow}+{level_bonus_percent}%{reset} к доходу ({yellow}{level_multiplier:.1f}x{reset}) ✨")
            print(f"Баланс: {yellow}{balance_f} монет {reset}💰")

            status_x2 = f"{green}🟢 Активирован {reset}" if balance_x2 else f"{red}🔴 Не куплен {reset}"
            print(f"Бустер монет: {status_x2}")

            status_xp_x2 = f"{green}🟢 Активирован {reset}" if xp_x2 else f"{red}🔴 Не куплен {reset}"
            print(f"Бустер опыта: {status_xp_x2}")

            status_amulet = f"{green}🟢 Экипирован (+1 жизнь) {reset}" if lucky_amulet else f"{red}🔴 Не куплен {reset}"
            print(f"Счастливый амулет: {status_amulet}")

            status_promo = f"{green}🟢 Использован {reset}" if promo_used else f"{red}🔴 Доступен для ввода {reset}"
            print(f"Промокод: {status_promo}")

            status_point = f"{green}🟢 Активирован {reset}" if potion_luck else f"{red}🔴 Не куплен {reset}"
            print(f"Зелье Удачи: {status_point}")

            status_lucky = f"{green}🟢 Активирован {reset}" if lucky_ticket else f"{red}🔴 Не куплен {reset}"
            print(f"Счастливый тикет: {status_lucky}")

            status_coffee = f"{green}🟢 Активирован (2x скорость) {reset}" if mining_boost else f"{red}🔴 Не куплен {reset}"
            print(f"Кофе (Разгон фермы): {status_coffee}")
            print(f"Уровень фермы: {yellow}{mining_lvl}{reset} LVL ⛏️")
            print("\n=======================\n")
        
        # Промокод
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

                    print(f"\n🎉 {green}Успешно, промокод был активирован!{reset} ")
                    print(f"💰 Вы получили {yellow}{coins_given}{reset} монет (Множитель уровня: {yellow}{level_multiplier:.1f}x{reset})!")
                    print(f"📈 Вам начислено {yellow}{xp_given}{reset} XP!\n")

                    xp, level = check_level_up(xp, level, green, reset)

                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

                else:
                    print(f"\n{red}Промокод не верен! {reset}\n")

            else:
                print(f"\n{yellow}Промокод уже был введён!{reset}\n")
        
        # Майнинг-ферма
        elif user_digit == 5:
            import msvcrt

            if mining_lvl > 0:
                print(f"\n⛏️ {green}Майнинг-ферма запущена! ⛏️{reset}")
                print("Монеты капают каждую секунду. [Нажмите Q для выхода]\n")

                while True:
                    balance += 5 * mining_lvl
                    balance_f = f"{balance:,}".replace(",", ".")

                    print(f"Добыча... Ваш баланс: {yellow}{balance_f}{reset} монет 💰")

                    sleep_time = 0.5 if mining_boost else 1.0

                    time.sleep(sleep_time)

                    save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode("utf-8", errors="ignore").lower()

                        if key == "q":
                            print(f"\n{green}Майнинг приостановлен. Возврат в меню...{reset}\n")

                            break

            else:
                print(f"\n{red}Сначала купите Майнинг-ферму в каталоге!{reset}\n")

        # Выход
        elif user_digit == 6:
            save_game(balance, balance_x2, promo_used, xp, level, xp_x2, lucky_amulet, secret_used, bought, mining_lvl, potion_luck, lucky_ticket, mining_boost, buy_num_boost, business)

            print("\nПрогресс сохранен! Прощайте, удачи вам! \n")

            break

        else:
            print(f"\n{red}Неизвестный пункт меню: {user_digit}{reset} \n")

# Запуск игры
if __name__ == "__main__":
    main()
