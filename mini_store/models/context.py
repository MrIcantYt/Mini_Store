from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mini_store.db import AbstractDataBase

from .daily import DailyContext
from .player import Player


@dataclass(slots=True)
class GameContext:
    player: Player
    db: AbstractDataBase
    daily: DailyContext
