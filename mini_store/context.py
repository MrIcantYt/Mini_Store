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


@dataclass(slots=True)
class GameContext:
    player: Player
    db: AbstractDataBase
    daily: Daily
