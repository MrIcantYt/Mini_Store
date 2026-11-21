from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple


class ProgressRange(NamedTuple):
    min: int
    max: int


@dataclass(frozen=True, slots=True)
class Contract:
    text: str
    progress_range: ProgressRange
    reward_base: int


class ContractKind(Enum):
    BLACKJACK_ROUNDS = Contract('Сыграть {target} раундов в Блекджек', ProgressRange(3, 7), 150)
    BLACKJACK_SCORE = Contract('Набрать ровно 21 очко {target} раз(а)', ProgressRange(1, 2), 300)
    ONCE_SPLIT = Contract('Разделить карты (Сплит) хотя бы {target} раз', ProgressRange(1, 1), 250)
    CRAPS_SCORE = Contract(
        'Выбить сумму 12 в Костях (6 и 6) {target} раз(а)', ProgressRange(1, 1), 500
    )
