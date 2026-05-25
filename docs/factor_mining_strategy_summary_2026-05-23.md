# 2026-05-23 因子挖掘策略总结

## 1. 今日目标和最终结果

今日目标是“再挖 10 个因子”。按照当前项目规则，只有新提交并且最终为 `ACTIVE`，且质量等级为 `AVERAGE`、`GOOD`、`EXCELLENT` 的 alpha 才计入目标；`INFERIOR`、已存在的 `ALREADY_ACTIVE`、提交失败或仍待确认的候选都不计数。

最终结果：

- 新增可计数 ACTIVE alpha：10 个。
- 等级分布：AVERAGE 10 个，GOOD 0 个，EXCELLENT 0 个。
- 已启动候选均已收尾：v15 中已经排队但未写入主汇总的 EMEA 和 Latin America 两个地理暴露候选，已在 cleanup 批次中确认，分别为 SELF_CORRELATION 和 LOW_SHARPE/LOW_FITNESS。

更新后的账户累计统计：

```text
INFERIOR : AVERAGE : GOOD : EXCELLENT = 1 : 71 : 13 : 2
Total = 87
```

## 2. 开始时的背景

本日开始前，`AGENTS.md` 记录的累计提交为：

```text
INFERIOR : AVERAGE : GOOD : EXCELLENT = 1 : 61 : 13 : 2
Total = 77
```

账户已经明显偏 AVERAGE-heavy。也就是说，普通过线因子已经很多，但 GOOD 和 EXCELLENT 的比例不足。因此今天理论上应该优先寻找强质量、低相关的候选；实际挖掘中，很多高 Sharpe/Fitness 的候选都因为 SELF_CORRELATION 失败，最后完成数量主要依靠 TOP500 下的销售惊喜、经营稳定性、地理销售暴露和少量期权偏度变化。

## 3. 今日新增 ACTIVE Alpha 明细

| Alpha id | Grade | Expression | Universe | Neutralization | Decay | Truncation | Sharpe | Fitness | Returns | Turnover | Margin |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `JjbZoZpO` | AVERAGE | `0.60*group_rank(-ts_delta(mdl77_2liquidityriskfactor_monchgsip, 90), subindustry)+0.40*group_rank(-ts_delta(close, 5), subindustry)` | TOP500 | SECTOR | 20 | 0.08 | 1.82 | 1.48 | 0.0962 | 0.1459 | 0.001318 |
| `YPQGzWNA` | AVERAGE | `0.70*group_rank(-ts_rank(mdl77_2historicalgrowthfactor_cv4qsales3y, 252), subindustry)+0.30*group_rank(-ts_delta(vwap, 10), subindustry)` | TOP1000 | SECTOR | 20 | 0.08 | 1.58 | 1.20 | 0.0717 | 0.0594 | 0.002413 |
| `JjbZ27em` | AVERAGE | `0.65*group_rank(-ts_rank(mdl77_liquidityriskfactor_mad3yttmsale, 252), subindustry)+0.35*group_rank(-ts_delta(vwap, 10), subindustry)` | TOP1000 | SECTOR | 20 | 0.08 | 1.72 | 1.21 | 0.0623 | 0.0677 | 0.001841 |
| `xARgKzZp` | AVERAGE | `0.60*group_rank(-mdl77_2earningmomentumfactor400_salesurp, subindustry)+0.40*group_rank(-ts_delta(close, 5), subindustry)` | TOP500 | SECTOR | 20 | 0.08 | 1.37 | 1.04 | 0.0722 | 0.0808 | 0.001786 |
| `akovrRA6` | AVERAGE | `0.45*group_rank(-mdl77_oearningmomentumfactor_salesurp, subindustry)+0.35*group_rank(-mdl177_2_5yearrelativevaluefactor_rel5yocfp, subindustry)+0.20*group_rank(-ts_delta(vwap, 10), subindustry)` | TOP500 | SECTOR | 20 | 0.08 | 1.48 | 1.22 | 0.0847 | 0.0586 | 0.002892 |
| `ZYrGY9Px` | AVERAGE | `0.65*group_rank(-ts_delta(implied_volatility_mean_skew_30, 20), subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP500 | SECTOR | 20 | 0.08 | 1.56 | 1.01 | 0.0878 | 0.2098 | 0.000837 |
| `LLkJqKK2` | AVERAGE | `0.65*group_rank(-ts_rank(mdl77_liquidityriskfactor_mad3yttmsale, 252), subindustry)+0.35*group_rank(-ts_delta(vwap, 10), subindustry)` | TOP500 | SUBINDUSTRY | 20 | 0.08 | 1.69 | 1.26 | 0.0692 | 0.0740 | 0.001871 |
| `omVOv2b2` | AVERAGE | `0.65*group_rank(-ts_delta(mdl77_liquidityriskfactor_mad3yttmsale, 120), subindustry)+0.35*group_rank(-ts_delta(vwap, 10), subindustry)` | TOP500 | SECTOR | 20 | 0.08 | 1.77 | 1.46 | 0.0845 | 0.0628 | 0.002692 |
| `GrkJnOp0` | AVERAGE | `0.65*group_rank(-north_america_sales_exposure, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP500 | SECTOR | 20 | 0.08 | 1.49 | 1.15 | 0.0746 | 0.0633 | 0.002356 |
| `6XzOzgP7` | AVERAGE | `0.70*group_rank(ts_delta(asia_pacific_sales_exposure, 60), subindustry)+0.30*group_rank(-ts_delta(vwap, 10), subindustry)` | TOP500 | SECTOR | 20 | 0.08 | 1.45 | 1.14 | 0.0770 | 0.0706 | 0.002182 |

## 4. 每个成功因子的经济直觉

`JjbZoZpO` 使用 `monchgsip`，可以把它理解为 short interest 或空头压力的月度变化。这里取负向 90 日变化，表示偏好做空压力下降的一侧，再加一点短期价格反转来稳定组合。对手方可能是继续追随拥挤空头、没有及时识别空头压力缓解的资金。

`YPQGzWNA` 使用销售稳定性的长期时间序列排名。`cv4qsales3y` 可以粗略理解为过去三年销售波动程度；对它做 252 日排名并取负号，表示偏好销售波动处在自身历史较低位置的公司。直觉是经营更稳定的公司可能被低估，或在风险偏好变化时更抗跌。

`JjbZ27em`、`LLkJqKK2`、`omVOv2b2` 都来自 `mad3yttmsale`，这是过去三年 TTM 销售的平均绝对偏离，可以理解为收入稳定性或波动性。取负号后，因子偏好销售更稳定、或销售波动下降的公司。今天这个方向比传统 EPS 或短借字段更有用，因为它和已有提交的表达不完全一样。

`xARgKzZp` 和 `akovrRA6` 使用销售惊喜 `salesurp`。销售惊喜是实际销售和市场预期销售之间的差异。这里取负号，说明在当前组合设定下，市场可能过度追逐正向销售惊喜，反而给了反向组合机会。`akovrRA6` 还加入了较小权重的经营现金流相对估值锚，帮助降低纯 earnings surprise 的拥挤程度。

`ZYrGY9Px` 使用期权隐含波动率偏度的 20 日变化。期权市场常常更快反映风险偏好和保护性需求；当偏度变化出现极端时，股票现货端可能还没有完全调整。它的换手较高，说明信号更偏短周期。

`GrkJnOp0` 使用北美销售暴露。这里取负号，表示偏好北美收入暴露较低的公司。直觉是如果市场对北美增长、利率或消费环境的定价过于集中，低北美暴露公司可能提供差异化收益。

`6XzOzgP7` 使用亚太销售暴露的 60 日变化。它不是静态地买高或低亚太收入占比，而是看暴露变化方向。对手方可能是只看公司整体业绩、没有及时分辨区域收入结构变化的资金。

## 5. 今日搜索路径

第一阶段从短借、short interest 和 TOP500/SECTOR 结构开始。`monchgsip` 90 日变化给出 `JjbZoZpO`，但同族 `dmd_supply`、`monchgsip` 邻近权重和窗口很快 SELF_CORRELATION。

第二阶段尝试 TOP1000/SECTOR 的历史增长稳定性。原始 `cv4qcf3y` 等水平项多半 self-correlated 或 Fitness 不够，但 `-ts_rank(cv4qsales3y, 252)` 给出 `YPQGzWNA`。这说明结构性时间序列变换比原始水平更有价值。

第三阶段扩大到 `mad3yttmsale` 等稳定性字段。TOP1000/SECTOR 的 `-ts_rank(mad3yttmsale, 252)` 给出 `JjbZ27em`；后续 TOP500/SUBINDUSTRY 和 TOP500/SECTOR 又分别给出 `LLkJqKK2` 和 `omVOv2b2`。这是今天最稳定的补数量方向。

第四阶段用 TOP500/SECTOR 救援强 earnings surprise 和 option-skew 候选。销售惊喜给出 `xARgKzZp`、`akovrRA6`，期权偏度变化给出 `ZYrGY9Px`。TOP500/INDUSTRY、TOP500/MARKET、低截断和 decay 30 的后续变体大多失败，说明有效窗口比较窄。

第五阶段在达到 8/10 后寻找不同信息源。地理销售暴露在 TOP500/SECTOR 下补齐最后两个：`GrkJnOp0` 来自北美销售暴露，`6XzOzgP7` 来自亚太销售暴露变化。v15 中已经排队的 EMEA 和 Latin America 候选也已额外确认，不留下未收尾任务。

## 6. 失败分析

SELF_CORRELATION 仍然是最大失败原因。很多候选不是没有收益，而是和已有 ACTIVE 太像。例如 `mad3yttmsale` 在 TOP500/MARKET 下 Sharpe/Fitness 很强，但直接撞到相关性；sales surprise 的 MARKET、INDUSTRY、低截断版本也大多因为相关性被拒。

LOW_FITNESS 和 LOW_SHARPE 主要出现在三类候选：

- TOP1000/INDUSTRY 的相邻 liquidity/solvency 字段，如 `ocfratio`、`dcc`、`netcashp`、`pcurlia`，多数没有足够强度。
- 会计质量和 growth analyst 的 `ts_rank`/`ts_delta` 变换，变换后相关性可能降低，但预测力也明显变弱。
- TOP200 universe，样本太窄，sales surprise、option skew、geography 和 stability 信号整体指标塌陷。

LOW_SUB_UNIVERSE_SHARPE 在 sales surprise 和 implied-vol skew 中反复出现。它表示因子整体看起来可以，但在某些子股票池里不稳定。TOP500/SECTOR 能救出部分候选，但并不是所有同族变体都能通过。

HIGH_TURNOVER 没有成为硬性提交失败，但 `ZYrGY9Px` 的 turnover 为 0.2098，偏高。以后继续期权偏度方向时，应优先测试更长窗口或更高 decay。

## 7. 今日学到的市场和数据状态

当前账户的 earnings surprise、analyst revision、short interest、地理销售暴露都已经相当拥挤。强信号仍然存在，但小幅调权、小幅改窗口、小幅换 neutralization 很容易失败。

真正有效的变化有三类：

- 从水平值变成时间序列结构，例如 `ts_rank` 或 `ts_delta`。
- 改 universe/neutralization，例如 TOP500/SECTOR 与 TOP500/SUBINDUSTRY。
- 换到相邻但经济含义不同的稳定性字段，例如从销售惊喜切到销售波动稳定性。

不过今天 10 个新增全是 AVERAGE，没有 GOOD 或 EXCELLENT。说明当前做法能完成数量目标，但对提升组合质量帮助有限。

## 8. 下一步应该尝试什么

优先继续经营稳定性，但不要只重复 `mad3yttmsale`：

```text
0.65*group_rank(-ts_rank(new_stability_field, 252), subindustry)
+0.35*group_rank(-ts_delta(vwap, 10), subindustry)
```

可尝试字段：

- `mdl77_liquidityriskfactor_mad3yttmni`
- `mdl177_2_historicalgrowthfactor_cv4qocf3y`
- `mdl177_2_historicalgrowthfactor_rsqr4qfcf3y`
- `mdl177_2_historicalgrowthfactor_slope4qocf3y`

地理暴露可以少量继续，但要换结构：

```text
0.70*group_rank(ts_delta(region_sales_exposure, 90), subindustry)
+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

优先尝试 TOP500/SECTOR 和 TOP1000/SECTOR；不要先去 TOP200。

期权偏度方向仍可探索，但应降低换手：

```text
0.70*group_rank(-ts_delta(implied_volatility_mean_skew_30, 40), subindustry)
+0.30*group_rank(-ts_delta(vwap, 20), subindustry)
```

## 9. 下一步应该避免什么

避免继续做这些事情：

- 在 `mdl77_2earningmomentumfactor400_salesurp`、`mdl77_oearningmomentumfactor_salesurp` 上做 0.55/0.60/0.65 小权重微调。
- 继续把 `mad3yttmsale` 的同一个 `ts_rank` 或 `ts_delta` 在 MARKET、SECTOR、INDUSTRY 间机械搬运。
- 使用 TOP200 作为主要救援手段；今天 TOP200 指标普遍变差。
- 继续围绕 `rel5yfwdep` 或旧 EPS growth 锚做混合，这些方向已经高度拥挤。
- 接受大量 barely ACTIVE 的 AVERAGE。今天已经新增 10 个 AVERAGE，下一次应该提高质量门槛，优先追求 GOOD/EXCELLENT。
