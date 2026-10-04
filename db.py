import sqlite3

from player import Player


class DataBase:
    def __init__(self, db_path: str = "game.db"):
        self.db_path = db_path

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    balance INTEGER DEFAULT 0,
                    balance_x2 BOOLEAN DEFAULT 0,
                    promo_used BOOLEAN DEFAULT 0,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    xp_x2 BOOLEAN DEFAULT 0,
                    lucky_amulet BOOLEAN DEFAULT 0,
                    secret_used BOOLEAN DEFAULT 0,
                    bought INTEGER DEFAULT 0,
                    mining_lvl INTEGER DEFAULT 0,
                    potion_luck BOOLEAN DEFAULT 0,
                    lucky_ticket BOOLEAN DEFAULT 0,
                    mining_boost BOOLEAN DEFAULT 0,
                    buy_num_boost INTEGER DEFAULT 0,
                    business BOOLEAN DEFAULT 0,
                    rebirths INTEGER DEFAULT 0
                )
            """)

            conn.commit()

    def get_player_by_id(self, player_id: int) -> Player:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM players WHERE id = ?", (player_id,))
            row = cursor.fetchone()
            if not row:
                cursor.execute("SELECT COUNT(*) FROM users")
                cursor.execute("INSERT INTO users (id) VALUES (?)", (player_id,))
                conn.commit()
                return self.get_player_by_id(player_id)

            return row

    def save_player(self, player: Player):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE users SET
                    balance = ?, balance_x2 = ?, promo_used = ?, xp = ?, level = ?,
                    xp_x2 = ?, lucky_amulet = ?, secret_used = ?, bought = ?, mining_lvl = ?,
                    potion_luck = ?, lucky_ticket = ?, mining_boost = ?, buy_num_boost = ?, business = ?
                WHERE id = 1
            """,
                (
                    player.balance,
                    int(player.balance_x2),
                    int(player.promo_used),
                    player._xp,
                    player.lvl,
                    int(player.xp_x2),
                    int(player.lucky_amulet),
                    int(player.secret_used),
                    player.bought,
                    player.mining_lvl,
                    int(player.potion_luck),
                    int(player.lucky_ticket),
                    int(player.mining_boost),
                    player.buy_num_boost,
                    int(player.business),
                ),
            )

            conn.commit()
