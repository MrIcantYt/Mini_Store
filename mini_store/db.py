from abc import ABC, abstractmethod
from os import PathLike
from pathlib import Path

from mini_store.config import CONFIG
from mini_store.models import Player
from mini_store.sign import SignedJson


class AbstractDataBase(ABC):
    path: Path

    @abstractmethod
    def init_db(self) -> bool:
        pass

    @abstractmethod
    def save_player(self, player: Player) -> None:
        pass

    @abstractmethod
    def reset_player(self, player: Player) -> Player:
        pass

    @abstractmethod
    def get_player_by_id(self, player_id: int) -> Player | None:
        pass

    @abstractmethod
    def get_all_players(self) -> list[Player]:
        pass


class JsonDataBase(AbstractDataBase):
    def __init__(self, db_path: str | PathLike[str] = Path('game.json')) -> None:
        self.path = Path(db_path)
        self.json = SignedJson(self.path, check_sign=not CONFIG.is_debug)

    def init_db(self) -> bool:
        """Initialize the database.

        Return:
            bool: `False` if the database was created, `True` otherwise.
        """
        if not self.path.exists():
            self.json.dump({'players': []})
            return False
        return True

    def save_player(self, player: Player) -> None:
        data = self.json.load()
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

    def reset_player(self, player: Player) -> Player:
        return Player(id=player.id)

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
