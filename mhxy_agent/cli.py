from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import DEFAULT_TASKS, StrategyEngine
from .planner import Planner
from .storage import JsonStore

DEMO_PROFILE = {
    "server": "待填写",
    "server_open_date": "待填写",
    "version": "待确认",
    "online_hours_daily": 4,
    "online_hours_weekly": 28,
    "available_cash": 0,
    "reserve": 0,
    "characters": [{"name": "账号1", "school": "待填写", "level": 0}],
}

def main() -> None:
    parser = argparse.ArgumentParser(prog="mhxy-agent", description="梦幻西游五开长期运营策略 Brain")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("init", help="创建可编辑的 Game Profile")
    sub.add_parser("plan", help="根据 profile 生成今日策略")
    sub.add_parser("tasks", help="查看内置任务收益模型")
    sub.add_parser("demo", help="运行零依赖演示")
    args = parser.parse_args()
    store = JsonStore()
    engine = StrategyEngine()

    if args.command == "init":
        store.save(DEMO_PROFILE)
        print("已创建 data/profile.json，请填写服务器、版本、角色、资金和在线时间。")
    elif args.command == "plan":
        profile = Planner().build_profile(store.load() or DEMO_PROFILE)
        print(json.dumps(Planner().run(profile), ensure_ascii=False, indent=2))
    elif args.command == "tasks":
        for task in DEFAULT_TASKS:
            print(json.dumps(engine.task_report(task), ensure_ascii=False))
    else:
        profile = Planner().build_profile(store.load() or DEMO_PROFILE)
        result = Planner().run(profile)
        print("=== mhxy_agent Demo ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
