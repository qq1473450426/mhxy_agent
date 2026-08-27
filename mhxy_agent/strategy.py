from .models import GameProfile, Task

LEVEL_MILESTONES = (20, 30, 40, 50, 60, 69, 89, 109, 129, 159, 175)

def five_open_state(count: int) -> str:
    states = {0: "STATE_0", 1: "STATE_1", 2: "STATE_3", 3: "STATE_5", 4: "STATE_7", 5: "STATE_9"}
    return states.get(min(count, 5), "STATE_9")

def rank_tasks(tasks: list[Task], available_hours: float) -> list[Task]:
    feasible = [t for t in tasks if t.hours <= available_hours]
    return sorted(feasible, key=lambda t: (t.profit_per_hour, t.stability), reverse=True)

def daily_plan(profile: GameProfile, tasks: list[Task]) -> list[Task]:
    remaining = max(0.0, profile.online_hours)
    plan = []
    for task in rank_tasks(tasks, remaining):
        if task.hours <= remaining:
            plan.append(task)
            remaining -= task.hours
    return plan

def upgrade_payback(total_cost: float, incremental_profit_per_hour: float) -> float | None:
    if incremental_profit_per_hour <= 0:
        return None
    return total_cost / incremental_profit_per_hour
