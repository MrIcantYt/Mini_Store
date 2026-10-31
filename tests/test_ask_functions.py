import pytest

from mini_store.utils import (
    HiddenOption,
    Option,
    Spacer,
    ask_confirmation,
    ask_number,
    ask_option,
)


def feed_input(monkeypatch: pytest.MonkeyPatch, *values: str) -> None:
    iterator = iter(values)
    monkeypatch.setattr('builtins.input', lambda _prompt='': next(iterator))


class TestAskConfirmation:
    @pytest.mark.parametrize(
        ('answer', 'expected'),
        [('да', True), ('ДА', True), ('нет', False), ('no', False), ('', False)],
    )
    def test_answers(
        self,
        monkeypatch: pytest.MonkeyPatch,
        answer: str,
        expected: bool,
    ) -> None:
        feed_input(monkeypatch, answer)

        assert ask_confirmation('Продолжить?') is expected


class TestAskNumber:
    def test_returns_number(self, monkeypatch: pytest.MonkeyPatch) -> None:
        feed_input(monkeypatch, ' 5 ')

        assert ask_number('Число: ') == 5

    def test_retries_after_invalid_input(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        feed_input(monkeypatch, 'abc', '3')

        assert ask_number('Число: ') == 3
        assert 'Введите корректное число' in capsys.readouterr().out

    def test_retries_below_minimum(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        feed_input(monkeypatch, '0', '2')

        assert ask_number('Число: ', min=1) == 2
        assert 'Минимум: 1' in capsys.readouterr().out

    def test_retries_above_maximum(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        feed_input(monkeypatch, '10', '2')

        assert ask_number('Число: ', max=5) == 2
        assert 'Максимум: 5' in capsys.readouterr().out

    def test_cancel(self, monkeypatch: pytest.MonkeyPatch) -> None:
        feed_input(monkeypatch, 'q')

        assert ask_number('Число: ', allow_cancel=True) is None

    def test_custom_cancel_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        feed_input(monkeypatch, '3')

        result = ask_number('Число: ', max=2, allow_cancel=True, cancel_on='3')

        assert result is None

    def test_hidden_value_bypasses_bounds(self, monkeypatch: pytest.MonkeyPatch) -> None:
        feed_input(monkeypatch, '666')

        result = ask_number('Число: ', max=2, hidden_values=[666])

        assert result == 666


class TestAskOption:
    def test_returns_selected_value(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        feed_input(monkeypatch, '2')
        options = [Option('Первый', 'one'), Option('Второй', 'two')]

        result = ask_option('Выбор: ', options)

        assert result == 'two'
        output = capsys.readouterr().out
        assert '1. Первый' in output
        assert '2. Второй' in output

    def test_cancel(self, monkeypatch: pytest.MonkeyPatch) -> None:
        feed_input(monkeypatch, 'q')

        assert ask_option('Выбор: ', [Option('Один', 1)], allow_cancel=True) is None

    def test_hidden_option(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        feed_input(monkeypatch, '666')
        options = [Option('Один', 1), HiddenOption(666, 'secret')]

        result = ask_option('Выбор: ', options)

        assert result == 'secret'
        assert '666' not in capsys.readouterr().out

    def test_spacer_does_not_take_a_number(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        feed_input(monkeypatch, '2')
        options = [Option('Один', 1), Spacer(lines=2), Option('Два', 2)]

        assert ask_option('Выбор: ', options) == 2
        output = capsys.readouterr().out
        assert '1. Один' in output
        assert '2. Два' in output

    def test_fixed_position_is_respected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        feed_input(monkeypatch, '5')
        options = [Option('Первый', 'one', pos=5), Option('Второй', 'two')]

        assert ask_option('Выбор: ', options) == 'one'

    def test_auto_numbering_skips_reserved_positions(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        feed_input(monkeypatch, '1')
        options = [Option('Первый', 'one', pos=5), Option('Второй', 'two')]

        assert ask_option('Выбор: ', options) == 'two'

    def test_duplicate_numbers_raise(self) -> None:
        options = [Option('Первый', 1, pos=1), Option('Второй', 2, pos=1)]

        with pytest.raises(ValueError, match='Duplicate option number'):
            ask_option('Выбор: ', options)

    def test_blank_line_can_be_disabled(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        feed_input(monkeypatch, '1')

        ask_option('Выбор: ', [Option('Один', 1)], blank_line=False)

        assert '1. Один' in capsys.readouterr().out
