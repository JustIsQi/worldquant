# 2026-05-21 因子挖掘策略总结

## 今日目标和最终结果

今日目标是“再挖 10 个 alpha，最少有 1 个 GOOD”。最终完成：

- 新增 ACTIVE alpha：10 个。
- 等级分布：GOOD 4 个，AVERAGE 5 个，INFERIOR 1 个。
- 质量目标：已满足，GOOD 数量为 4，超过“至少 1 个 GOOD”的要求。
- 账号状态：`state/active_alphas.json` 已更新到 61 个 ACTIVE 记录。
- 收尾状态：所有已经启动的候选都已检查。3 个 `UNRESOLVED_404` 候选已重新提交确认，最终均为 SELF_CORRELATION 拒绝；没有遗留 pending submission。

## 起始背景

开跑前账户统计是：

```text
AVERAGE : GOOD : EXCELLENT = 43 : 7 : 1
Total = 51
```

此前账户明显 AVERAGE-heavy，所以今天优先尝试低使用度的 earnings surprise、analyst revision、earnings quality、forward growth 和少量新 liquidity-risk 字段。目标不是只凑数量，而是尽量拿到 GOOD。实际结果较好：10 个新增里有 4 个 GOOD，但最后为了凑满数量也接受了 1 个 INFERIOR。

## 新增 ACTIVE Alpha 明细

| Alpha id | 等级 | 表达式 | Universe | Neutralization | Decay | Truncation | Sharpe | Fitness | Returns | Turnover | Margin |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `gJmnJazv` | GOOD | `0.65*group_rank(-mdl77_2earningmomentumfactor400_rev1q1, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP3000 | MARKET | 20 | 0.08 | 1.90 | 1.51 | 0.0787 | 0.1106 | 0.001422 |
| `KPnWlA3g` | GOOD | `0.65*group_rank(quarterly_eps_surprise_delta, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP3000 | MARKET | 20 | 0.08 | 1.88 | 1.54 | 0.0841 | 0.0691 | 0.002434 |
| `KPnW6EJx` | AVERAGE | `0.65*group_rank(mdl77_earningsqualityfactor_rau, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP3000 | MARKET | 20 | 0.08 | 1.46 | 1.05 | 0.0645 | 0.0549 | 0.002349 |
| `xAeJQrlm` | AVERAGE | `0.65*group_rank(-mdl77_earningsqualityfactor_rau, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP3000 | MARKET | 20 | 0.08 | 1.58 | 1.19 | 0.0707 | 0.0549 | 0.002576 |
| `wp50LXPQ` | AVERAGE | `0.65*group_rank(mdl77_oearningsqualityfactor_pedu, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP3000 | MARKET | 20 | 0.08 | 1.59 | 1.08 | 0.0577 | 0.0548 | 0.002105 |
| `omnxVqv5` | AVERAGE | `0.65*group_rank(mdl77_oearningsqualityfactor_salegpm, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP3000 | MARKET | 20 | 0.08 | 1.54 | 1.21 | 0.0776 | 0.0540 | 0.002876 |
| `O0nlNMWq` | AVERAGE | `0.65*group_rank(-two_year_relative_eps_growth, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP3000 | MARKET | 20 | 0.08 | 1.68 | 1.40 | 0.0865 | 0.0572 | 0.003025 |
| `KPnWgxNl` | GOOD | `0.65*group_rank(-one_year_ahead_eps_growth, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP3000 | MARKET | 20 | 0.08 | 2.12 | 1.94 | 0.1046 | 0.0573 | 0.003654 |
| `O0nlL7Gd` | INFERIOR | `0.65*group_rank(-mdl77_2liquidityriskfactor_yoychgda, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP3000 | MARKET | 20 | 0.08 | 1.40 | 1.00 | 0.0640 | 0.0584 | 0.002189 |
| `VkOvkNxM` | GOOD | `0.65*group_rank(-mdl77_liquidityriskfactor_mad3yttmsale, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP3000 | MARKET | 20 | 0.08 | 1.87 | 1.56 | 0.0868 | 0.0533 | 0.003256 |

## 成功因子的经济直觉

`gJmnJazv` 使用 fiscal quarter 1 EPS forecast revision。直觉是分析师对下一季度盈利预测的变化可能还没有完全反映到价格里。这里取负号，说明当前数据环境下，预测被上修的一侧未必表现更好，反向可能代表过度乐观后的回撤。

`KPnWlA3g` 使用季度 EPS surprise 的变化。EPS surprise 可以理解为“公司实际盈利和市场预期之间的差距”。如果惊喜程度在变化，说明市场对公司基本面的认知在更新。这个因子是 GOOD，说明 earnings surprise 变化仍是今天最有质量的来源之一。

`KPnW6EJx` 和 `xAeJQrlm` 都来自 `rau`，即应收账款的异常变化。应收账款变化可能反映收入质量：收入增长如果没有同步转成现金，可能质量较弱；但不同定义下正反两边都可能捕捉到会计异常或市场误定价。

`wp50LXPQ` 使用异常折旧变化，`omnxVqv5` 使用销售和毛利率变化。这类 earnings-quality 字段不是直接预测“盈利更多”，而是在检查财报质量是否健康。交易对手可能是只看表面利润、没有细分会计质量的资金。

`O0nlNMWq` 和 `KPnWgxNl` 来自 forward EPS growth。它们都取负号，说明今天反而是“预期增长较低或被市场低估的一侧”表现更好。`KPnWgxNl` 是今天最强的 GOOD，Sharpe 2.12、Fitness 1.94。

`O0nlL7Gd` 使用 leverage 的同比变化字段，等级为 INFERIOR。它勉强 ACTIVE，主要贡献是数量和信息源差异，不应作为下一轮重点模板。

`VkOvkNxM` 使用 3 年 TTM sales 的平均绝对偏差字段并取负号。它衡量销售稳定性或波动程度，可能捕捉到市场对经营波动的过度惩罚。该因子为 GOOD，是最后阶段最好的新增质量结果。

## 搜索路径

第一阶段测试低使用度 earnings surprise 和 analyst revision。`rev1q1` 反向和 `quarterly_eps_surprise_delta` 直接产出两个 GOOD，但大量相邻 surprise 字段因为 SELF_CORRELATION 被拒绝，说明这个家族虽然强，但已拥挤。

第二阶段转向 earnings quality 和 analyst/growth 模块。`rau` 正反两边都通过，说明应收账款异常变化仍有独立性。随后 `pedu`、`salegpm`、forward EPS growth 继续产出 ACTIVE。

第三阶段尝试地理销售敞口和 visibility ratio。许多候选指标过线，但最终都因为 SELF_CORRELATION 或低基础指标失败，未贡献新增 ACTIVE。

第四阶段回到低使用度 liquidity-risk 字段，但避开 `pcurlia/covol/netcashp`。`yoychgda` 反向通过但等级 INFERIOR；最后 `mad3yttmsale` 反向成为 GOOD，完成第 10 个 ACTIVE。

## 失败分析

今日主要失败原因仍然是 SELF_CORRELATION。按原始 `submit_summary.csv` 统计，376 条记录中有 79 条最终 SELF_CORRELATION 拒绝，285 条候选在初始检查中出现 SELF_CORRELATION pending。很多高 Sharpe/Fitness 候选，例如 sales exposure、visibility ratio、growth revision、salerec，都不是指标不强，而是和已有提交集太像。

LOW_FITNESS 和 LOW_SHARPE 更普遍，分别出现约 265 次和 234 次。说明许多低使用度字段虽然新，但单独预测力不足。以后不应只因为 userCount 低就提交，需要先看 Sharpe/Fitness 是否有质量。

LOW_SUB_UNIVERSE_SHARPE 出现约 63 次。典型例子是部分 `salesurp`、`salerec` 和 `pelh` 候选，整体 Sharpe/Fitness 不错，但子宇宙不稳。遇到这类候选可以尝试换 universe 或结构，但今天大多没有成为最终来源。

HIGH_TURNOVER 不是今天的问题。所有成功 Alpha 的 turnover 都在约 0.053 到 0.111 之间，decay 20 和 0.35 的短反转稳定器有效压住了换手。

## 今日市场/数据状态

当前账户对 earnings surprise/revision 已经明显拥挤，但仍能从更细的低使用度字段里挖到 GOOD。相比单纯 surprise 水平值，“变化量”和“不同定义的质量字段”更容易通过。

Earnings quality 今天比地理销售敞口更有效。`rau`、`pedu`、`salegpm`、`mad3yttmsale` 都说明会计质量和经营稳定性仍有空间。

MARKET neutralization + 内部 `group_rank(..., subindustry)` 继续有效。今天所有成功因子都使用 TOP3000、MARKET、decay 20、truncation 0.08。

## 下一步建议

优先继续 earnings quality，但不要重复今天已成功字段的小权重变体。可以试：

- `mdl77_oearningsqualityfactor_dpcapex`
- `mdl77_2earningsqualityfactor_chgsgasale`
- `mdl77_earningsqualityfactor_salerec` 的结构变体，而不是原表达式
- `mdl77_liquidityriskfactor_mad3yttmsale` 的相邻但非同义字段
- forward EPS growth 的更稳健变化量，例如 `ts_delta(one_year_ahead_eps_growth, 60)` 或不同中性化设置

也可以对 LOW_SUB_UNIVERSE_SHARPE 的强候选做少量结构性修复，例如换成 `trade_when(volume > adv20, expr, -1)` 或降低短反转权重，但不要做 0.60/0.65/0.70 的机械扫权重。

## 下一次应该避免

- 避免继续围绕 `quarterly_eps_surprise_delta`、`rev1q1`、`rau`、`pedu`、`salegpm` 做同模板小改动。
- 避免继续把地理销售敞口和 visibility ratio 的相邻字段直接套今天模板；这批大多 SELF_CORRELATION。
- 避免提交 INFERIOR 附近的 borderline 候选，除非目标明确是补数量。
- 避免回到 `pcurlia/covol/netcashp` 小权重调参；这些字段在前几天已经非常拥挤。

---

# 追加记录：质量限定目标“再挖 3 个 alpha，低质量不算”

## 本次目标和最终结果

本次追加目标是“再挖 3 个 alpha，低质量的 Alpha 不算”。按照新的计数规则，只有 `AVERAGE`、`GOOD`、`EXCELLENT` 三种质量等级可以计入目标；`INFERIOR`、`Below average` 或更低/不清楚的等级即使 ACTIVE 也不算。

最终结果：

- 新增可计数 ACTIVE alpha：6 个。
- 等级分布：EXCELLENT 1 个，AVERAGE 5 个。
- 低质量 ACTIVE：0 个计入目标。
- 目标状态：已完成，并且超过目标 3 个。
- 账号状态：`state/active_alphas.json` 已更新到 67 个 ACTIVE 记录。
- 收尾状态：本次已启动候选均有最终记录；`2rJ1Nz1N` 从 `UNRESOLVED_200` 追加确认成 ACTIVE，没有遗留 pending submission。

本次开始前的账户统计是：

```text
INFERIOR : AVERAGE : GOOD : EXCELLENT = 1 : 48 : 11 : 1
Total = 61
```

本次结束后的账户统计是：

```text
INFERIOR : AVERAGE : GOOD : EXCELLENT = 1 : 53 : 11 : 2
Total = 67
```

## 本次新增 ACTIVE Alpha 明细

| Alpha id | 等级 | 表达式 | Universe | Neutralization | Decay | Truncation | Sharpe | Fitness | Returns | Turnover | Margin |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `2rJ1Ea3w` | EXCELLENT | `0.65*group_rank(-mdl77_2historicalgrowthfactor_cv4qsales3y, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP3000 | MARKET | 20 | 0.08 | 2.35 | 2.20 | 0.1099 | 0.0510 | 0.004310 |
| `RRdJ136b` | AVERAGE | `0.65*group_rank(-mdl177_historicalgrowthfactor_cv4qcf3y, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP1000 | MARKET | 20 | 0.08 | 1.58 | 1.25 | 0.0779 | 0.0539 | 0.002890 |
| `VkOvGo8Y` | AVERAGE | `0.65*group_rank(-ts_delta(mdl77_2liquidityriskfactor_atmputvol, 20), subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP1000 | MARKET | 20 | 0.08 | 1.58 | 1.13 | 0.0903 | 0.1761 | 0.001026 |
| `58MZpwlz` | AVERAGE | `0.65*group_rank(mdl77_2growthanalystmodel2_qga_ltepssurprise, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP1000 | MARKET | 20 | 0.08 | 1.66 | 1.34 | 0.0817 | 0.0592 | 0.002761 |
| `akor1Vaw` | AVERAGE | `0.65*group_rank(mdl77_2growthanalystmodel_qga_epscapex, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP1000 | MARKET | 20 | 0.08 | 1.77 | 1.35 | 0.0723 | 0.0589 | 0.002455 |
| `2rJ1Nz1N` | AVERAGE | `0.65*group_rank(-mdl77_historicalgrowthfactor_cv4qsales3y, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP1000 | MARKET | 20 | 0.08 | 1.52 | 1.12 | 0.0676 | 0.0555 | 0.002435 |

## 成功因子的经济直觉

`2rJ1Ea3w` 是本次最强结果，等级为 EXCELLENT。它使用 `cv4qsales3y`，衡量过去 3 年销售的波动程度，并取负号。直觉是：销售更稳定的公司更容易被市场低估其持续经营质量，或者在不确定环境中获得更高溢价。这个因子不是在追逐高增长，而是在寻找“经营更稳”的股票。

`RRdJ136b` 使用现金流稳定性相关字段 `cv4qcf3y`，同样取负号。现金流越稳定，说明公司赚钱和回款能力越可预测。交易对手可能是只关注短期价格波动、没有系统区分现金流质量的资金。

`2rJ1Nz1N` 是 `cv4qsales3y` 在 TOP1000 universe 下的同方向版本。它说明销售稳定性在大盘股票中仍然有效，但和 TOP3000 版本相比质量较低，所以是 AVERAGE 而不是 EXCELLENT。

`VkOvGo8Y` 使用 at-the-money put implied volatility 的 20 日变化并取负号。put implied volatility 可以理解为市场为下跌保护支付的价格。这个因子捕捉的是期权市场恐慌或避险需求的变化，可能在恐慌过度后获得反转收益。

`58MZpwlz` 使用 long-term EPS surprise。它衡量长期盈利预期和实际/基准之间的差异。长期预期变化较慢，和短期 earnings surprise 不完全相同，因此在 TOP1000 设置下通过了自相关检查。

`akor1Vaw` 使用 EPS growth to CapEx link。它关注盈利增长和资本开支之间是否匹配。直觉是：如果盈利增长背后有合理的资本投入支持，或者市场误读了资本开支对未来盈利的作用，就可能形成可交易的预期差。

## 搜索路径

第一阶段继续测试 earnings quality、management quality、historical growth、value analyst 字段。大多数质量字段 Sharpe/Fitness 不够，或者因为 LOW_SUB_UNIVERSE_SHARPE 失败；但 `-mdl77_2historicalgrowthfactor_cv4qsales3y` 在 TOP3000 下直接产出 EXCELLENT。

第二阶段沿着销售/现金流稳定性相邻字段扩展。许多相邻字段，例如 `cv4qcf3y`、`y3fcq4vc`、`salegstdev`，在 TOP3000 下指标很强，但几乎都被 SELF_CORRELATION 拒绝。说明稳定性这个信息源有效，但同一 universe 下已经很拥挤。

第三阶段切换到 option、short/borrow、news/event 的变化量。option 字段有一些候选 Sharpe/Fitness 接近过线，但 TOP3000 下仍然自相关或低适应度，没有直接贡献 ACTIVE。

第四阶段做 settings rescue：把强但自相关失败的候选切到 TOP1000、MARKET、decay 20。这个变化显著有效，最终贡献 5 个 AVERAGE，包括现金流稳定性、销售稳定性、期权 implied volatility 变化和 growth analyst 字段。

## 失败分析

SELF_CORRELATION 仍然是最大障碍。很多强候选不是没有预测力，而是和已有提交集太像。例如 `-mdl77_historicalgrowthfactor_cv4qsales3y` 在 TOP3000 下 Sharpe/Fitness 和 EXCELLENT 因子几乎一样，但提交失败；切到 TOP1000 后才通过。

LOW_FITNESS 和 LOW_SHARPE 在 value analyst、news/event 和部分 option 变化量里很常见。低 userCount 不等于高质量；很多低使用字段只是没人用，未必有稳定预测力。

LOW_SUB_UNIVERSE_SHARPE 主要出现在 management quality 和 option level/变化量候选。`trade_when(volume>adv20, ...)` 对本批候选没有明显修复效果，后续不要机械套用。

本次没有把 INFERIOR 或 Below average 计入成果。最终 6 个新增全部是 AVERAGE 或 EXCELLENT，符合“低质量不算”的新规则。

## 本次学到的市场/数据状态

销售和现金流稳定性是当前最值得继续研究的信息源之一。它能产生 EXCELLENT，但相邻字段之间高度相似，必须通过 universe、neutralization 或时间变换来拉开相关性。

TOP1000 settings rescue 在今天有效。它让 TOP3000 下自相关失败的强候选变成可提交 AVERAGE，说明大盘股票的收益流和全 TOP3000 股票池不完全相同。但 TOP1000 也可能降低因子容量和泛化能力，不能无限依赖。

Growth analyst 字段在 TOP1000 下仍有空间，尤其是 `qga_epscapex` 和 `qga_ltepssurprise`。这类字段和直接 earnings surprise 不完全一样，可以作为下一轮重点。

## 下一步建议

优先尝试这些方向：

- TOP1000 下继续测试 growth analyst 相邻字段：`mdl77_2growthanalystmodel_qga_niroe`、`mdl77_growthanalystmodel_qga_iarsales`、`mdl77_growthanalystmodel_qga_opmarginsales`。
- 对稳定性字段只做结构性变化，不做同义字段堆叠。可以试 `ts_delta(cv4q..., 120)`、`ts_rank(cv4q..., 252)`，或者切换 neutralization。
- Option family 中继续围绕 `atmputvol` 的变化做低换手版本，例如更长窗口 `ts_delta(..., 60)` 或更低短反转权重。
- 如果强候选在 TOP3000 下只有 SELF_CORRELATION 失败，优先尝试 TOP1000 或 INDUSTRY neutralization，而不是继续改 0.65/0.35 的小权重。

## 下一次应该避免

- 不要继续直接提交 `cv4qsales3y`、`cv4qcf3y`、`salegstdev` 的同义字段水平值；这批很容易撞 SELF_CORRELATION。
- 不要把 `trade_when(volume>adv20, ...)` 当成通用修复器；本次对 LOW_SUB_UNIVERSE_SHARPE 的改善有限。
- 不要把低质量 ACTIVE 当作完成目标。以后必须先看 grade，只有 AVERAGE、GOOD、EXCELLENT 才计数。
- 不要在 TOP1000 rescue 成功后无限重复 settings rescue；它应当用于少量强候选，而不是替代寻找新信息源。
