import subprocess
from collections.abc import Callable

import pytest

import mini_store.utils
from mini_store.utils import HiddenOption, Option, ask_confirmation, ask_option, cls, fmt


@pytest.fixture
def options() -> list[Option[int]]:
    """Base menu shared by the `ask_option` tests."""
    return [Option(f'Item {i}', i) for i in range(1, 4)]


class TestFmt:
    @pytest.mark.parametrize(
        ('value', 'expected'),
        [
            (0, '0'),
            (7, '7'),
            (999, '999'),
            (1000, '1.000'),
            (1234567, '1.234.567'),
            (-1234567, '-1.234.567'),
        ],
    )
    def test_formats_with_dot_separator(self, value: int, expected: str) -> None:
        assert fmt(value) == expected


class TestCls:
    @pytest.fixture
    def run_calls(self, monkeypatch: pytest.MonkeyPatch) -> list[tuple[tuple, dict]]:
        calls: list[tuple[tuple, dict]] = []

        def fake_run(*args, **kwargs):
            calls.append((args, kwargs))
            return subprocess.CompletedProcess(args, returncode=0)

        monkeypatch.setattr(mini_store.utils, 'run', fake_run)
        return calls

    def test_clears_screen_on_posix(
        self,
        monkeypatch: pytest.MonkeyPatch,
        run_calls: list[tuple[tuple, dict]],
    ) -> None:
        monkeypatch.setattr(mini_store.utils, 'os_name', 'posix')

        cls()

        assert run_calls == [(('clear',), {'check': False})]

    def test_clears_screen_on_windows(
        self,
        monkeypatch: pytest.MonkeyPatch,
        run_calls: list[tuple[tuple, dict]],
    ) -> None:
        monkeypatch.setattr(mini_store.utils, 'os_name', 'nt')

        cls()

        assert run_calls == [(('cls',), {'shell': True, 'check': False})]


class TestAskConfirmation:
    @pytest.mark.parametrize(
        ('answer', 'expected'),
        [
            ('д', True),
            ('да', True),
            ('ДА', True),
            ('нет', False),
            ('no', False),
            ('ладно', False),
            ('думаю, нет', False),
        ],
    )
    def test_accepts_only_explicit_yes(
        self,
        feed_input: Callable[..., None],
        answer: str,
        expected: bool,
    ) -> None:
        feed_input(answer)

        assert ask_confirmation('Продолжить?') is expected


class TestAskOption:
    def test_simple(self, feed_input: Callable[..., None], options: list[Option[int]]) -> None:
        feed_input('1')

        assert ask_option('', options) == 1

    def test_choose_last_option(
        self,
        feed_input: Callable[..., None],
        options: list[Option[int]],
    ) -> None:
        feed_input('3')

        assert ask_option('', options) == 3

    def test_choose_not_exist_option_reprompts(
        self,
        feed_input: Callable[..., None],
        options: list[Option[int]],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        feed_input('99', '2')

        assert ask_option('', options) == 2
        assert 'Максимум: 3' in capsys.readouterr().out

    def test_auto_numbering_skips_reserved_positions(
        self,
        feed_input: Callable[..., None],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        feed_input('3')
        options = [
            Option('Первый', 'one', pos=1),
            Option('Второй', 'two', pos=2),
            Option('Третий', 'three'),
        ]

        assert ask_option('', options) == 'three'
        output = capsys.readouterr().out
        assert '3. Третий' in output
        assert '4. Третий' not in output

    def test_cancel(
        self,
        feed_input: Callable[..., None],
        options: list[Option[int]],
    ) -> None:
        feed_input('q')

        assert ask_option('', options, allow_cancel=True) is None

    def test_gap_in_positions_reprompts(
        self,
        feed_input: Callable[..., None],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        feed_input('3', '5')
        options = [Option('Пятый', 'five', pos=5)]

        assert ask_option('', options) == 'five'
        assert 'Нет такого пункта: 3' in capsys.readouterr().out

    def test_hidden_option_pos_cant_be_gl_len_options(self) -> None:
        options = [HiddenOption(1, 'hidden'), Option('Видимый', 'visible')]

        with pytest.raises(ValueError):
            ask_option('', options)

    def test_duplicate_numbers_raise(self) -> None:
        options = [Option('Первый', 'one', pos=1), Option('Второй', 'two', pos=1)]

        with pytest.raises(ValueError, match='Duplicate option number'):
            ask_option('', options)
