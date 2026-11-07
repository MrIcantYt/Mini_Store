from abc import ABC, abstractmethod
from os import path

from mini_store.config import config
from mini_store.context import Daily
from mini_store.player import Player
from mini_store.sign import SignedJson


class AbstractDataBase(ABC):
    path: str

    @abstractmethod
    def init_db(self) -> None:
        pass

    @abstractmethod
    def save_player(self, player: Player) -> None:
        pass

    @abstractmethod
    def reset_player(self, player: Player) -> Player:
        """Reset player to default state and return the resetted player object."""

    @abstractmethod
    def get_player_by_id(self, player_id: int) -> Player | None:
        pass

    @abstractmethod
    def get_all_players(self) -> list[Player]:
        pass


class JsonDataBase(AbstractDataBase):
    def __init__(self, db_path: str = 'game.json') -> None:
        self.path = db_path
        self.json = SignedJson(db_path, check_sign=not config.is_debug)

    def init_db(self) -> None:
        if not path.exists(self.path):
            self.json.dump({'players': []})

    def save_player(self, player: Player) -> None:
        data = self.json.load(False)
        players = data.get('players')

        if not players:
            players = data['players'] = []

        record = player.to_dict()

        for i, p in enumerate(players):
            if p['id'] == player.id:
                players[i] = record
                break
        else:
            players.append(record)

        self.json.dump(data)

    def reset_player(self, daily: Daily, player: Player) -> tuple[Player, Daily]:
        """Reset player to default state and return the resetted player and daily objects."""
        return Player(id=player.id), Daily(id=daily.id)

    def get_player_by_id(self, player_id: int) -> Player | None:
        data = self.json.load()

        if (players := data.get('players')) is None:
            return

        for p in players:
            if p['id'] == player_id:
                return Player.from_dict(p)
        return

    def get_all_players(self) -> list[Player]:
        data = self.json.load()

        if (players := data.get('players')) is None:
            return []

        return [Player.from_dict(p) for p in players]
