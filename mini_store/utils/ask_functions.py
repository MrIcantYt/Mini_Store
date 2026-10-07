from dataclasses import dataclass

from mini_store.colors import Colors


@dataclass(slots=True)
class Option[T]:
    """A visible menu option, printed and numbered automatically.

    Attributes:
        name (str): Display name shown in the menu.
        value (T): Value returned when this option is selected.
    """

    name: str
    value: T
    pos: int | None = None
    color: Colors | None = None


@dataclass(slots=True)
class HiddenOption[T]:
    """A hidden menu option, not printed but selectable by number.

    Attributes:
        number (int): The number the user must enter to select this option.
        value (T): Value returned when this option is selected.
    """

    number: int
    value: T


@dataclass(slots=True)
class Spacer:
    """A spacer that adds blank lines to the menu output."""

    lines: int = 1


def ask_number(
    prompt: str,
    *,
    min: int = 1,
    max: int | None = None,
    allow_cancel: bool = False,
    cancel_on: str = 'q',
    hidden_values: list[int] | None = None,
) -> int | None:
    """Reads an integer from the user with bounds checking.

    Re-prompts on invalid input until a valid number is entered or the
    user cancels. Invalid input includes non-numeric strings and values
    outside the allowed range.

    Args:
        prompt (str): The input prompt shown to the user.
        min (int): Minimum accepted value (inclusive). Defaults to 1.
        max (int | None): Maximum accepted value (inclusive). If None,
            the upper bound is not checked.
        allow_cancel (bool): If True, the user can cancel by entering
            cancel_on.
        cancel_on (str): Cancellation string. Compared case-insensitively.
            Only used when allow_cancel=True.
        hidden_values (list[int] | None): Values that bypass the min/max
            bounds. Intended for secret codes and hidden menu options.
            If a value is in this list, it is returned immediately,
            regardless of the bounds.

    Returns:
        int | None: The parsed integer, or None if the user cancelled.

    Example:
        >>> n = ask_number("How many? ", min=1, max=10)
        >>> if n is None:
        ...     print("Cancelled")
    """
    while True:
        raw = input(prompt).strip().lower()

        if allow_cancel and raw == cancel_on:
            return None

        try:
            value = int(raw)
        except ValueError:
            print(f'\n{Colors.red}Ошибка! Введите корректное число, а не: {raw!r}.{Colors.reset}\n')
            continue

        if hidden_values is not None and value in hidden_values:
            return value
        elif value < min:
            print(f'{Colors.red}Минимум: {min}{Colors.reset}')
            continue
        elif max is not None and value > max:
            print(f'{Colors.red}Максимум: {max}{Colors.reset}')
            continue

        return value


def ask_option[T](
    prompt: str,
    options: list[Option[T] | HiddenOption[T] | Spacer],
    *,
    allow_cancel: bool = False,
    cancel_on: str = 'q',
) -> T | None:
    """Prompts the user to pick a menu option by number.

    Visible options are printed and numbered. By default they are
    numbered sequentially starting at 1, skipping positions already
    taken by options with a fixed position. Hidden options are not
    printed but can be selected by entering their number manually.
    Spacers print blank lines and have no number or value.

    Args:
        prompt (str): The input prompt shown to the user.
        options (list[Option[T] | HiddenOption[T] | Spacer]): List of
            visible options, hidden options, and spacers. Visible options
            are numbered automatically unless a fixed position is set.
            Hidden options use their explicit number. Spacers insert
            blank lines into the output.
        allow_cancel (bool): If True, the user can cancel the selection
            by entering cancel_on.
        cancel_on (str): Cancellation string. Compared case-insensitively.
            Only used when allow_cancel=True.

    Returns:
        T | None: The value of the chosen option, or None if the user
            cancelled or the entered number does not match any option.

    Raises:
        ValueError: If two options share the same number.

    Example:
        >>> options = [
        ...     Option("Shop", open_shop),
        ...     Spacer(),
        ...     Option("Games", open_games, position=5),
        ...     HiddenOption(666, easter_egg),
        ... ]
        >>> choice = ask_option("Choose a menu item: ", options)
        >>> if choice is not None:
        ...     choice()
    """
    by_number: dict[int, T] = {}
    hidden_numbers: list[int] = []
    visible_entries: list[tuple[int, str, Colors | None] | Spacer] = []

    next_auto = 1

    reserved: set[int] = {
        opt.pos for opt in options if isinstance(opt, Option) and opt.pos is not None
    }

    for opt in options:
        if isinstance(opt, Spacer):
            visible_entries.append(opt)
            continue

        if isinstance(opt, HiddenOption):
            number = opt.number
            hidden_numbers.append(number)
        else:
            if opt.pos is not None:
                number = opt.pos
            else:
                while next_auto in reserved:
                    next_auto += 1
                number = next_auto
                reserved.add(number)
                next_auto += 1

            visible_entries.append((number, opt.name, opt.color))

        if number in by_number:
            raise ValueError(f'Duplicate option number: {number}')
        by_number[number] = opt.value

    options_only = [e for e in visible_entries if not isinstance(e, Spacer)]
    options_only.sort()

    for entry in visible_entries:
        if isinstance(entry, Spacer):
            print('\n' * entry.lines, end='')
        else:
            number, name, color = entry
            print(f'{color or Colors.reset}{number}. {name}{Colors.reset}')

    print()  # blank line before the prompt

    max_visible = max((num for num, _, _ in options_only), default=0)

    value = ask_number(
        prompt,
        max=max_visible,
        allow_cancel=allow_cancel,
        cancel_on=cancel_on,
        hidden_values=hidden_numbers,
    )

    if value is None:
        return None

    return by_number[value]
