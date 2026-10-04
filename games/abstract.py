from abc import ABC, abstractmethod
from typing import Any

from player import Player


class AbstractGame(ABC):
    @abstractmethod
    def play(self, player: Player) -> Any:
        pass
