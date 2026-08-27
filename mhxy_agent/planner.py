from __future__ import annotations

from datetime import date
from .engine import DEFAULT_TASKS, StrategyEngine
from .models import Character, GameProfile

class Planner:
    def __init__(self) -> None:
        self.engine = StrategyEngine()

    def build_profile(self, data: dict) -> GameProfile:
        chars = [Character(**item) for item in data.get("characters", [])]
        return GameProfile(
            server=data.get("server", "未知"),
            server_open_date=data.get("server_open_date", "未知"),
            current_date=data.get("current_date", date.today().isoformat()),
            version=data.get("version", "未知"),
            online_hours_daily=float(data.get("online_hours_daily", 4)),
            online_hours_weekly=float(data.get("online_hours_weekly", 28)),
            total_investment=float(data.get("total_investment", 0)),
            current_assets=float(data.get("current_assets", 0)),
            available_cash=float(data.get("available_cash", 0)),
            reserve=float(data.get("reserve", 0)),
            unliquidated_items=float(data.get("unliquidated_items", 0)),
            characters=chars,
        )

    def run(self, profile: GameProfile, tasks=None) -> dict:
        return self.engine.initial_plan(profile, list(tasks or DEFAULT_TASKS))
