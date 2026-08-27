from dataclasses import dataclass, field
from typing import Literal

@dataclass
class Account:
    name: str = ""
    school: str = "未知"
    level: int = 0
    cash: float = 0.0
    reserve: float = 0.0
    hp: int = 0
    mp: int = 0
    status: str = "idle"

@dataclass
class GameProfile:
    server: str = "未知"
    version: str = "未知"
    online_hours: float = 4.0
    accounts: list[Account] = field(default_factory=list)
    total_investment: float = 0.0
    current_assets: float = 0.0
    emergency_fund: float = 0.0

    @property
    def account_count(self) -> int:
        return len(self.accounts)

    @property
    def average_level(self) -> float:
        return sum(a.level for a in self.accounts) / len(self.accounts) if self.accounts else 0.0

@dataclass(frozen=True)
class Task:
    name: str
    hours: float
    cash: float = 0.0
    reserve: float = 0.0
    items: float = 0.0
    growth: float = 0.0
    cost: float = 0.0
    risk: float = 0.0
    stability: Literal["S", "A", "B", "C", "D"] = "B"

    @property
    def net_profit(self) -> float:
        return self.cash + self.reserve + self.items + self.growth - self.cost - self.risk

    @property
    def profit_per_hour(self) -> float:
        return self.net_profit / self.hours if self.hours > 0 else 0.0
