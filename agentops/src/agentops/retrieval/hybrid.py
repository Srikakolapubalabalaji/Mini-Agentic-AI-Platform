import json
import sqlite3
from pathlib import Path


class HybridRetriever:
    """
    Mock hybrid retriever using SQLite FTS5 for Lexical,
    and a mocked semantic search (since Qdrant requires heavy deps/running server).
    """

    def __init__(self, runbooks_path: str):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self._init_fts(runbooks_path)

    def _init_fts(self, path_str: str):
        self.conn.execute("CREATE VIRTUAL TABLE runbooks USING fts5(id, service, title, content);")

        path = Path(path_str)
        if not path.exists():
            return

        with open(path) as f:
            data = json.load(f)

        for rb in data:
            self.conn.execute(
                "INSERT INTO runbooks (id, service, title, content) VALUES (?, ?, ?, ?)",
                (rb["id"], rb["service"], rb["title"], rb["content"]),
            )
        self.conn.commit()

    def search(self, query: str, service: str) -> list[dict]:
        # Simple FTS match on the service.
        # In a real system, RRF would combine this with Qdrant vector scores.
        cur = self.conn.cursor()
        cur.execute("SELECT id, title, content FROM runbooks WHERE service = ?", (service,))
        results = []
        for row in cur.fetchall():
            results.append({"id": row[0], "title": row[1], "content": row[2]})
        return results
