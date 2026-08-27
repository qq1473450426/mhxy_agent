from mhxy_agent.models import Task
from mhxy_agent.strategy import upgrade_payback, daily_plan
from mhxy_agent.models import GameProfile

def test_profit_per_hour():
    t = Task("test", 2, cash=100, cost=20)
    assert t.net_profit == 80
    assert t.profit_per_hour == 40

def test_upgrade_payback():
    assert upgrade_payback(1000, 100) == 10
    assert upgrade_payback(1000, 0) is None

def test_daily_plan_respects_hours():
    p = GameProfile(online_hours=2)
    tasks = [Task("slow", 3, cash=1000), Task("fast", 1, cash=100)]
    assert [x.name for x in daily_plan(p, tasks)] == ["fast"]
