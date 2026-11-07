from dataclasses import dataclass
from datetime import date

from mini_store.db import AbstractDataBase
from mini_store.player import Player


# TODO: combine all fileds except discount_item_id in Contact class
@dataclass(slots=True)
class Daily:
    contract: str | None = None
    target: int = 0
    progress: int = 0
    reward: int = 0
    last_update: date | None = None
    completed: bool = False
    discount_item_id: int | None = None

    def register_daily(self, keyword: str) -> None:
        if self.contract and keyword in self.contract and not self.completed:
            self.progress += 1


@dataclass(slots=True)
class GameContext:
    player: Player
    db: AbstractDataBase
    daily: Daily
