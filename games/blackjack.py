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

# Игра: Блекджек (21 очко)
def blackjack(balance, balance_x2, xp, xp_x2, level):
    print(f"\n {Colors.yellow}== Игра: Блекджек (21 очко) =={Colors.reset}\n")

    cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
    player_score = 0
    bot_score = 0

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

    balance -= money_player

    player_score = random.choice(cards) + random.choice(cards)
    bot_score = random.choice(cards) + random.choice(cards)

    player_overflow = False

    while player_score < 21:
        print(f"\nУ вас на руках: {Colors.yellow}{player_score}{Colors.reset} очков")
        
        user_choice = input("1. Взять ещё карту | 2. Остановиться: ").strip()

        if user_choice == "1":
            random_cart = random.choice(cards)
            player_score += random_cart
            
            print(f"Вы вытянули карту: {Colors.yellow}{random_cart}{Colors.reset}")

            if player_score > 21:
                print(f"\nУ вас на руках: {Colors.red}{player_score}{Colors.reset} очков")
                print(f"\n{Colors.red}💥 Перебор! Вы проиграли свою ставку!{Colors.reset}\n")
                
                player_overflow = True
                
                break
        
        elif user_choice == "2":
            break
        
        else:
            print(f"\n{Colors.red}Неверный пункт! Выберите 1 или 2.{Colors.reset}\n")

    if player_overflow:
        return balance, xp

    if player_score == 21:
        print(f"\n🎉 {Colors.green}ОГО! У вас ровно 21 очко!{Colors.reset}")

    print(f"\n{Colors.blue}🤖 Очередь Дилера (Бота)...{Colors.reset}\n")
    
    print(f"Стартовые очки бота: {Colors.blue}{bot_score}{Colors.reset}")
    
    time.sleep(0.6)

    while bot_score < 17:
        bot_card = random.choice(cards)
        bot_score += bot_card
        
        print(f"🤖 Бот вытянул карту: {Colors.yellow}{bot_card}{Colors.reset} (Всего у бота: {bot_score})")
        
        time.sleep(0.6)

    print(f"\nФинальный счёт дилера: {Colors.blue}{bot_score}{Colors.reset} очков")
    
    time.sleep(0.4)

    level_multiplier = 1.0 + (level - 1) * 0.1

    if bot_score > 21 or player_score > bot_score:
        reward_coins = int(money_player * level_multiplier * (2 if balance_x2 else 1))
        reward_xp = 60 if xp_x2 else 30

        balance += (money_player + reward_coins)
        xp += reward_xp

        if bot_score > 21:
            print(f"\n🎉 {Colors.green}Бот перебрал ({bot_score} очков)! Вы победили!{Colors.reset}")
        
        else:
            print(f"\n🎉 {Colors.green}Поздравляю! У вас больше очков. Вы победили дилера!{Colors.reset}")

        print(f"💰 Вы получили {Colors.yellow}{fmt(reward_coins)}{Colors.reset} монет (Множитель уровня: {Colors.yellow}{level_multiplier:.1f}x{Colors.reset})!")
        print(f"📈 Вам начислено {Colors.yellow}{fmt(reward_xp)}{Colors.reset} XP!\n")

    elif player_score == bot_score:
        balance += money_player
        
        print(f"\n{Colors.yellow}🤝 Ничья! Очков поровну ({player_score} vs {bot_score}). Ставка возвращена на баланс.{Colors.reset}\n")

    else:
        print(f"\n{Colors.red}🔴 У дилера больше очков ({bot_score}). Вы проиграли свою ставку!{Colors.reset}\n")

    return balance, xp
