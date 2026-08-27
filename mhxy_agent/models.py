from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

STATES = {
    0: "单号起步", 1: "单号成长", 2: "准备第二号", 3: "双开", 4: "准备第三号",
    5: "三开", 6: "准备第四号", 7: "四开", 8: "五开准备", 9: "五开基础成型",
    10: "五开稳定运营", 11: "五开收益优化", 12: "长期搬砖",
}

@dataclass
class Character:
    name: str = "未知"
    school: str = "未知"
    level: int = 0
    skills: str = "未知"
    cultivation: str = "未知"
    equipment: str = "未知"
    weapon: str = "未知"
    pets: str = "未知"
    magic_weapons: str = "未知"
    cash: float = 0.0
    reserve: float = 0.0
    stamina: float = 0.0
    vitality: float = 0.0
    task: str = "未知"
    map_name: str = "未知"
    status: str = "未知"

@dataclass
class GameProfile:
    server: str = "未知"
    server_open_date: str = "未知"
    current_date: str = "未知"
    version: str = "未知"
    online_hours_daily: float = 4.0
    online_hours_weekly: float = 28.0
    total_investment: float = 0.0
    current_assets: float = 0.0
    available_cash: float = 0.0
    reserve: float = 0.0
    unliquidated_items: float = 0.0
    characters: list[Character] = field(default_factory=list)

    @property
    def account_count(self) -> int:
        return len(self.characters)

    @property
    def state(self) -> int:
        n = self.account_count
        if n <= 0: return 0
        if n == 1: return 1
        if n == 2: return 3
        if n == 3: return 5
        if n == 4: return 7
        return 10

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["state"] = self.state
        data["state_name"] = STATES[self.state]
        return data

@dataclass
class Task:
    name: str
    minutes: float
    cash: float = 0.0
    reserve: float = 0.0
    tradable_items: float = 0.0
    nontradable_items: float = 0.0
    growth_value: float = 0.0
    consumption: float = 0.0
    risk_cost: float = 0.0
    success_rate: float = 1.0
    operation_cost: float = 0.0
    prerequisites: str = ""

    @property
    def expected_cash(self) -> float:
        return self.cash * max(0.0, min(1.0, self.success_rate))

    @property
    def expected_tradable_items(self) -> float:
        return self.tradable_items * max(0.0, min(1.0, self.success_rate))

    @property
    def expected_profit(self) -> float:
        return self.expected_cash + self.expected_tradable_items + self.growth_value * max(0.0, min(1.0, self.success_rate)) - self.consumption - self.risk_cost - self.operation_cost

    @property
    def hourly_profit(self) -> float:
        return self.expected_profit / (self.minutes / 60.0) if self.minutes > 0 else 0.0

    @property
    def stability(self) -> str:
        score = self.success_rate * 100 - min(30, self.risk_cost / max(1.0, self.expected_profit + 1))
        if score >= 90: return "S"
        if score >= 75: return "A"
        if score >= 55: return "B"
        if score >= 35: return "C"
        return "D"

@dataclass
class DailyRecord:
    start_capital: float
    end_capital: float
    cash_profit: float
    item_profit: float
    reserve_profit: float
    growth_profit: float
    consumption: float
    hours: float

    @property
    def net_profit(self) -> float:
        return self.cash_profit + self.item_profit + self.growth_profit - self.consumption

    @property
    def net_profit_per_hour(self) -> float:
        return self.net_profit / self.hours if self.hours > 0 else 0.0
