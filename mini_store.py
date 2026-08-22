import random

print("\n === Добро пожаловать в \"Мини Магазин\" === \n")

balance = 0
balance_x2 = False
promo = "MrIcant"
promo_used = False

def game_guess_number():
    global balance

    print("\n == Игра: Угадай число ==\n")

    number = random.randint(1, 15)

    life = 3

    while True:
        user_number = int(input("Введите число: "))

        life -= 1

        if user_number == number:
            print(f"\nПоздравляю! Вы угадали число! \n")

            if balance_x2:
                print("Вы получаете 50 Монет!\n")
                balance += 50
            elif not balance_x2:
                print("Вы получаете 25 Монет!\n")
                balance += 25
            break

        elif life <= 0:
            print(f"\nВы програли! У вас {life} жизней.")
            print(f"Загаданное число было {number}.\n")
            break

        elif user_number > number:
            print(f"\nЗагаданное число меньше! Осталось жизней: {life}\n")

        elif user_number < number:
            print(f"\nЗагаданное число больше! Осталось жизней: {life}\n")

while True:
    print("1. Каталог")
    print("2. Игры")
    print("3. Баланс")
    print("4. Промокод")
    print("5. Выход")

    user_digit = int(input("\nВведите цифру: "))

    if user_digit == 1:
        with open("mini_store_shop.txt", "r", encoding="utf-8") as file:
            file_open = file.read()

            print("\n===============\n")
            print(file_open)
            print("\n===============\n")

        user_buy = input("Хотите ли вы что-то купить? (Yes or No): ")

        print()

        if "e" in user_buy:
            user_id_buy = int(input("Выберите ID продукта для покупки: "))

            if user_id_buy == 1:
                if not balance_x2:
                    if balance >= 100:
                        print("\nУ вас списалось 100 рублей, теперь у вас 2x монет! \n")

                        balance -= 100
                        balance_x2 = True

                    elif balance < 100:
                        print("\nУ вас нету денег для этой покупки! \n")
                elif balance_x2:
                    print("\nВы уже купили этот товар!\n")

    elif user_digit == 2:
        print("\n1. Угадать число")
        print("2. Скоро")

        user_number_game = int(input("\nВведите число: "))

        if user_number_game == 1:
            game_guess_number()

    elif user_digit == 3:
        print(f"\nВаш баланс: {balance} \n")

    elif user_digit == 4:

        if not promo_used:
            user_promo = input("\nВведите промокод: ")

            if user_promo == promo:
                print("\nУспешно, промокод был активирован! На ваш баланс пришло 50 Монет! \n")

                balance += 50
                promo_used = True

            elif user_promo != promo:
                print("\nПромокод не верен! \n")

        elif promo_used:
            print("\nПромокод уже был введён! \n")

    elif user_digit == 5:
        print("\nПрощайте, удачи вам! \n")
        break

    else:
        print(f"\nНеизвестно: {user_digit} \n")