from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AppConfig:
    game_window_keyword: str = "梦幻西游"
    mode: str = "simulation"
    database_path: str = "data/mhxy_agent.db"

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            game_window_keyword=os.getenv("MHXY_WINDOW_KEYWORD", cls.game_window_keyword),
            mode=os.getenv("MHXY_MODE", cls.mode),
            database_path=os.getenv("MHXY_DATABASE", cls.database_path),
        )
