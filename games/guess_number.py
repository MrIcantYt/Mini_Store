import random

class Colors:
    red = "\033[31m"
    green = "\033[32m"
    yellow = "\033[33m"
    blue_dark = "\033[34m"
    blue = "\033[36m"
    reset = "\033[0m"

def fmt(value):
    return f"{value:,}".replace(",", ".")

# Игра: Угадай число
def game_guess_number(balance, balance_x2, xp, xp_x2, level, lucky_amulet, lucky_ticket, potion_luck):
    print(f"\n {Colors.yellow}== Игра: Угадай число == {Colors.reset}\n")

    try:
        choose = int(input(f"Выберите сложность {Colors.green}Лёгкая (1){Colors.reset}, {Colors.yellow}Средняя (2){Colors.reset}, {Colors.red}Сложная (3){Colors.reset}: "))

        if choose == 1:
            number, num = random.randint(1, 15), 15

        elif choose == 2:
            number, num = random.randint(1, 25), 25

        elif choose == 3:
            number, num = random.randint(1, 50), 50

        else:
            print(f"\n{Colors.red}Ошибка! Выбрана несуществующая сложность. Возврат в меню.{Colors.reset}\n")

            return balance, xp

        life = 4 if lucky_amulet else 3

        while life > 0:
            try:
                user_number = int(input(f"Введите число (От 1 до {num}): "))

            except ValueError:
                print(f"\n{Colors.red}Ошибка! Введите целое число. {Colors.reset}\n")
                continue

            life -= 1

            if lucky_ticket:
                lucky_ticket = False
                life += 1

                print(f"\n🎫 {Colors.yellow}Счастливый тикет сработал и спас вашу жизнь!{Colors.reset}")

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

                print(f"\n🎉 {Colors.green}Поздравляю! Вы победили! {Colors.reset}")
                print(f"💰 Вы получили {Colors.yellow}{fmt(reward_coins)}{Colors.reset} монет (Множитель уровня: {Colors.yellow}{level_multiplier:.1f}x{Colors.reset})!")
                print(f"📈 Вам начислено {Colors.yellow}{fmt(reward_xp)}{Colors.reset} XP!\n")

                return balance + reward_coins, xp + reward_xp

            elif life == 0:
                print(f"\n{Colors.red}Вы програли! Загаданное число было: {number}. {Colors.reset}\n")
                return balance, xp

            elif user_number > number:
                print(f"\nЗагаданное число меньше! Осталось жизней: {life}\n")

            elif user_number < number:
                print(f"\nЗагаданное число больше! Осталось жизней: {life}\n")

        return balance, xp

    except (ValueError, TypeError):
        print(f"\n{Colors.red}Ошибка! Введите корректное число. {Colors.reset}\n")

        return balance, xp
