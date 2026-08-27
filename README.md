# mhxy_agent

> 《梦幻西游》电脑版五开长期运营 AI Strategy Brain。

本项目把你提供的 **Strategy Brain 2.0** 从“长提示词”落成一个可运行、可测试、可扩展的 Python 项目：状态建模 → 收益计算 → 任务排序 → 升级/停级决策 → Machine Action Plan → 安全校验 → 持续迭代。

## 目标

最终持续回答：

> **对于当前这个五开队伍，现在做什么最划算？**

优化目标为 **长期稳定净收益 / 小时**，同时约束投资风险、运营稳定性、角色成长、操作复杂度和资源消耗，而不是简单追求最高等级或理论总收益。

## 当前已实现

- `GameProfile`：服务器、版本、资金、在线时间、账号/角色状态模型
- 0～175 关键等级节点与五开状态机
- `Task` 收益模型：现金、储备金、可交易物品、成长价值、消耗、风险、成功率
- `Expected Profit` 与 `Net Profit / Hour`
- S/A/B/C/D 稳定性分级
- 每日时间预算下的任务排序
- 升级/停级回本周期判断
- `Marginal ROI` 投资排序
- 收益统计：平均值、中位数、极值、标准差、样本置信度
- `Machine Action Plan`
- `Action → Observe → Verify` 可验证执行
- 高风险/不可逆操作安全拦截
- 本地 JSON 状态持久化
- 零第三方运行依赖的 CLI
- Python 3.10 / 3.11 / 3.12 CI
- 单元测试与 `compileall` 检查

## 项目结构

```text
mhxy_agent/
├── mhxy_agent/
│   ├── __init__.py       # 包信息
│   ├── models.py         # GameProfile / Character / Task / 收益记录
│   ├── engine.py         # 核心策略、收益、ROI、任务排序
│   ├── planner.py        # Profile → Strategy Plan
│   ├── action.py         # Machine Action Plan 与安全控制
│   ├── prompt.py         # Strategy Brain 运行时系统提示词
│   ├── storage.py        # JSON 持久化
│   └── cli.py             # 命令行入口
├── tests/
│   └── test_engine.py
├── docs/
│   └── strategy-brain.md # 原始策略规范的结构化文档
├── .github/workflows/test.yml
├── pyproject.toml
└── README.md
```

## 快速运行

### 方式一：不安装，直接运行

```bash
python -m mhxy_agent.cli demo
```

查看内置任务模型：

```bash
python -m mhxy_agent.cli tasks
```

创建自己的 Game Profile：

```bash
python -m mhxy_agent.cli init
```

编辑 `data/profile.json` 后生成策略：

```bash
python -m mhxy_agent.cli plan
```

### 方式二：安装为 CLI

```bash
python -m pip install -e .
mhxy-agent demo
mhxy-agent init
mhxy-agent plan
```

项目当前核心运行时仅使用 Python 标准库，因此基础功能不依赖网络、数据库或第三方 SDK。

## Game Profile

示例：

```json
{
  "server": "新区名称",
  "server_open_date": "2026-08-27",
  "version": "待确认",
  "online_hours_daily": 4,
  "online_hours_weekly": 28,
  "available_cash": 500000,
  "reserve": 100000,
  "characters": [
    {"name": "账号1", "school": "待填写", "level": 60},
    {"name": "账号2", "school": "待填写", "level": 60}
  ]
}
```

缺失信息必须保持 `未知` / `待确认`，策略引擎不会把缺失数据伪装成事实。

## 核心策略

### 1. 五开状态

```text
STATE_0  单号起步
STATE_1  单号成长
STATE_2  准备第二号
STATE_3  双开
STATE_4  准备第三号
STATE_5  三开
STATE_6  准备第四号
STATE_7  四开
STATE_8  五开准备
STATE_9  五开基础成型
STATE_10 五开稳定运营
STATE_11 五开收益优化
STATE_12 长期搬砖
```

### 2. 等级节点

```text
0 → 20 → 30 → 40 → 50 → 60 → 69 → 89 → 109 → 129 → 159 → 175
```

升级不能仅凭“等级更高”决定。必须比较新增任务、装备/宝宝/技能/修炼投入和新增净收益。

回本公式：

```text
Payback Period = Upgrade Cost / Added Net Profit Per Hour
```

### 3. 任务评价

收益必须拆开：

```text
Cash
Reserve
Tradable Items
Non-tradable Items
Growth Value
Consumption
Risk Cost
```

核心决策使用期望收益：

```text
Expected Profit
= Expected Cash
+ Expected Tradable Items
+ Expected Growth Value
- Consumption
- Risk Cost
- Operation Cost
```

然后按：

```text
Net Profit / Hour
```

进行排序。

**现金 ≠ 储备金 ≠ 物品价值。**

### 4. 投资

五个角色不平均投资，按 `Marginal ROI` 决定预算优先级：

```text
Main Carry
Secondary Carry
Support
Support
Support
```

装备、宝宝、技能、修炼、法宝都应该回答：成本多少、收益增加多少、使用周期多长、回本多少小时、是否有更便宜替代方案。

### 5. 真实数据

不要长期依赖理论收益。建议记录 10 / 20 / 50 / 100 小时测试结果，并统计平均值、中位数、最大/最小值、标准差。样本不足时降低置信度。

## 自动化执行层

策略层输出的决策可以进一步转成机器执行计划：

```text
Action
  ↓
Observe
  ↓
Verify
  ↓
Success / Recovery
```

例如任务“抓鬼”会被拆成检查队伍、检查角色状态、领取任务、定位、导航、进入战斗、执行战斗、验证结果等步骤。

**重要：当前仓库实现的是策略与执行计划层，不会擅自控制游戏客户端。** 真正接入桌面自动化、视觉识别或输入控制时，应在 Action 层增加具体 Adapter，并继续保留 Verify 和 SafetyGuard。

## 安全机制

默认拒绝以下高风险操作：

- 删除角色
- 删除高价值装备/物品
- 高价值交易
- 其他不可逆操作

除非通过明确授权加入允许集合。安全控制位于 `mhxy_agent/action.py`，与策略层解耦。

## 知识来源原则

项目遵循原始 Strategy Brain 的知识优先级：

1. 官方公告 / 当前游戏实际规则
2. 当前版本可靠资料
3. `xyq-skills` Knowledge Layer
4. 当前服务器 / 新区实际数据
5. 长期玩家经验
6. 历史攻略
7. AI 推测

`xyq-skills` 只作为 Knowledge Layer，不直接复制为 Hardcoded Rule Layer。历史数据、玩家经验和 AI 推测必须明确标注，不能伪装成当前官方事实。

## 测试

运行：

```bash
python -m unittest discover -s tests -v
python -m compileall -q mhxy_agent
```

GitHub Actions 会在 Python 3.10 / 3.11 / 3.12 上执行这两项检查。

## 当前边界

本版本的目标是先把你给出的提示词**真正程序化**，形成稳定的 Strategy Core，而不是假装已经具备完整的游戏视觉/鼠标键盘控制能力。

后续可以在不破坏核心策略层的前提下增加：

- LLM Provider Adapter（OpenAI / 本地模型等）
- `xyq-skills` 同步与检索
- 官方规则/版本数据 Adapter
- 新区价格数据 Adapter
- SQLite / PostgreSQL 数据层
- 收益流水与历史 Memory
- 每日/每周调度器
- OCR / CV 游戏状态观察器
- Windows 游戏客户端 Adapter
- Action Recovery State Machine
- Web API / Web UI

这些都应通过接口接入，避免把外部服务硬编码进收益模型。

## 设计原则

> **观察数据 → 读取知识 → 建模 → 计算 → 决策 → 生成任务 → 验证执行 → 记录结果 → 重新规划。**

最终原则：

> **稳定、低投入、高效率、可持续的五开运营体系。**

## License

当前仓库未指定开源许可证；如准备公开分发，建议后续明确 License。
