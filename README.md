# MHXY Agent

> Python + PySide6 Windows Desktop Strategy Brain

MHXY Agent 的目标不是生成攻略，而是把长期运营策略工程化为一个可观察、可计算、可测试、可扩展的桌面 Agent。

## 当前版本

**V0.1 / Strategy Brain Desktop Foundation**

已经具备：

- Python 3.10+ 工程
- PySide6 Windows 桌面 UI
- Dashboard / Strategy Brain / 今日任务三页导航
- GameProfile / Account / Task 领域模型
- 五开状态识别
- Net Profit / Hour 收益计算
- 在线时间约束下的任务规划
- 升级回本计算
- StrategyEngine 确定性策略层
- Mock / Simulation 思路，可脱离真实游戏开发
- CLI 与桌面端双入口
- pytest 自动化测试
- GitHub Actions 多 Python 版本 CI
- Windows `run_desktop.bat` 启动脚本

## Windows 启动

安装 Python 3.10+ 后，双击：

```text
run_desktop.bat
```

脚本会创建 `.venv`、安装运行依赖并启动 PySide6 桌面程序。

也可以手动运行：

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m mhxy_agent
```

## CLI

```bash
python -m mhxy_agent.cli
python -m mhxy_agent.cli --profile examples/profile.json
```

## 架构

```text
PySide6 UI
    ↓
Application / Worker
    ↓
Game Profile
    ↓
Economy + Strategy Engine
    ↓
Task Planner
    ↓
Safety Engine
    ↓
Executor Adapter
    ↓
Observe → Verify → Re-plan
```

核心原则：**LLM 负责理解与推理；确定性的收益计算、状态机、约束和安全检查由代码负责。**

## 下一阶段

1. SQLite 持久化与 Memory
2. 账号管理与 Game Profile 编辑器
3. 收益流水与历史分析
4. Strategy Decision Log
5. Action / Observe / Verify 执行链
6. MockExecutor 完整模拟器
7. OCR / OpenCV Observer Adapter
8. Windows Executor Adapter
9. LLM Adapter
10. PyInstaller 打包成独立 `.exe`

真实游戏执行器将在安全校验、观察与验证链完整后再接入；开发和测试阶段始终支持 Simulation 模式。
