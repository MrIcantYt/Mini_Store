from colorama import init as colorama_init

from mini_store.colors import Colors
from mini_store.config import is_debug
from mini_store.db import JsonDataBase
from mini_store.exceptions import SignCheckError
from mini_store.games import *
from mini_store.player import Player
from mini_store.sections import *
from mini_store.utils import *

colorama_init()


def init_game(player_id: int) -> GameContext:
    cls()
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

    if is_debug:
        print(
            f"{Colors.green}You're in debug mode. The save's sign check is disabled.{Colors.reset}\n"
        )
    while True:
        print('=== Добро пожаловать в "Мини Магазин" ===\n')

        options: list = [
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
        if is_debug:
            options.extend(
                [Spacer(), Option('Debug menu', debug_menu, color=Colors.green)]
            )

        section: SectionFunc | None = ask_option('Выберите пункт меню: ', options)
        if section is None:
            continue

        section(ctx)

        # Passive business
        if ctx.player.business:
            print(
                f'\nНезнакомец: {Colors.blue_dark}Ваш стартап принёс доход {Colors.yellow}+25 монет{Colors.blue_dark}.{Colors.reset}'
            )

            ctx.player.balance += 25

        ctx.db.save_player(ctx.player)


# Запуск игры
if __name__ == '__main__':
    main()
