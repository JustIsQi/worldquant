# 量化小白的因子挖掘方法论

这是给完全没接触过量化的人写的可持续学习路径。读完这一份，再回到
[daily_workflow.md](daily_workflow.md) 看怎么跑命令。

---

## 第一章：异常为什么会存在

量化挖到一个 ACTIVE alpha，本质上是发现一个**市场异常**（anomaly）——某类股票的预期收益和它们承担的风险不匹配。学术界对"为什么 anomaly 能持续存在"主要有三类解释：

1. **风险溢价**（risk-based）：异常是对承担某类风险的补偿。
   - 例：value（低估值股票）的超额收益，可能是补偿"价值陷阱"的破产风险。
   - 例：low-volatility 的超额收益（部分情况下）可被解释为杠杆约束下的均衡。
2. **行为偏差**（behavioural）：投资者系统性犯错。
   - 例：momentum（动量）= 投资者对新信息反应过慢（underreaction）。
   - 例：short-term reversal（短期反转）= 流动性冲击后的过度反应回归。
3. **市场摩擦**（frictions）：交易成本、做空成本、监管让套利者无法消除异常。
   - 例：小盘股的 anomaly 更顽固，因为机构难以做空。

**一句话心智模型**："anomaly 能持续，是因为总有人愿意接反面单。" 当你挖到一个 alpha，问自己：谁在亏钱给我？如果答不出来，回测好看也可能是过拟合。

**延伸阅读**：

- Fama & French (1993) "Common risk factors in the returns on stocks and bonds"
- Asness, Moskowitz, Pedersen (2013) "Value and Momentum Everywhere"
- Novy-Marx (2013) "The Other Side of Value: The Gross Profitability Premium"
- Hou, Xue, Zhang (2020) "Replicating Anomalies"（一篇泼冷水的论文，提醒你大部分 anomaly 出样本就死了）

---

## 第二章：六大因子家族

本仓库当前生成器内置 6 个家族（见 [configs/daily.yaml](../configs/daily.yaml) 的
`candidates.families`）。每个家族都是横截面（cross-sectional）信号：对每只股票打分，然后做多高分股、做空低分股。

### 2.1 leverage（杠杆 / 财务困境）

- **经济直觉**：负债率高的公司在经济下行时违约概率高；理论上市场应该要求更高的预期回报作为补偿。但实际数据里高杠杆股票常常 *underperform*，说明投资者高估了高杠杆公司的成长性，或低估了违约风险。做空高杠杆 + 做多低杠杆通常有正预期。
- **典型表达式**：
  ```
  liabilities/assets
  rank(liabilities/assets)
  group_rank(liabilities/assets, subindustry)
  ```
- **有效时**：信贷收紧期、衰退期、风险厌恶上升期。
- **失效时**：流动性泛滥（QE 时期）、低利率时期高杠杆公司反而被追捧。
- **FAIL 时怎么读**：
  - `SELF_CORRELATION` PENDING：你已经有一个杠杆 alpha 在 ACTIVE 了（**这是当前仓库的真实情况**）。应当换家族，不要继续在杠杆字段上加权重。
  - `LOW_FITNESS`：杠杆是慢变量，把 `brain.decay` 调高（30+），或用 `ts_mean(liabilities/assets, 60)`。

### 2.2 quality（盈利质量）

- **经济直觉**：盈利能力强、资本效率高的公司长期跑赢盈利能力差的——Novy-Marx 2013。和 value 互补：避免"便宜的烂公司"。
- **典型表达式**：
  ```
  pnl/assets
  rank(pnl/equity)
  group_rank(cashflow/assets, subindustry)
  ```
- **有效时**：成长股回调期、利率上行期（市场重新认可现金流）。
- **失效时**：极端 momentum 行情（垃圾股暴涨）、政策红利驱动的板块（基本面失灵）。
- **FAIL 时怎么读**：
  - `LOW_SUB_UNIVERSE_SHARPE`：质量因子常只在大盘股有效，加 `group_rank` 或换 universe 到 TOP500。
  - `HIGH_TURNOVER`：基本面数据本不该高换手，检查 wrap 是否引入了短窗口噪声。

### 2.3 value（价值）

- **经济直觉**：用 `bookvalue/price`、`earnings/price`、`cashflow/price` 这类比值找"便宜"的股票。长期超额收益最被验证的家族之一。
- **典型表达式**：
  ```
  bookvalue_ps/close
  rank(cashflow/cap)
  group_rank(pnl/cap, subindustry)
  ```
- **有效时**：泡沫破裂后、价值回归期、利率上行期。
- **失效时**："Value trap"——便宜是有原因的（行业被颠覆、公司治理差）。2017–2020 美股 value 大幅落后。
- **FAIL 时怎么读**：
  - `LOW_SHARPE`：检查符号——B/P 大的是便宜还是贵？通常 B/P 大 = 便宜 = 预期高回报，做多高 B/P。
  - `SELF_CORRELATION`：和 quality 容易重合（盈利质量高的常 B/P 不高），换 field。

### 2.4 reversal_short（短期反转）

- **经济直觉**：1–5 天 horizon 上，强势股回调、弱势股反弹。微结构原因：流动性冲击后的回归。注意符号——做多昨天跌的、做空昨天涨的。
- **典型表达式**：
  ```
  -ts_delta(close, 5)
  -returns
  rank(-ts_zscore(returns, 5))
  ```
- **有效时**：高波动、低流动性环境，做市商需要溢价。
- **失效时**：强趋势市场（牛市、连续上涨）、流动性极佳的大盘股（已被套利者吃掉）。
- **FAIL 时怎么读**：
  - `LOW_FITNESS`（典型）：短期反转 Sharpe 看起来不错但 fitness 低，**通常是换手率高、交易成本吃掉了 alpha**。把 `decay` 调到 20+，或者放弃这个家族。
  - `HIGH_TURNOVER`：意料之中，这个家族天然高换手；考虑用更长窗口（`ts_delta(close, 20)`）。

### 2.5 momentum_medium（中期动量）

- **经济直觉**：3–12 月 horizon 上，赢家继续赢、输家继续输（Jegadeesh-Titman 1993）。和短期反转方向相反。常解释为投资者对新信息反应不足（underreaction）。
- **典型表达式**：
  ```
  ts_delta(close, 60)
  rank(ts_rank(returns, 120))
  ```
- **有效时**：趋势性行情、有持续主线的市场。
- **失效时**：剧烈反转（momentum crashes，例如 2009-03、2020-03）。
- **FAIL 时怎么读**：
  - `SELF_CORRELATION`：动量很容易和已有公开 alpha 相关，建议加行业中性化 `group_rank(..., subindustry)`。
  - `LOW_SHARPE`：检查窗口大小，120 天比 60 天稳；用 `ts_rank` 比 `ts_delta` 更稳。

### 2.6 volume_lowvol（量价 / 低波动）

- **经济直觉**：
  - 低波动率股票 risk-adjusted 跑赢高波动率（low-vol anomaly，可能是杠杆约束 + 彩票偏好）。
  - 价量负相关（价格下跌伴随成交放大）通常是机构出货信号。
- **典型表达式**：
  ```
  -ts_std_dev(returns, 20)
  -ts_corr(close, volume, 20)
  ```
- **有效时**：避险情绪上升、市场震荡。
- **失效时**：极端牛市（高 beta 股票跑赢）。
- **FAIL 时怎么读**：
  - `LOW_SHARPE`：低波动有时被 cap 中性化吃掉，加 `group_rank(..., subindustry)` 帮助。
  - `LOW_SUB_UNIVERSE_SHARPE`：在小盘股可能噪声大，专注 TOP500/TOP1000。

---

## 第三章：读懂 FAIL 报告（决策树）

每个 alpha 跑完会给一组 check 结果。**先看 FAIL，再看 Fitness，再看 Sharpe，再看 Turnover**。

| FAIL 类型 | 含义 | 第一步排查 | 长期对策 |
|---|---|---|---|
| `LOW_FITNESS` | 信号弱或交易成本过高 | 调高 `decay`（10 → 30 → 60），或换 wrap 平滑（`ts_mean`、`ts_rank`） | 弃用短窗口纯价格信号；用基本面慢变量 |
| `LOW_SHARPE` | 信号方向错或太杂 | 检查表达式正负号；加 truncation | 确认经济直觉，不要凭着回测好看就提交 |
| `LOW_SUB_UNIVERSE_SHARPE` | 只在大盘股 / 部分子样本有效 | 加 `group_rank(..., subindustry)`；切 TOP500 universe | 这个 field 可能本身只适用大盘股，缩 universe |
| `HIGH_TURNOVER` | 换手太高，回测利润被交易成本吃光 | 调高 `decay`；去掉短窗口价格成分 | 看 turnover 是否 >0.5；>0.3 一般已经吃成本 |
| `SELF_CORRELATION` PENDING | 和已 ACTIVE 的 alpha 相关性太高 | **换家族**（不要在同一 field 上继续混） | 用 report.md 的 per-family 表确认还有哪些家族没产出 |
| `LOW_SUB_SHARPE` / `IS_LADDER_SHARPE` | 子周期表现不稳 | 看回测分段，前几年好后几年差通常是过拟合 | 加更长样本测试，谨慎提交 |

**心智 checklist**（每个候选问自己）：

1. 这个信号背后的经济故事是什么？谁在亏钱？
2. 在什么市场环境会失效？过去 5 年里有没有这样的环境？
3. 换手率合理吗？回测里有没有把交易成本扣干净？
4. 是不是和我已 ACTIVE 的 alpha 在赌同一件事？

---

## 第四章：每天的迭代节奏

跑完 daily 拿到 `runs/<date>/<run_id>/report.md` 后，按下列 checklist 决策：

1. **看"今日结论"**：今日有没有新 ACTIVE？周目标差几个？
2. **看"按因子家族表现"**：
   - 哪个家族 `attempted > 0 且 active == 0 且 failed 占大头` → **disable** 该家族（[configs/daily.yaml](../configs/daily.yaml) `families.<name>.enabled: false`）。
   - 哪个家族刚出了 ACTIVE → 给它**加一个新 field**（不是改权重，是加新独立信号），下次跑试试。
   - 哪个家族还没尝试过 → 优先级别人之上。
3. **看"失败原因统计"**：
   - 某个 fail reason 集中（>50%）→ 按第三章决策树调参数。
   - 比如 `LOW_FITNESS` 占大头 → 全局调 `brain.decay`。
4. **看"历史累计 skip_history"**：
   - 某家族 skip 数远大于其他 → 该家族的 field 可能选错了，去换。
5. **commit**：把 `configs/daily.yaml` 改动 commit 到 git。让明天的迭代可追溯。

**红线规则**：

- 如果连续 3 天没出新 ACTIVE，**停止加新候选**，回去读第一章，问自己挖的方向有没有经济直觉。
- 如果 `SELF_CORRELATION` 占 PENDING 大头，**不要**继续加权混合同一个 field——换家族才有效。
- 如果你不能在两句话里讲清楚一个 alpha 在赌什么，别提交。

---

## 第五章：心智模型

1. **回测 fitness ≠ 实盘 alpha**。WorldQuant 的 fitness 已经包含 turnover penalty，但仍可能过拟合。一年里只要稳定出 12 个 active alpha，已经够养一个产品线。
2. **多样性 > 数量**。挖 100 个互相相关的 alpha，能用的还是 1 个。挖 6 个互相低相关的家族各 1 个，组合起来就是 6 个独立来源。
3. **少看 Sharpe，多看 fitness 和 turnover**。Sharpe 1.5 但 turnover 0.8 的 alpha 实盘可能赔钱；Sharpe 0.8 但 turnover 0.05 的可能反而能上。
4. **拒绝"凭感觉调权重"**。每次改 `mix_weights` 都要有理由（经济直觉或某次具体 FAIL）。
5. **学术论文是脚手架，不是答案**。看一篇 anomaly 论文，先问"现在还有效吗？发表后是不是已经被套利掉了？"
6. **失败比成功教得多**。一个 SELF_CORRELATION 失败教会你"杠杆这条路走到头了"；这比任何教科书都直接。

---

## 学习推进路径（按周）

- **第 1 周**：跑通 dry-run，能读懂 [report.md](daily_workflow.md)，理解 sharpe / fitness / turnover 三个指标分别衡量什么。
- **第 2 周**：跑通真实 submit，让 leverage 出 1 个 ACTIVE，复现"基线"。
- **第 3 周**：disable leverage，逼自己用 quality 或 value 出新 ACTIVE。
- **第 4 周**：交叉家族组合（e.g. `rank(quality_field) * rank(value_field)`），出第一个 multi-factor alpha。
- **第 8 周**：能在 commit 信息里写清楚"我为什么 enable 这个家族 / 改这个 decay"，并且预测下一次 FAIL 类型。

到这一步，你已经不是小白了。
