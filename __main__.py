from colorama import init as colorama_init

from colors import Colors
from db import JsonDataBase
from exceptions import SignCheckError
from games import *
from player import Player
from sections import *
from utils import *

colorama_init()


def init_game(player_id: int) -> tuple[JsonDataBase, Player]:
    db = JsonDataBase()
    db.init_db()

    try:
        player = db.get_player_by_id(player_id)
    except SignCheckError as e:
        print(f'\n{Colors.red}{e.message}. Ваш прогресс сброшен!{Colors.reset}')
        player = None

    if player is None:
        player = Player(id=player_id)
        db.save_player(player)

    return db, player


def main():
    first_iteration = True
    player_id = 1
    db, player = init_game(player_id)

    if player is None:
        print(f'\n{Colors.red}Ошибка! Игрок с ID {player_id} не найден.{Colors.reset}\n')
        return

    while True:
        clear_console()

        if first_iteration:
            print('\n === Добро пожаловать в "Мини Магазин" === \n')
            first_iteration = False

        print(
            '1. Магазин',
            '2. Игры',
            '3. Профиль',
            '4. Майнинг ферма',
            '5. Задания незнакомца',
            '6. Выход',
            f'\n{Colors.red}7. Сброс игры{Colors.reset}',
            sep='\n',
        )

        max_value = 7
        if not player.promo_used:
            max_value = 8
            print(f'\n{Colors.yellow}8. Промокод{Colors.reset}')

        section_choose = ask_number('Выберите пункт меню: ', max=max_value)
        if not section_choose:
            continue

        # Passive business
        if player.business:
            print(
                f'\nНезнакомец: {Colors.blue_dark}Стартап принёс доход: {Colors.yellow}+25 монет{Colors.blue_dark}.{Colors.reset}'
            )

            player.balance += 25

        match section_choose:
            case 666:  # Easter egg
                if not player.secret_used:
                    print(f'Вы нашли пасхалку!\n{player.add_coins(100)}\n')
                    player.secret_used = True
                else:
                    print(f'{Colors.red}Ошибка 666! Вы уже нашли пасхалку!{Colors.reset}\n')

            case 1:  # Shop
                shop(player)

            case 2:  # Games
                game(player)

            case 3:  # Profile
                profile(player)

            case 4:  # Mining Farm
                mining(player)

            case 5:  # Stranger
                stranger(player)

            case 6:  # Exit
                db.save_player(player)
                print('\nПрогресс сохранен! Прощайте, удачи вам! \n')
                break

            case 7:  # Progress reset
                if not confirm(
                    f'\nНезнакомец: {Colors.blue_dark}Вы уверенны, что хотите сбросить весь свой прогресс?{Colors.reset}\n'
                ):
                    continue

                print(
                    f'\nНезнакомец: {Colors.blue_dark}Хорошо! Ваше решение принято.{Colors.reset}\n'
                )

                db.reset_player(player_id)

            case 8:  # Promo-code
                promocode(player)
            case _:  # Unknown
                print(f'\n{Colors.red}Неизвестный пункт меню: {section_choose}{Colors.reset} \n')

        db.save_player(player)


# Запуск игры
if __name__ == '__main__':
    main()
