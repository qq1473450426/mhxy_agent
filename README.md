# MHXY Agent

这是可运行的 Strategy Brain MVP。它把核心策略从 Prompt 落到可测试的领域模型、收益计算、任务排序和 CLI。

## 快速开始

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m mhxy_agent.cli
python -m mhxy_agent.cli --profile examples/profile.json
```

## 当前实现

- GameProfile / Account / Task 数据模型
- 五开阶段识别
- Expected Net Profit / Hour
- 在线时间约束下的任务规划
- 升级投资回本计算
- pytest 自动化测试
- GitHub Actions 多 Python 版本 CI

## 架构

`models` → `strategy` → `cli`；后续可接入 Knowledge、LLM、Memory、Observer、Executor Adapter，而不改变核心策略接口。
