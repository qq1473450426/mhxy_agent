from __future__ import annotations

from typing import Optional

from .models import GameProfile, Task

LEVEL_MILESTONES = (20, 30, 40, 50, 60, 69, 89, 109, 129, 159, 175)


def five_open_state(count: int) -> str:
    count = max(0, min(count, 5))
    return {0: "STATE_0", 1: "STATE_1", 2: "STATE_3", 3: "STATE_5", 4: "STATE_7", 5: "STATE_9"}[count]


def rank_tasks(tasks: list[Task], available_hours: float) -> list[Task]:
    feasible = [t for t in tasks if t.hours > 0 and t.hours <= available_hours]
    stability_score = {"S": 5, "A": 4, "B": 3, "C": 2, "D": 1}
    return sorted(feasible, key=lambda t: (t.profit_per_hour, stability_score[t.stability]), reverse=True)


def daily_plan(profile: GameProfile, tasks: list[Task]) -> list[Task]:
    remaining = max(0.0, profile.online_hours)
    plan: list[Task] = []
    for task in rank_tasks(tasks, remaining):
        if task.hours <= remaining:
            plan.append(task)
            remaining -= task.hours
    return plan


def upgrade_payback(total_cost: float, incremental_profit_per_hour: float) -> Optional[float]:
    if total_cost < 0 or incremental_profit_per_hour <= 0:
        return None
    return total_cost / incremental_profit_per_hour


class StrategyEngine:
    """Deterministic strategy engine; LLM and executor adapters can be added later."""

    def create_daily_plan(self, profile: GameProfile, hours: Optional[float] = None) -> list[Task]:
        budget = profile.online_hours if hours is None else max(0.0, hours)
        tasks = [
            Task("稳定日常", 1.0, cash=120, reserve=30, items=20, cost=10, risk=2, stability="S"),
            Task("高收益活动", 1.0, cash=150, reserve=20, items=50, cost=20, risk=8, stability="A"),
            Task("成长任务", 0.5, cash=30, growth=60, cost=5, risk=3, stability="B"),
            Task("低稳定任务", 2.0, cash=250, items=50, cost=20, risk=60, stability="C"),
        ]
        return daily_plan(GameProfile(**{**profile.__dict__, "online_hours": budget}), tasks)
