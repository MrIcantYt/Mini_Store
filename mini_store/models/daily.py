from dataclasses import dataclass, field
from datetime import date

from mini_store.utils import today

from .contract import ContractKind


@dataclass(slots=True)
class DailyContract:
    kind: ContractKind
    target: int
    progress: int = 0
    last_update_date: date = field(default_factory=today)
    completed: bool = False

    @property
    def text(self) -> str:
        return self.kind.value.text.format(target=self.target)

    @property
    def reward(self) -> int:
        return self.target * self.kind.value.reward_base

    def update_progress(self, kind: ContractKind, amount: int = 1) -> bool:
        if kind is not self.kind or self.completed:
            return False

        self.progress = min(self.progress + amount, self.target)
        return True


@dataclass(slots=True)
class DailyContext:
    contract: DailyContract | None = None
    discount_item_id: int | None = None

    def update_contract_progress(self, kind: ContractKind, amount: int = 1) -> bool:
        """Syntax sugar for:
        ```py
        if (contract := self._ctx.daily.contract) is not None:
            contract.update_progress(kind, amount)
        ```
        """
        if self.contract is None:
            return False
        return self.contract.update_progress(kind, amount)
