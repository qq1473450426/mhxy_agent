from __future__ import annotations

import sqlite3
from pathlib import Path


class Database:
    def __init__(self, path: str = "data/mhxy_agent.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.initialize()

    def initialize(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                level INTEGER NOT NULL DEFAULT 0,
                school TEXT NOT NULL DEFAULT '',
                enabled INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS strategy_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                decision TEXT NOT NULL,
                reason TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS action_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                stage TEXT NOT NULL,
                action TEXT NOT NULL,
                result TEXT NOT NULL DEFAULT ''
            );
            """
        )
        self.connection.commit()

    def add_account(self, name: str, level: int = 0, school: str = "") -> int:
        cursor = self.connection.execute(
            "INSERT INTO accounts(name, level, school) VALUES (?, ?, ?)",
            (name, level, school),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def list_accounts(self) -> list[tuple]:
        return self.connection.execute(
            "SELECT id, name, level, school, enabled FROM accounts ORDER BY id"
        ).fetchall()

    def log_action(self, stage: str, action: str, result: str = "") -> None:
        self.connection.execute(
            "INSERT INTO action_logs(stage, action, result) VALUES (?, ?, ?)",
            (stage, action, result),
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()
