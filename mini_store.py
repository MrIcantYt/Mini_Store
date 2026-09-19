import random
import os
import json

promo = "MrIcant"
shop_file = "mini_store_shop.txt"
default_shop_content = "1. Множитель монет x2 — Цена: 100 монет (ID: 1)"
save_file = "save.json"

def load_game():
    if os.path.exists(save_file):
        with open(save_file, "r", encoding="utf-8") as file:
            data = json.load(file)

            return data["balance"], data["balance_x2"], data["promo_used"]
        
    return 0, False, False

def save_game(balance, balance_x2, promo_used):
    data = {
        "balance": balance,
        "balance_x2": balance_x2,
        "promo_used": promo_used,
    }

    with open(save_file, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def create_shop_if_not_exists():
    if not os.path.exists(shop_file):
        with open(shop_file, "w", encoding="utf-8") as file:
            file.write(default_shop_content)

def game_guess_number(balance, balance_x2):
    print("\n == Игра: Угадай число ==\n")

    number = random.randint(1, 15)

    life = 3

    while life > 0:
        try:
            user_number = int(input("Введите число (От 1 до 15): "))

        except ValueError:
            print("Ошибка! Введите целое число.")
            continue

        life -= 1

        if user_number == number:
            reward = 50 if balance_x2 else 25

            print(f"\nПоздравляю! Вы угадали число! Вы получили {reward} монет!\n")

            return balance + reward

        elif life == 0:
            print(f"\nВы програли! Загаданное число было: {number}.\n")

        elif user_number > number:
            print(f"\nЗагаданное число меньше! Осталось жизней: {life}\n")

        elif user_number < number:
            print(f"\nЗагаданное число больше! Осталось жизней: {life}\n")

    return balance

def game_rock_scissors_paper(balance, balance_x2):
    print("\n == Игра: Камень, ножницы, бумага ==\n")

    variants = ["камень", "ножницы", "бумага"]

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
            reward = 50 if balance_x2 else 25

            print(f"\nВы победили! У вас оставалось {life} жизней. Вы получили {reward} монет!\n")

            return balance + reward

        elif user_choice == bot_choice:
            print("Ничья! Продолжаем...\n")

        else:
            life -= 1

            print(f"Вы не угадали! У вас осталось {life} жизни!\n")
            
            if life == 0:
                print("Вы полностью проиграли в этой игре!\n")

    return balance

def main():
    create_shop_if_not_exists()

    balance = 0
    balance_x2 = False
    promo_used = False

    balance, balance_x2, promo_used = load_game()

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
            print("\nОшибка! Введите число!\n")
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

                        print()

                        if user_id_buy == 1:
                            if balance_x2:
                                print("Вы уже купили этот товар!\n")

                            elif balance >= 100:
                                balance -= 100
                                balance_x2 = True
                                save_game(balance, balance_x2, promo_used)

                                print("Успешно! Списано 100 монет, теперь у вас x2 бонус к выигрышу!\n")

                            else:
                                print(f"Недостаточно монет! Нужно 100, а у вас {balance}.\n")

                        else:
                            print("\nТовара с таким ID не существует!\n")

                    except ValueError:
                        print("\nОшибка! Введите корректный ID числом!\n")

            except FileNotFoundError:
                print("\n[Магазин временно пуст]\n")

        elif user_digit == 2:
            print("\n1. Угадать число")
            print("2. Камень, ножницы, бумага")

            try:
                user_number_game = int(input("\nВведите число игры: "))

                if user_number_game == 1:
                    balance = game_guess_number(balance, balance_x2)
                    save_game(balance, balance_x2, promo_used)

                elif user_number_game == 2:
                    balance = game_rock_scissors_paper(balance, balance_x2)
                    save_game(balance, balance_x2, promo_used)

                else:
                    print("\nТакой игры нет.\n")

            except ValueError:
                print("\nОшибка! Введите число!\n")

        elif user_digit == 3:
            print("\n===== ВАШ ПРОФИЛЬ =====\n")
            print(f"Баланс: {balance} монет")
            
            status_x2 = "🟢 Активирован" if balance_x2 else "🔴 Не куплен"
            
            print(f"Множитель x2: {status_x2}")
            
            status_promo = "🟢 Использован" if promo_used else "🔴 Доступен для ввода"

            print(f"Промокод: {status_promo}")
            print("\n=======================\n")


        elif user_digit == 4:
            if not promo_used:
                user_promo = input("\nВведите промокод: ").strip()

                if user_promo == promo:
                    balance += 100 if balance_x2 else 50
                    promo_used = True
                    save_game(balance, balance_x2, promo_used)

                    if balance_x2:
                        print("\nУспешно! На ваш баланс пришло 100 Монет!\n")
                    elif not balance_x2:
                        print("\nУспешно! На ваш баланс пришло 50 Монет!\n")
                else:
                    print("\nПромокод не верен!\n")

            elif promo_used:
                print("\nПромокод уже был введён!\n")

        elif user_digit == 5:
            save_game(balance, balance_x2, promo_used)

            print("\nПрогресс сохранен! Прощайте, удачи вам! \n")
            break

        else:
            print(f"\nНеизвестный пункт меню: {user_digit} \n")

if __name__ == "__main__":
    main()