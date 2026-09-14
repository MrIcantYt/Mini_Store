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
            print("\nПоздравляю! Вы угадали число! \n")

            if balance_x2:
                print("Вы получили 50 монет!\n")
                balance += 50
            elif not balance_x2:
                print("Вы получили 25 монет!\n")
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

def game_rock_scissors_paper():
    global balance

    print("\n == Игра: Камень, ножницы, бумага ==\n")

    tests = ["камень", "ножницы", "бумага"]

    life = 3

    while True:
        user_choice = input("Выберите: Камень, Ножницы, Бумага: ").lower().strip()

        random_choice = random.choice(tests)

        if life <= 0:
            print(f"\nВы проиграли! У бота было: \"{random_choice}\".\n")
            break

        elif (user_choice == "камень" and random_choice == "ножницы") or \
            (user_choice == "ножницы" and random_choice == "бумага") or \
            (user_choice == "бумага" and random_choice == "камень"):
                print(f"\nВы победили! И у вас оставалось {life} жизни.")
                print(f"У бота было \"{random_choice}\".\n")

                if balance_x2:
                    print("Вы получили 50 монет!\n")
                    balance += 50
                elif not balance_x2:
                    print("Вы получили 25 монет!\n")
                    balance += 25
                break

        elif user_choice == random_choice:
            print(f"\nНичья! У бота было: \"{random_choice}\".\n")

        elif (user_choice == "камень" and random_choice == "бумага") or \
            (user_choice == "ножницы" and random_choice == "камень") or \
            (user_choice == "бумага" and random_choice == "ножницы"):

            life -= 1

            print("\nВы не угадали! Попробуйте ещё раз!")
            print(f"У вас осталось {life} жизни!\n")

        else:
            print("\nНеизвестно!\n")

while True:
    print("1. Каталог")
    print("2. Игры")
    print("3. Баланс")
    print("4. Промокод")
    print("5. Выход")

    try:
        user_digit = int(input("\nВведите цифру: "))

        if user_digit == 1:
            try:
                with open("mini_store_shop.txt", "r", encoding="utf-8") as file:
                    file_open = file.read()

                    print("\n===============\n")
                    print(file_open)
                    print("\n===============\n")

                user_buy = input("Хотите ли вы что-то купить? (Yes or No): ")

                print()

                if user_buy.lower() == "yes":

                    try:
                        user_id_buy = int(input("Выберите ID продукта для покупки: "))

                        if user_id_buy == 1:
                            if not balance_x2:
                                if balance >= 100:
                                    print("\nУ вас списалось 100 монет, теперь у вас 2x монет! \n")

                                    balance -= 100
                                    balance_x2 = True

                                elif balance < 100:
                                    print("\nУ вас нету монет для этой покупки! \n")

                            elif balance_x2:
                                print("\nВы уже купили этот товар!\n")

                    except ValueError:
                        print("\nОшибка! Введите число!\n")

            except FileNotFoundError:
                print("\n[Магазин временно пуст — файл каталога не найден]\n")

        elif user_digit == 2:
            print("\n1. Угадать число")
            print("2. Камень, ножницы, бумага")
            print("3. Скоро")

            try:
                user_number_game = int(input("\nВведите число: "))

                if user_number_game == 1:
                    game_guess_number()

                elif user_number_game == 2:
                    game_rock_scissors_paper()

            except ValueError:
                print("\nОшибка! Введите число!\n")

        elif user_digit == 3:
            print(f"\nВаш баланс: {balance} монет\n")

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

    except ValueError:
        print("\nОшибка! Введите число!\n")
