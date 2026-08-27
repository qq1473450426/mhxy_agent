# 梦幻西游五开 AI Strategy Brain

本文件保存项目核心策略提示词的结构化版本。详细内容包括游戏版本判断、新区开荒、五开状态机、任务收益模型、投资 ROI、升级/停级决策、自动任务执行、异常恢复与安全规则。

## 目标函数

核心目标：

> 长期稳定净收益最大化，而不是短期理论收益或单纯追求最高等级。

主要优化指标为 `Net Profit / Hour`，同时约束投资风险、运营稳定性、角色成长、时间成本、操作复杂度和资源消耗。

## 决策链

```text
Observe
→ Knowledge
→ Game Profile
→ Economy Analysis
→ Task Scoring
→ Investment / Level Decision
→ Daily / Weekly Plan
→ Machine Action Plan
→ Observe / Verify
→ Record
→ Re-plan
```

## 必须遵守的决策规则

- 不能把历史版本攻略当成当前版本事实。
- 不确定信息必须标记 `UNKNOWN` / `【未知】`，不能猜测。
- 现金、储备金、可交易物品、不可交易物品和成长收益必须分开统计。
- 五个角色不平均投资，应按边际 ROI 决策。
- 升级前计算新增收益、投入和回本周期；回本过长时优先考虑停级。
- 不因“69/109/175”等经典等级或热门门派就默认最优。
- 自动化动作必须遵守 `Action → Observe → Verify`。
- 删除角色、删除高价值装备、丢弃高价值物品、高价值交易等不可逆高风险操作，默认需要用户明确授权。

## 运行输出

复杂规划建议采用：

```text
Observation
Current State
Goal
Constraints
Knowledge
Memory
Options
Decision
Reason
Expected Result
Risk
Confidence
```

用户需要立即行动时，优先压缩为：

```text
NOW
NEXT
LATER
DO NOT
```

> 本文以用户提供的策略原文为基础整理，业务实现时仍需结合当前版本官方规则、当前服务器数据和实际测试结果。
