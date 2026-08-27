import argparse
import json
from pathlib import Path
from .models import GameProfile, Task
from .strategy import daily_plan, five_open_state

def main() -> None:
    parser = argparse.ArgumentParser(description="MHXY Strategy Brain")
    parser.add_argument("--profile", type=Path, help="JSON Game Profile")
    args = parser.parse_args()
    if not args.profile:
        print("mhxy-agent 0.1.0")
        print("用 --profile <file.json> 运行每日策略规划。")
        return
    data = json.loads(args.profile.read_text(encoding="utf-8"))
    profile = GameProfile(
        server=data.get("server", "未知"), version=data.get("version", "未知"),
        online_hours=float(data.get("online_hours", 4)),
        total_investment=float(data.get("total_investment", 0)),
        current_assets=float(data.get("current_assets", 0)),
        emergency_fund=float(data.get("emergency_fund", 0)),
    )
    profile.accounts = [__import__("mhxy_agent.models", fromlist=["Account"]).Account(**a) for a in data.get("accounts", [])]
    tasks = [Task(**t) for t in data.get("tasks", [])]
    plan = daily_plan(profile, tasks)
    print(json.dumps({"state": five_open_state(profile.account_count), "tasks": [t.name for t in plan]}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
