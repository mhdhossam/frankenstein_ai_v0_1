# Memory placeholder
import sqlite3
import time
import os

DB_PATH = os.getenv("FRANKENSTEIN_DB","frankenstein_memory.sqlite")

class Memory:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self._init()

    def _init(self):
        cur = self.conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS interactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts INTEGER,
            prompt TEXT,
            response TEXT
        );""")
        self.conn.commit()

    def save_interaction(self, prompt:str, response:str):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO interactions(ts,prompt,response) VALUES(?,?,?)",
                    (int(time.time()), prompt, response))
        self.conn.commit()

    def search(self, query:str, limit:int=5):
        cur = self.conn.cursor()
        q = f"%{query[:60]}%"
        cur.execute("SELECT prompt,response,ts FROM interactions WHERE prompt LIKE ? OR response LIKE ? ORDER BY ts DESC LIMIT ?",
                    (q,q,limit))
        rows = cur.fetchall()
        return [{"prompt":r[0],"response":r[1],"ts":r[2]} for r in rows]
