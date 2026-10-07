from abc import ABC, abstractmethod

from mini_store.player import Player


class AbstractGame(ABC):
    def __init__(self, player: Player):
        self._player = player

    @abstractmethod
    def play(self) -> None:
        pass
