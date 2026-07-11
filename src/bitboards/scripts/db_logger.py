import sqlite3
from pathlib import Path

DB_PATH = Path("./src/bitboards/data/chess_database.db")

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT,
            move_number INTEGER,
            position_hash TEXT,
            result REAL
        )
    ''')
    conn.commit()
    conn.close()

def log_game_to_db(game_id, game_states, final_result):
    conn = sqlite3.connect(DB_PATH, timeout=60.0)
    cursor = conn.cursor()

    for move_num, pos_hash in enumerate(game_states):
        cursor.execute('''
            INSERT INTO game_states (game_id, move_number, position_hash, result)
            VALUES (?, ?, ?, ?)
        ''', (game_id, move_num, str(pos_hash), final_result))
    conn.commit()
    conn.close()