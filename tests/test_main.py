import sys
from pathlib import Path

import pytest

import mini_store.__main__ as main_module
import mini_store.shop as shop_module
from mini_store.__main__ import init_game, main
from mini_store.config import CONFIG
from mini_store.models import Player
from mini_store.sign import SignedJson


def test_version_flag(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(sys, 'argv', ['mini-store', '--version'])

    main()

    assert capsys.readouterr().out.strip() == f'Mini-Store {CONFIG.version}'


def write_raw_save(path: Path, content: str) -> None:
    save = SignedJson(path)
    path.write_text(save._get_save_sign(content) + '\n' + content)


def test_main_menu_shop_buy_and_exit(db, monkeypatch: pytest.MonkeyPatch) -> None:
    player = Player(id=1)
    player.balance = 1000
    db.save_player(player)

    monkeypatch.setattr(main_module, 'JsonDataBase', lambda: db)
    monkeypatch.setattr(shop_module.random, 'random', lambda: 0.5)
    inputs = iter(['1', '3', '1', '8'])
    monkeypatch.setattr('builtins.input', lambda _prompt='': next(inputs))

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

        ctx = init_game(1)

        assert ctx.player.id == 1
        assert ctx.player.balance == 0
        assert 'прогресс сброшен' in capsys.readouterr().out.lower()

    def test_init_game_resets_invalid_json(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.chdir(tmp_path)
        write_raw_save(tmp_path / 'game.json', '{invalid')

        ctx = init_game(1)

        assert ctx.player.id == 1
        assert ctx.player.balance == 0
        assert 'прогресс сброшен' in capsys.readouterr().out.lower()

    def test_init_game_loads_old_save_with_defaults(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
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

        ctx = init_game(1)

        assert ctx.player.balance == 500
        assert ctx.player.lvl == 3
        assert ctx.player.lucky_amulet is True
        assert ctx.player.has_coffee is True
        assert ctx.player.bank_deposit == 0
        assert ctx.player.bank_turns == 0
