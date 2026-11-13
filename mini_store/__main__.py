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


def select_or_create_player(db: JsonDataBase) -> Player:
    """Выбирает существующее сохранение или создаёт новое."""
    try:
        players = db.get_all_players()
    except (FileNotFoundError, SignCheckError, ValueError, JSONDecodeError, TypeError) as e:
        if isinstance(e, FileNotFoundError):
            print(
                f'\n{Colors.red}Файл сохранения не был найден. Было создано новое.{Colors.reset}\n'
            )
        elif isinstance(e, (JSONDecodeError, ValueError, TypeError)):
            print(
                f'{Colors.red}Файл сохранения был повреждён или устарел. Ваш прогресс сброшен.{Colors.reset}\n'
            )
        else:
            print(f'\n{Colors.red}{e.message}. Ваш прогресс сброшен!{Colors.reset}\n')

        db.reset()

        players = []

    if not players:
        player = Player(id=1)
        db.save_player(player)
        return player

    players.sort(key=lambda p: p.id)

    while True:
        cls()
        print('=== ВЫБОР СОХРАНЕНИЯ ===\n')

        options: list = []
        for p in players:
            options.append(Option(f'Save {p.id}', p))

        next_id = max(p.id for p in players) + 1
        options.extend(
            [
                Spacer(),
                Option('Создать новую игру', 'NEW', color=Colors.green),
                Spacer(),
                Option('Выход', sys.exit),
            ]
        )

        choice = ask_option('Выберите слот: ', options)

        if choice is None:
            continue

        if choice is sys.exit:
            print(f'\n{Colors.red}Выход из игры...{Colors.reset}\n')
            sys.exit()

        if choice == 'NEW':
            new_player = Player(id=next_id)
            db.save_player(new_player)
            return new_player

        return choice


def init_game() -> GameContext:
    cls()
    db = JsonDataBase()
    db.init_db()

    player = select_or_create_player(db)
    cls()

    return GameContext(player, db, DailyContext())


def main() -> None:
    if '--version' in sys.argv[1:]:
        print(f'Mini-Store {CONFIG.version}')
        return

    ctx = init_game()

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

        ctx.db.save_player(ctx.player)


# Запуск игры
if __name__ == '__main__':
    main()
