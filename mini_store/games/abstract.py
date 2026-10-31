from abc import ABC, abstractmethod

from mini_store.context import GameContext


class AbstractGame(ABC):
    def __init__(self, ctx: GameContext):
        self._ctx = ctx
        self._player = ctx.player

    @abstractmethod
    def play(self) -> None:
        pass
