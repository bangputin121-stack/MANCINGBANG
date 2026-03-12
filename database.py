import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List


class Database:
    def __init__(self, db_path: str = "fishing_game.db"):
        self.db_path = db_path
        self.init_db()

    def get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_conn()
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            coins INTEGER DEFAULT 500,
            gems INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            vip_level INTEGER DEFAULT 0,
            vip_expires TEXT,
            rod_level INTEGER DEFAULT 1,
            bait_level INTEGER DEFAULT 1,
            boat_level INTEGER DEFAULT 0,
            current_map TEXT DEFAULT 'sungai',
            active_boost TEXT DEFAULT NULL,
            boost_expires TEXT DEFAULT NULL,
            last_fishing TEXT DEFAULT NULL,
            last_daily TEXT DEFAULT NULL,
            total_fish INTEGER DEFAULT 0,
            registered_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS fish_bag (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            fish_id TEXT,
            fish_name TEXT,
            fish_rarity TEXT,
            fish_weight REAL,
            fish_value INTEGER,
            caught_at TEXT DEFAULT CURRENT_TIMESTAMP,
            map_caught TEXT,
            is_favorite INTEGER DEFAULT 0,
            is_sold INTEGER DEFAULT 0
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS fishing_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            result TEXT,
            fish_name TEXT,
            fish_rarity TEXT,
            fish_weight REAL,
            coins_earned INTEGER DEFAULT 0,
            map_name TEXT,
            caught_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS market_listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER,
            fish_bag_id INTEGER,
            fish_name TEXT,
            fish_rarity TEXT,
            fish_weight REAL,
            price INTEGER,
            listed_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_sold INTEGER DEFAULT 0
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,
            amount INTEGER,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS collection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            fish_id TEXT,
            fish_name TEXT,
            first_caught TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, fish_id)
        )''')

        conn.commit()
        conn.close()

    # ── Player methods ──────────────────────────────────────────────
    def get_player(self, user_id: int) -> Optional[Dict]:
        conn = self.get_conn()
        row = conn.execute("SELECT * FROM players WHERE user_id=?", (user_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def register_player(self, user_id: int, username: str, full_name: str) -> bool:
        if self.get_player(user_id):
            return False
        conn = self.get_conn()
        conn.execute(
            "INSERT INTO players (user_id, username, full_name) VALUES (?,?,?)",
            (user_id, username or "", full_name or "Player")
        )
        conn.commit()
        conn.close()
        return True

    def update_player(self, user_id: int, **kwargs):
        if not kwargs:
            return
        sets = ", ".join(f"{k}=?" for k in kwargs)
        vals = list(kwargs.values()) + [user_id]
        conn = self.get_conn()
        conn.execute(f"UPDATE players SET {sets} WHERE user_id=?", vals)
        conn.commit()
        conn.close()

    def add_coins(self, user_id: int, amount: int):
        conn = self.get_conn()
        conn.execute("UPDATE players SET coins=coins+? WHERE user_id=?", (amount, user_id))
        conn.commit()
        conn.close()

    def add_xp(self, user_id: int, xp: int):
        player = self.get_player(user_id)
        if not player:
            return
        new_xp = player['xp'] + xp
        new_level = player['level']
        xp_needed = new_level * 100
        while new_xp >= xp_needed:
            new_xp -= xp_needed
            new_level += 1
            xp_needed = new_level * 100
        conn = self.get_conn()
        conn.execute("UPDATE players SET xp=?, level=? WHERE user_id=?", (new_xp, new_level, user_id))
        conn.commit()
        conn.close()
        return new_level > player['level'], new_level  # leveled_up, new_level

    # ── Fish bag methods ─────────────────────────────────────────────
    def add_fish(self, user_id: int, fish: Dict) -> int:
        conn = self.get_conn()
        cur = conn.execute(
            "INSERT INTO fish_bag (user_id,fish_id,fish_name,fish_rarity,fish_weight,fish_value,map_caught) VALUES (?,?,?,?,?,?,?)",
            (user_id, fish['id'], fish['name'], fish['rarity'], fish['weight'], fish['value'], fish.get('map', ''))
        )
        fish_bag_id = cur.lastrowid
        conn.execute("UPDATE players SET total_fish=total_fish+1 WHERE user_id=?", (user_id,))
        conn.commit()
        conn.close()
        # Add to collection
        self.add_collection(user_id, fish['id'], fish['name'])
        return fish_bag_id

    def get_bag(self, user_id: int, page: int = 0, per_page: int = 10) -> List[Dict]:
        conn = self.get_conn()
        rows = conn.execute(
            "SELECT * FROM fish_bag WHERE user_id=? AND is_sold=0 ORDER BY caught_at DESC LIMIT ? OFFSET ?",
            (user_id, per_page, page * per_page)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_bag_count(self, user_id: int) -> int:
        conn = self.get_conn()
        count = conn.execute("SELECT COUNT(*) FROM fish_bag WHERE user_id=? AND is_sold=0", (user_id,)).fetchone()[0]
        conn.close()
        return count

    def get_favorites(self, user_id: int) -> List[Dict]:
        conn = self.get_conn()
        rows = conn.execute(
            "SELECT * FROM fish_bag WHERE user_id=? AND is_favorite=1 AND is_sold=0",
            (user_id,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def toggle_favorite(self, user_id: int, fish_bag_id: int) -> bool:
        conn = self.get_conn()
        row = conn.execute("SELECT is_favorite FROM fish_bag WHERE id=? AND user_id=?", (fish_bag_id, user_id)).fetchone()
        if not row:
            conn.close()
            return False
        new_val = 0 if row[0] else 1
        conn.execute("UPDATE fish_bag SET is_favorite=? WHERE id=?", (new_val, fish_bag_id))
        conn.commit()
        conn.close()
        return bool(new_val)

    # ── History ──────────────────────────────────────────────────────
    def add_history(self, user_id: int, result: str, fish_name: str = None,
                    fish_rarity: str = None, fish_weight: float = 0,
                    coins_earned: int = 0, map_name: str = ""):
        conn = self.get_conn()
        conn.execute(
            "INSERT INTO fishing_history (user_id,result,fish_name,fish_rarity,fish_weight,coins_earned,map_name) VALUES (?,?,?,?,?,?,?)",
            (user_id, result, fish_name, fish_rarity, fish_weight, coins_earned, map_name)
        )
        conn.commit()
        conn.close()

    def get_history(self, user_id: int, limit: int = 20) -> List[Dict]:
        conn = self.get_conn()
        rows = conn.execute(
            "SELECT * FROM fishing_history WHERE user_id=? ORDER BY caught_at DESC LIMIT ?",
            (user_id, limit)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ── Market ───────────────────────────────────────────────────────
    def list_market(self, seller_id: int, fish_bag_id: int, price: int) -> bool:
        conn = self.get_conn()
        fish = conn.execute("SELECT * FROM fish_bag WHERE id=? AND user_id=? AND is_sold=0", (fish_bag_id, seller_id)).fetchone()
        if not fish:
            conn.close()
            return False
        conn.execute(
            "INSERT INTO market_listings (seller_id,fish_bag_id,fish_name,fish_rarity,fish_weight,price) VALUES (?,?,?,?,?,?)",
            (seller_id, fish_bag_id, fish['fish_name'], fish['fish_rarity'], fish['fish_weight'], price)
        )
        conn.execute("UPDATE fish_bag SET is_sold=2 WHERE id=?", (fish_bag_id,))  # 2=listed
        conn.commit()
        conn.close()
        return True

    def get_market_listings(self, limit: int = 20) -> List[Dict]:
        conn = self.get_conn()
        rows = conn.execute(
            "SELECT * FROM market_listings WHERE is_sold=0 ORDER BY listed_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def buy_from_market(self, buyer_id: int, listing_id: int) -> Dict:
        conn = self.get_conn()
        listing = conn.execute("SELECT * FROM market_listings WHERE id=? AND is_sold=0", (listing_id,)).fetchone()
        if not listing:
            conn.close()
            return {'success': False, 'reason': 'Listing tidak ditemukan'}
        listing = dict(listing)
        if listing['seller_id'] == buyer_id:
            conn.close()
            return {'success': False, 'reason': 'Tidak bisa membeli ikan sendiri'}
        buyer = conn.execute("SELECT coins FROM players WHERE user_id=?", (buyer_id,)).fetchone()
        if not buyer or buyer['coins'] < listing['price']:
            conn.close()
            return {'success': False, 'reason': 'Koin tidak cukup'}
        # Process purchase
        conn.execute("UPDATE players SET coins=coins-? WHERE user_id=?", (listing['price'], buyer_id))
        conn.execute("UPDATE players SET coins=coins+? WHERE user_id=?", (listing['price'], listing['seller_id']))
        conn.execute("UPDATE market_listings SET is_sold=1 WHERE id=?", (listing_id,))
        conn.execute("UPDATE fish_bag SET user_id=?, is_sold=0 WHERE id=?", (buyer_id, listing['fish_bag_id']))
        conn.commit()
        conn.close()
        return {'success': True, 'listing': listing}

    # ── Collection ───────────────────────────────────────────────────
    def add_collection(self, user_id: int, fish_id: str, fish_name: str):
        conn = self.get_conn()
        conn.execute(
            "INSERT OR IGNORE INTO collection (user_id,fish_id,fish_name) VALUES (?,?,?)",
            (user_id, fish_id, fish_name)
        )
        conn.commit()
        conn.close()

    def get_collection(self, user_id: int) -> List[Dict]:
        conn = self.get_conn()
        rows = conn.execute("SELECT * FROM collection WHERE user_id=? ORDER BY first_caught", (user_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ── Leaderboard ──────────────────────────────────────────────────
    def get_leaderboard(self, sort_by: str = "total_fish", limit: int = 10) -> List[Dict]:
        allowed = ['total_fish', 'level', 'coins', 'xp']
        if sort_by not in allowed:
            sort_by = 'total_fish'
        conn = self.get_conn()
        rows = conn.execute(
            f"SELECT user_id, full_name, username, level, total_fish, coins, xp FROM players ORDER BY {sort_by} DESC LIMIT ?",
            (limit,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
