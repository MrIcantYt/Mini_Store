import random
import time

class Colors:
    red = "\033[31m"
    green = "\033[32m"
    yellow = "\033[33m"
    blue_dark = "\033[34m"
    blue = "\033[36m"
    reset = "\033[0m"

def fmt(value):
    return f"{value:,}".replace(",", ".")

# Игра: Игровой Автомат
def gaming_machine(balance, balance_x2, xp, xp_x2, potion_luck):
    print(f"\n {Colors.yellow}== Игра: Игровой Автомат =={Colors.reset}\n")

    if not potion_luck:
        variants = ["🍒", "🍒", "🍒", "🍒", "💎", "💎", "💎", "👑", "👑"]

        slot1 = random.choice(variants)
        slot2 = random.choice(variants)
        slot3 = random.choice(variants)

    elif potion_luck:
        variants = ["🍒", "🍒", "🍒", "💎", "💎", "💎", "👑", "👑", "👑", "💰", "💰", "7"]

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
        print(f"\n{Colors.red}Ошибка! Введите корректное число или слово 'all'/'все'.{Colors.reset}\n")
        return balance, xp

    if money_player <= 0:
        print(f"\n{Colors.red}Ошибка! Ставка {fmt(money_player)} монет невозможна! Нельзя играть на 0 или меньше.{Colors.reset}\n")
        return balance, xp

    elif money_player > balance:
        print(f"\n{Colors.red}Ошибка! Нельзя вводить ставку больше своего баланса! {Colors.reset}\n")
        return balance, xp

    balance -= money_player
    is_vip = (money_player == 777 and balance >= 777)

    if is_vip:
        print(f"\n{Colors.yellow}⚡ ВНИМАНИЕ! Активирован VIP-режим ХАЙРОЛЛЕРА «777»!⚡{Colors.reset}")
        print(f"{Colors.red}Ставки максимальны. Риск удвоен. Выигрыш колоссален!{Colors.reset}")
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

    if slot1 == slot2 == slot3:
        combos = {
            "7": (20, 10, 200, 100, f"\n{Colors.green}⚡ МЕГА-ДЖЕКПОТ! ТРИ СЕМЕРКИ В РЯД! ⚡{Colors.reset}"),
            "👑": (15, 7, 120, 60, f"{Colors.green}🔥 ДЖЕКПОТ! У вас выпали три КОРОНЫ! 🔥 {Colors.reset}"),
            "💰": (10, 5, 90, 45, f"{Colors.green}💰 БОГАТСТВО! Три мешка золота обеспечили вам куш! {Colors.reset}"),
            "💎": (8, 4, 80, 40, f"{Colors.green}💎 КРИСТАЛЛЫ! Отличная комбинация! {Colors.reset}"),
            "🍒": (4, 2, 40, 20, f"{Colors.green}🍒 Обычный выигрыш! Три вишни в ряд! {Colors.reset}")
        }

        mult_vip, mult_norm, xp_vip, xp_norm, msg = combos[slot1]

        mult = mult_vip if is_vip else mult_norm
        win_xp = xp_vip if xp_x2 else xp_norm

        win_coins = int(money_player * mult * (2 if balance_x2 else 1))

        print(msg)
        print(f"💰 Вы выиграли {Colors.yellow}{fmt(win_coins)}{Colors.reset} монет и получили {Colors.yellow}{fmt(win_xp)}{Colors.reset} XP!\n")

        return balance + win_coins, xp + win_xp

    else:
        if is_vip:
            print(f"{Colors.red}💥 КРАХ ХАЙРОЛЛЕРА! Слот заблокирован. С вашего баланса списан ДВОЙНОЙ штраф за риск!{Colors.reset}\n")
            balance -= money_player
        
        else:
            print("🔴 Увы, комбинация пустая. Вы потеряли свою ставку. Попробуйте еще раз!\n")

        return balance, xp
