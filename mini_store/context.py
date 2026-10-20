from dataclasses import dataclass

from mini_store.db import AbstractDataBase
from mini_store.player import Daily, Player


@dataclass
class GameContext:
    player: Player
    db: AbstractDataBase
    daily: Daily
