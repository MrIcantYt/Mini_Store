import sys
from json import JSONDecodeError

from mini_store.colors import Colors, enable_ansi
from mini_store.config import CONFIG
from mini_store.db import JsonDataBase
from mini_store.exceptions import SignCheckError
from mini_store.games import *
from mini_store.models import DailyContext, GameContext, Player
from mini_store.sections import *
from mini_store.utils import *

enable_ansi()


def init_game(player_id: int) -> GameContext:
    cls()
    db = JsonDataBase()
    db.init_db()

    try:
        player = db.get_player_by_id(player_id)
    except (FileNotFoundError, SignCheckError, ValueError, JSONDecodeError) as e:
        if isinstance(e, FileNotFoundError):
            print(
                f'\n{Colors.red}Файл сохранения не был найден. Было создано новое.{Colors.reset}\n'
            )
        elif isinstance(e, (JSONDecodeError, ValueError)):
            print(
                f'{Colors.red}Файл сохранения был повреждён. Ваш прогресс сброшен.{Colors.reset}\n'
            )
        else:
            print(f'\n{Colors.red}{e.message}. Ваш прогресс сброшен!{Colors.reset}\n')

        db.reset()
        player = None

    if player is None:
        player = Player(id=player_id)
        db.save_player(player)

    return GameContext(player, db, DailyContext())


def main() -> None:
    if '--version' in sys.argv[1:]:
        print(f'Mini-Store {CONFIG.version}')
        return

    # TODO: choose id
    player_id = 1
    ctx = init_game(player_id)

    if CONFIG.is_debug:
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
            Option('Банк', bank_menu),
            Option('Контракты Торговца', merchant_contracts),
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
        if CONFIG.is_debug:
            options.extend([Spacer(), Option('Debug menu', debug_menu, color=Colors.green)])

        section: SectionFunc | None = ask_option('Выберите пункт меню: ', options)

        if section is None:
            continue

        section(ctx)

        # # Passive business
        # if ctx.player.business:
        #     print(f'Незнакомец: {Colors.blue_dark}Ваш стартап принёс доход {Colors.yellow}+25 монет{Colors.blue_dark}.{Colors.reset}\n')

        #     ctx.player.balance += 25

        ctx.db.save_player(ctx.player)


# Запуск игры
if __name__ == '__main__':
    main()
