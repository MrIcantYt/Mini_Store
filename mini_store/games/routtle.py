import random
import time

from mini_store.colors import Colors
from mini_store.utils import *

from .abstract import AbstractGame

class RouttleGame(AbstractGame):
    def play(self) -> None:
        print(f"\n {Colors.yellow}== Игра: Рулетка Казино =={Colors.reset}\n")

        user_input = input(f"Введите вашу ставку или 'all'/'все' (Ваш баланс: {fmt(self._player.balance)}): ").strip().lower()

        if user_input == "all" or user_input == "все":
            bet = self._player.balance
        
        else:
            if not user_input.isdigit():
                print(f"\n{Colors.red}Ошибка! Введите корректное число или слово 'all'/'все'.{Colors.reset}\n")
                return
        
            bet = int(user_input)

        if bet <= 0:
            print(f"\n{Colors.red}Ошибка! Ставка {fmt(bet)} монет невозможна! Нельзя играть на 0 или меньше.{Colors.reset}\n")
            return
        
        elif bet > self._player.balance:
            print(f"\n{Colors.red}Ошибка! Нельзя вводить ставку больше своего баланса!{Colors.reset}\n")
            return

        bet_option = ask_option('Выберите тип ставки: ', [
            Option(f'На {Colors.red}Красное{Colors.reset} (Выигрыш x2)', 'красное'),
            Option('На Чёрное (Выигрыш x2)', 'черное'),
            Option(f'На {Colors.green}Зеро (0){Colors.reset} (Выигрыш x35!)', 'зеро')
        ])

        self._player.balance -= bet

        print(f"\n| 🎰 СТАВКА ПРИНЯТА. КОЛЕСО РУЛЕТКИ ЗАПУЩЕНО... |")
        time.sleep(0.5)
        print(" [ . ]", end="", flush=True)
        time.sleep(0.5)
        print(" [ .. ]", end="", flush=True)
        time.sleep(0.5)
        print(" [ ... ]\n")
        time.sleep(0.5)

        wheel_result = random.randint(0, 36)

        if self._player.potion_luck and bet_option in ["красное", "черное"]:
            if random.randint(1, 100) <= 35:
                winning_color = bet_option
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

        if bet_option == winning_color:
            if bet_option == "зеро":
                mult = 35
                reward_xp = 250

                print(f"\n{Colors.green}🔥 НЕВЕРОЯТНО! ВЫ СОРВАЛИ КУШ НА ЗЕРО!!! 🔥{Colors.reset}")

            else:
                mult = 2
                reward_xp = 30

                print(f"\n{Colors.green}🎉 Победа! Ваша ставка сыграла!{Colors.reset}")

            reward_coins = int(bet * mult)

            print(self._player.add_coins_and_xp(coins=reward_coins, xp=reward_xp))

        else:
            print(f"\n{Colors.red}🔴 Увы, ставка не сыграла. Незнакомец забирает монеты!{Colors.reset}\n")

        return
