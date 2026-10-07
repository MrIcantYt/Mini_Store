from .abstract import AbstractGame, Player


# Use it's a template for creating new games:
# Copy this class into new file and rename it to create a new game.
class __TemplateGame(AbstractGame):
    def __init__(self, player: Player):
        self._player = player

    def play(self) -> None:
        pass
