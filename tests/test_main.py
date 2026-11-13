import sys
from collections.abc import Callable
from json import JSONDecodeError
from pathlib import Path

import pytest

import mini_store.__main__ as main_module
import mini_store.shop as shop_module
from mini_store.__main__ import init_game, main, select_or_create_player
from mini_store.config import CONFIG
from mini_store.exceptions import SignCheckError
from mini_store.models import Player
from mini_store.sign import SignedJson


def test_version_flag(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(sys, 'argv', ['mini-store', '--version'])

    main()

    assert capsys.readouterr().out.strip() == f'Mini-Store {CONFIG.version}'


def write_raw_save(path: Path, content: str) -> None:
    save = SignedJson(path)
    path.write_text(save._get_save_sign(content) + '\n' + content)


def test_main_menu_shop_buy_and_exit(
    db, monkeypatch: pytest.MonkeyPatch, feed_input: Callable[..., None]
) -> None:
    player = Player(id=1)
    player.balance = 1000
    db.save_player(player)

    monkeypatch.setattr(main_module, 'JsonDataBase', lambda: db)
    monkeypatch.setattr(shop_module.random, 'random', lambda: 0.5)
    feed_input('1', '1', '3', '1', '8')

    with pytest.raises(SystemExit):
        main()

    assert db.saved[-1].lucky_amulet is True
    assert db.saved[-1].balance == 700


class TestInitGame:
    def test_init_game_resets_file_without_separator(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.chdir(tmp_path)
        (tmp_path / 'game.json').write_text('no-signature')

        ctx = init_game()

        assert ctx.player.id == 1
        assert ctx.player.balance == 0
        assert 'прогресс сброшен' in capsys.readouterr().out.lower()

    def test_init_game_resets_invalid_json(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.chdir(tmp_path)
        write_raw_save(tmp_path / 'game.json', '{invalid')

        ctx = init_game()

        assert ctx.player.id == 1
        assert ctx.player.balance == 0
        assert 'прогресс сброшен' in capsys.readouterr().out.lower()

    def test_init_game_loads_old_save_with_defaults(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, feed_input: Callable[..., None]
    ) -> None:
        monkeypatch.chdir(tmp_path)
        legacy = {
            'id': 1,
            'balance': 500,
            'balance_multiplier': 1,
            'xp': 0,
            'xp_multiplier': 1,
            'lvl': 3,
            'promo_used': False,
            'lucky_amulet': True,
            'secret_used': False,
            'bought': 0,
            'mining_lvl': 0,
            'potion_luck': False,
            'lucky_ticket': False,
            'buy_num_boost': 0,
            'business': False,
            'secret_case': 0,
            'quest_id': 1,
            'quest_progress': 0,
            'rebirths': 0,
        }
        SignedJson(tmp_path / 'game.json').dump({'players': [legacy]})
        feed_input('1')

        ctx = init_game()

        assert ctx.player.balance == 500
        assert ctx.player.lvl == 3
        assert ctx.player.lucky_amulet is True
        assert ctx.player.has_coffee is False
        assert ctx.player.bank_deposit == 0
        assert ctx.player.bank_turns == 0


def fail_with(error: BaseException) -> Callable[[], list[Player]]:
    def fail() -> list[Player]:
        raise error

    return fail


def spy_reset(db, monkeypatch: pytest.MonkeyPatch) -> list[bool]:
    calls: list[bool] = []
    original_reset = db.reset

    def reset() -> None:
        calls.append(True)
        original_reset()

    monkeypatch.setattr(db, 'reset', reset)
    return calls


class TestSelectOrCreatePlayer:
    def test_creates_player_when_database_is_empty(self, db, capsys) -> None:
        player = select_or_create_player(db)

        assert player.id == 1
        assert player.balance == 0
        assert db.saved == [player]
        assert 'сброшен' not in capsys.readouterr().out.lower()

    @pytest.mark.parametrize(
        ('error', 'message'),
        [
            pytest.param(FileNotFoundError(), 'не был найден', id='missing-file'),
            pytest.param(ValueError('broken'), 'повреждён или устарел', id='value-error'),
            pytest.param(TypeError('broken'), 'повреждён или устарел', id='type-error'),
            pytest.param(
                JSONDecodeError('broken', '', 0), 'повреждён или устарел', id='invalid-json'
            ),
            pytest.param(
                SignCheckError('Подпись не совпала'), 'Подпись не совпала', id='sign-error'
            ),
        ],
    )
    def test_resets_database_and_creates_player_on_load_error(
        self, db, monkeypatch: pytest.MonkeyPatch, capsys, error: BaseException, message: str
    ) -> None:
        monkeypatch.setattr(db, 'get_all_players', fail_with(error))
        reset_calls = spy_reset(db, monkeypatch)

        player = select_or_create_player(db)

        assert reset_calls == [True]
        assert player.id == 1
        assert db.saved == [player]
        assert message in capsys.readouterr().out

    @pytest.mark.parametrize(('choice', 'expected_id'), [('1', 1), ('2', 2)])
    def test_loads_selected_player(
        self, db, feed_input: Callable[..., None], choice: str, expected_id: int
    ) -> None:
        first = Player(id=1)
        first.balance = 100
        second = Player(id=2)
        second.balance = 200
        db.save_player(first)
        db.save_player(second)
        feed_input(choice)

        player = select_or_create_player(db)

        assert player.id == expected_id
        assert player.balance == (100 if expected_id == 1 else 200)

    def test_sorts_players_by_id_before_choosing(
        self, db, feed_input: Callable[..., None], capsys
    ) -> None:
        second = Player(id=2)
        first = Player(id=1)
        db.save_player(second)
        db.save_player(first)
        feed_input('1')

        player = select_or_create_player(db)

        assert player is first
        out = capsys.readouterr().out
        assert out.index('Сохранение #1') < out.index('Сохранение #2')

    def test_new_game_gets_next_id_after_max(self, db, feed_input: Callable[..., None]) -> None:
        db.save_player(Player(id=1))
        db.save_player(Player(id=3))
        feed_input('3')

        player = select_or_create_player(db)

        assert player.id == 4
        assert db.saved[-1] is player
        assert len(db.saved) == 3

    def test_none_choice_exits(self, db, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
        db.save_player(Player(id=1))
        monkeypatch.setattr(main_module, 'ask_option', lambda *_, **__: None)

        with pytest.raises(SystemExit):
            select_or_create_player(db)

        assert 'Выход из игры' in capsys.readouterr().out

    def test_exit_option_exits(self, db, feed_input: Callable[..., None], capsys) -> None:
        db.save_player(Player(id=1))
        feed_input('3')

        with pytest.raises(SystemExit):
            select_or_create_player(db)

        assert 'Выход из игры' in capsys.readouterr().out

    def test_invalid_number_reprompts(self, db, feed_input: Callable[..., None], capsys) -> None:
        db.save_player(Player(id=1))
        feed_input('99', '1')

        player = select_or_create_player(db)

        assert player.id == 1
        assert 'Максимум: 3' in capsys.readouterr().out
