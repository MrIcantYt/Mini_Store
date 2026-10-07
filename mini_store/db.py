import sqlite3
from abc import ABC, abstractmethod
from os import path
from warnings import deprecated

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


@deprecated('SqliteDataBase is deprecated. Use JsonDataBase instead.')
class SqliteDataBase(AbstractDataBase):
    def __init__(self, db_path: str = 'game.db'):
        self.path = db_path

    def init_db(self):
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                    balance             INTEGER NOT NULL DEFAULT 0,
                    balance_multiplier  INTEGER NOT NULL DEFAULT 1,
                    xp                  INTEGER NOT NULL DEFAULT 0,
                    xp_multiplier       INTEGER NOT NULL DEFAULT 1,
                    lvl                 INTEGER NOT NULL DEFAULT 1 CHECK (lvl >= 1),
                    promo_used          BOOLEAN NOT NULL DEFAULT 0,
                    lucky_amulet        BOOLEAN NOT NULL DEFAULT 0,
                    secret_used         BOOLEAN NOT NULL DEFAULT 0,
                    bought              INTEGER NOT NULL DEFAULT 0,
                    mining_lvl          INTEGER NOT NULL DEFAULT 0,
                    potion_luck         BOOLEAN NOT NULL DEFAULT 0,
                    lucky_ticket        BOOLEAN NOT NULL DEFAULT 0,
                    mining_boost        BOOLEAN NOT NULL DEFAULT 0,
                    buy_num_boost       INTEGER NOT NULL DEFAULT 0,
                    business            BOOLEAN NOT NULL DEFAULT 0,
                    reset_num           INTEGER NOT NULL DEFAULT 0,
                    secret_case         INTEGER NOT NULL DEFAULT 0,
                    quest_id            INTEGER NOT NULL DEFAULT 1,
                    quest_progress      INTEGER NOT NULL DEFAULT 0,
                    rebirths            INTEGER NOT NULL DEFAULT 0
                );
            """)

            conn.commit()

    def save_player(self, player: Player) -> None:
        data = player.to_row()
        columns = ', '.join(f'{col} = ?' for col in data)

        with sqlite3.connect(self.path) as conn:
            conn.execute(
                f'UPDATE players SET {columns} WHERE id = ?',
                (*data.values(), player.id),
            )

    def get_player_by_id(self, player_id: int) -> Player | None:
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                'SELECT * FROM players WHERE id = ?', (player_id,)
            ).fetchone()

        return Player.from_row(row) if row else None

    def get_all_players(self) -> list[Player]:
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute('SELECT * FROM players').fetchall()

        return [Player.from_row(row) for row in rows]


class JsonDataBase(AbstractDataBase):
    def __init__(self, db_path: str = 'game.json') -> None:
        self.path = db_path
        self.json = SignedJson(db_path)

    def init_db(self) -> None:
        if not path.exists(self.path):
            self.json.dump({'players': []})

    def save_player(self, player: Player) -> None:
        data = self.json.load(False)
        players = data['players']
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
        for p in data['players']:
            if p['id'] == player_id:
                return Player.from_dict(p)
        return None

    def get_all_players(self) -> list[Player]:
        data = self.json.load()
        return [Player.from_dict(p) for p in data['players']]
