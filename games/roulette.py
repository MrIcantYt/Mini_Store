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

# Игра: Рулетка Казино
def play_roulette(balance, balance_x2, xp, xp_x2, level, potion_luck):
    print(f"\n {Colors.yellow}== Игра: Рулетка Казино =={Colors.reset}\n")

    user_input = input(f"Введите вашу ставку или 'all'/'все' (Ваш баланс: {fmt(balance)}): ").strip().lower()

    if user_input == "all" or user_input == "все":
        money_player = balance
    
    else:
        if not user_input.isdigit():
            print(f"\n{Colors.red}Ошибка! Введите корректное число или слово 'all'/'все'.{Colors.reset}\n")
            return balance, xp
    
        money_player = int(user_input)

    if money_player <= 0:
        print(f"\n{Colors.red}Ошибка! Ставка {fmt(money_player)} монет невозможна! Нельзя играть на 0 или меньше.{Colors.reset}\n")
        return balance, xp
    
    elif money_player > balance:
        print(f"\n{Colors.red}Ошибка! Нельзя вводить ставку больше своего баланса!{Colors.reset}\n")
        return balance, xp

    print(f"\nВарианты ставок:\n1. На {Colors.red}Красное{Colors.reset} (Выигрыш x2)\n2. На Чёрное (Выигрыш x2)\n3. На {Colors.green}Зеро (0){Colors.reset} (Выигрыш x35!)")
    
    choice_input = input("\nВыберите тип ставки (1, 2 или 3): ").strip()

    match choice_input:
        case "1":
            player_choice = "красное"
    
        case "2":
            player_choice = "черное"
        
        case "3":
            player_choice = "зеро"
    
        case _:
            print(f"\n{Colors.red}Ошибка! Выбран несуществующий тип ставки. Возврат в меню.{Colors.reset}\n")
            return balance, xp

    balance -= money_player

    print(f"\n| 🎰 СТАВКА ПРИНЯТА. КОЛЕСО РУЛЕТКИ ЗАПУЩЕНО... |")
    time.sleep(0.5)
    print(" [ . ]", end="", flush=True)
    time.sleep(0.5)
    print(" [ .. ]", end="", flush=True)
    time.sleep(0.5)
    print(" [ ... ]\n")
    time.sleep(0.5)

    wheel_result = random.randint(0, 36)

    if potion_luck and player_choice in ["красное", "черное"]:
        if random.randint(1, 100) <= 35:
            winning_color = player_choice
            wheel_result = 2 if winning_color == "красное" else 1
        
        else:
            if wheel_result == 0: 
                winning_color = "зеро"
            
            else: 
                winning_color = "красное" if wheel_result % 2 == 0 else "черное"
    
    else:
        if wheel_result == 0:
            winning_color = "зеро"
    
        else:
            winning_color = "красное" if wheel_result % 2 == 0 else "черное"

    if winning_color == "зеро":
        print(f"Выпало: {Colors.green}[ {wheel_result} ЗЕРО ]{Colors.reset} 🟢")
    elif winning_color == "красное":
        print(f"Выпало: {Colors.red}[ {wheel_result} КРАСНОЕ ]{Colors.reset} 🔴")
    else:
        print(f"Выпало: [ {wheel_result} ЧЁРНОЕ ] ⚫")

    time.sleep(0.4)

    level_multiplier = 1.0 + (level - 1) * 0.1

    if player_choice == winning_color:
        if player_choice == "зеро":
            mult = 35
            reward_xp = 500 if xp_x2 else 250

            print(f"\n{Colors.green}🔥 НЕВЕРОЯТНО! ВЫ СОРВАЛИ КУШ НА ЗЕРО!!! 🔥{Colors.reset}")

        else:
            mult = 2
            reward_xp = 60 if xp_x2 else 30

            print(f"\n{Colors.green}🎉 Победа! Ваша ставка сыграла!{Colors.reset}")

        reward_coins = int(money_player * mult * level_multiplier * (2 if balance_x2 else 1))

        balance += (money_player + reward_coins)
        xp += reward_xp

        print(f"💰 Вы получили {Colors.yellow}{fmt(reward_coins)}{Colors.reset} монет (Множитель уровня: {Colors.yellow}{level_multiplier:.1f}x{Colors.reset})!")
        print(f"📈 Вам начислено {Colors.yellow}{fmt(reward_xp)}{Colors.reset} XP!\n")
    
    else:
        print(f"\n{Colors.red}🔴 Увы, ставка не сыграла. Незнакомец забирает монеты!{Colors.reset}\n")

    return balance, xp
