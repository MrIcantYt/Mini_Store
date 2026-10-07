from colorama import init as colorama_init

from mini_store.colors import Colors
from mini_store.db import JsonDataBase
from mini_store.exceptions import SignCheckError
from mini_store.games import *
from mini_store.player import Player
from mini_store.sections import *
from mini_store.utils import *

colorama_init()


def init_game(player_id: int) -> GameContext:
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

    return GameContext(player, db)


def main():
    # TODO: choose id
    player_id = 1
    ctx = init_game(player_id)

    if ctx.player is None:
        print(
            f'\n{Colors.red}Ошибка! Игрок с ID {player_id} не найден.{Colors.reset}\n'
        )
        return

    cls()
    while True:
        print('\n === Добро пожаловать в "Мини Магазин" === \n')

        options = [
            Option('Магазин', shop),
            Option('Игры', game),
            Option('Профиль', profile),
            Option('Майнинг ферма', mining),
            Option('Задания незнакомца', stranger),
            Option('Сброс', reset, color=Colors.red),
            Spacer(),
            Option('Выход', game_exit),
            HiddenOption(666, easter_egg),
        ]

        if not ctx.player.promo_used:
            options.extend(
                [
                    Spacer(),
                    Option('Промокод', promocode, color=Colors.yellow),
                ]
            )

        section: SectionFunc | None = ask_option(
            'Выберите пункт меню: ', options
        )
        if not section:
            continue

        # Passive business
        if ctx.player.business:
            print(
                f'\nНезнакомец: {Colors.blue_dark}Стартап принёс доход: {Colors.yellow}+25 монет{Colors.blue_dark}.{Colors.reset}'
            )

            ctx.player.balance += 25

        section(ctx)

        ctx.db.save_player(ctx.player)


# Запуск игры
if __name__ == '__main__':
    main()
