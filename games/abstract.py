from abc import ABC, abstractmethod
from typing import Any

from player import Player


class AbstractGame(ABC):
    def __init__(self, player: Player):
        self._player = player

    @abstractmethod
    def play(self, player: Player) -> Any:
        pass
