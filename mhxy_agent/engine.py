from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, median, pstdev
from typing import Iterable

from .models import Character, GameProfile, STATES, Task

LEVEL_NODES = (20, 30, 40, 50, 60, 69, 89, 109, 129, 159, 175)

@dataclass
class Decision:
    action: str
    reason: str
    confidence: str

class StrategyEngine:
    def classify_level(self, level: int) -> str:
        if level < 20: return "0-20"
        for a, b in zip(LEVEL_NODES, LEVEL_NODES[1:]):
            if level < a: return f"{a-10 if a >= 30 else 20}-{a}"
            if level < b: return f"{a}-{b}"
        return "175+"

    def next_node(self, level: int) -> int | None:
        return next((n for n in LEVEL_NODES if n > level), None)

    def state_report(self, profile: GameProfile) -> dict:
        return {"state": profile.state, "state_name": STATES[profile.state], "accounts": profile.account_count,
                "level_stage": self.classify_level(max((c.level for c in profile.characters), default=0)),
                "next_level_node": self.next_node(max((c.level for c in profile.characters), default=0))}

    def rank_tasks(self, tasks: Iterable[Task], hours: float) -> list[Task]:
        budget = max(0.0, hours * 60)
        ranked = sorted(tasks, key=lambda t: (t.hourly_profit, t.expected_profit, t.success_rate), reverse=True)
        chosen: list[Task] = []
        used = 0.0
        for task in ranked:
            if used + task.minutes <= budget:
                chosen.append(task)
                used += task.minutes
        return chosen

    def upgrade_decision(self, current_level: int, investment: float, added_hourly_profit: float) -> Decision:
        if added_hourly_profit <= 0:
            return Decision("STAY", "升级后没有可量化的新增净收益，无法证明升级值得。", "A")
        payback = investment / added_hourly_profit
        if payback <= 20:
            return Decision("UPGRADE", f"预计回本 {payback:.1f} 小时，符合短周期投资逻辑。", "B")
        if payback <= 50:
            return Decision("CONDITIONAL", f"预计回本 {payback:.1f} 小时，需结合服务器物价和长期玩法确认。", "C")
        return Decision("STAY", f"预计回本 {payback:.1f} 小时，周期过长，当前更适合停级积累。", "C")

    def investment_priority(self, options: dict[str, tuple[float, float]]) -> list[tuple[str, float]]:
        """options: name -> (cost, expected hourly profit increase)."""
        result = []
        for name, (cost, benefit) in options.items():
            roi = benefit / cost if cost > 0 else 0.0
            result.append((name, roi))
        return sorted(result, key=lambda x: x[1], reverse=True)

    def task_report(self, task: Task) -> dict:
        return {"name": task.name, "expected_profit": round(task.expected_profit, 2),
                "hourly_profit": round(task.hourly_profit, 2), "stability": task.stability,
                "success_rate": task.success_rate, "cash": task.expected_cash,
                "tradable_items": task.expected_tradable_items, "reserve": task.reserve}

    def statistics(self, hourly_profits: list[float]) -> dict:
        if not hourly_profits:
            return {"sample_count": 0, "mean": 0, "median": 0, "min": 0, "max": 0, "stddev": 0, "confidence": "未知"}
        n = len(hourly_profits)
        confidence = "初步估计" if n < 10 else ("较可靠" if n < 50 else "可靠")
        return {"sample_count": n, "mean": round(mean(hourly_profits), 2), "median": round(median(hourly_profits), 2),
                "min": min(hourly_profits), "max": max(hourly_profits), "stddev": round(pstdev(hourly_profits), 2), "confidence": confidence}

    def initial_plan(self, profile: GameProfile, tasks: list[Task]) -> dict:
        stage = self.state_report(profile)
        selected = self.rank_tasks(tasks, profile.online_hours_daily)
        max_level = max((c.level for c in profile.characters), default=0)
        return {
            "observation": "基于当前 Game Profile 生成条件化方案；未知字段不做假设。",
            "current_state": stage,
            "goal": "长期稳定净收益最大化",
            "constraints": {"daily_hours": profile.online_hours_daily, "accounts": profile.account_count},
            "today": [self.task_report(t) for t in selected],
            "decision": "优先单位时间期望净收益最高且稳定性可接受的任务。",
            "now": selected[0].name if selected else "补充任务数据",
            "next": selected[1].name if len(selected) > 1 else "完成当前任务后重新规划",
            "later": f"复盘 {self.next_node(max_level) or 175} 级节点",
            "do_not": "不要在缺少成本/收益数据时盲目升级或重资产投入",
            "confidence": "B" if profile.server != "未知" and profile.version != "未知" else "C"
        }

DEFAULT_TASKS = [
    Task("师门", 20, cash=50000, reserve=80000, success_rate=0.99, consumption=3000),
    Task("抓鬼", 60, cash=120000, reserve=70000, tradable_items=30000, success_rate=0.97, consumption=8000),
    Task("副本", 50, cash=90000, reserve=60000, tradable_items=70000, success_rate=0.92, consumption=9000, risk_cost=3000),
    Task("日常活动", 40, cash=70000, reserve=50000, tradable_items=90000, success_rate=0.85, consumption=7000, risk_cost=5000),
]
