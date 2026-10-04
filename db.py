import sqlite3
from abc import ABC, abstractmethod

from player import Player


class AbstractDataBase(ABC):
    db_path: str

    @abstractmethod
    def init_db(self) -> None:
        pass

    @abstractmethod
    def save_player(self, player: Player) -> None:
        pass

    @abstractmethod
    def get_player_by_id(self, player_id: int) -> Player | None:
        pass


class SqliteDataBase(AbstractDataBase):
    def __init__(self, db_path: str = 'game.db'):
        self.db_path = db_path

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
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
                    rebirths            INTEGER NOT NULL DEFAULT 0
                );
            """)

            conn.commit()

    def get_player_by_id(self, player_id: int) -> Player | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute('SELECT * FROM players WHERE id = ?', (player_id,)).fetchone()

        return Player.from_row(row) if row else None

    def save_player(self, player: Player) -> None:
        data = player.to_row()
        columns = ', '.join(f'{col} = ?' for col in data)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                f'UPDATE players SET {columns} WHERE id = ?',
                (*data.values(), player.id),
            )


class JsonDataBase(AbstractDataBase):
    def __init__(self, db_path: str = 'game.json') -> None:
        self.db_path = db_path

    def init_db(self) -> None:
        pass

    def save_player(self, player: Player) -> None:
        pass

    def get_player_by_id(self, player_id: int) -> Player | None:
        pass
