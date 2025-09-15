from contextlib import contextmanager
import sqlite3

class NotFoundError(Exception):
    pass

_db = None
class DB:
    def __init__(self, db_url, conn = None):
        self.conn = conn or sqlite3.connect(db_url)
        with self._session() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vms (
                    uid INTEGER PRIMARY KEY AUTOINCREMENT,
                    power_state TEXT NOT NULL
                )
            """)


    @contextmanager
    def _session(self):
        cursor = self.conn.cursor()
        try:
            yield cursor
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cursor.close()


    def create(self, power_state):
        with self._session() as cursor:
            cursor.execute(
                "INSERT INTO vms (power_state) VALUES (?)",
                (f"power_state: {power_state}",)
            )
            uid = cursor.lastrowid
        return {"uid": uid, "power_state": power_state}


    def read(self, uid):
        with self._session() as cursor:
            cursor.execute("SELECT uid, power_state FROM vms WHERE uid = ?", (uid,))
            row = cursor.fetchone()
            if row is None:
                raise NotFoundError(f"VM with uid {uid} not found")
            return {"uid": row[0], "power_state": row[1]}


    def update(self, uid, power_state):
        with self._session() as cursor:
            cursor.execute(
                "UPDATE vms SET power_state = ? WHERE uid = ?",
                (power_state, uid)
            )
            if cursor.rowcount == 0:
                raise NotFoundError(f"VM with uid {uid} not found")
        return {"uid": uid, "power_state": power_state}


    def delete(self, uid):
        with self._session() as cursor:
            cursor.execute("DELETE FROM vms WHERE uid = ?", (uid,))
            if cursor.rowcount == 0:
                raise NotFoundError(f"VM with uid {uid} not found")
        return True

def db(db_url=":memory:"):
    global _db
    if _db is None:
        _db = DB(db_url)
    return _db

