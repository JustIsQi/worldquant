# 2026-05-20 因子挖掘策略总结

## 目标和最终结果

今天的目标是“再挖 10 个 Alpha，最少要有 1 个 GOOD”。最终完成：

- 新增提交并确认 ACTIVE 的 Alpha：10 个。
- 等级分布：AVERAGE 8 个，GOOD 2 个，EXCELLENT 0 个。
- GOOD 要求已满足：`RRNog0v1` 和 `QPnRLwg5` 都是 GOOD。
- 结束后累计提交统计从 `AVERAGE:GOOD:EXCELLENT = 34:4:1` 更新为 `42:6:1`，总数从 39 增加到 49。

这里的 ACTIVE 表示 Alpha 已经通过 WorldQuant BRAIN 的提交检查，可以进入已提交集合。GOOD/AVERAGE 是平台给出的质量等级，通常和夏普、Fitness、稳定性、相关性等综合表现有关。

## 今日新增 Alpha 明细

| Alpha id | 等级 | 状态 | 表达式 | Universe | Neutralization | Decay | Truncation | Sharpe | Fitness | Returns | Turnover | Margin |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `P0nbR0ZM` | AVERAGE | 直接 ACTIVE | `0.80*group_rank(-ts_delta(mdl77_shortsentimentfactor_benchmark_fee, 120), subindustry)+0.20*group_rank(-ts_delta(vwap, 10), subindustry)` | TOP3000 | SUBINDUSTRY | 20 | 0.08 | 1.87 | 1.43 | 0.0731 | 0.0731 | 0.002000 |
| `RRNog0v1` | GOOD | 直接 ACTIVE | `0.70*group_rank(-ts_delta(mdl77_2liquidityriskfactor_monchgsip, 60), subindustry)+0.30*group_rank(-ts_delta(vwap, 10), subindustry)` | TOP3000 | SUBINDUSTRY | 20 | 0.08 | 2.08 | 1.62 | 0.0762 | 0.1216 | 0.001253 |
| `2rvodKWJ` | AVERAGE | 直接 ACTIVE | `0.70*group_rank(-mdl77_2liquidityriskfactor_sigma, subindustry)+0.30*group_rank(-ts_delta(vwap, 10), subindustry)` | TOP3000 | INDUSTRY | 20 | 0.08 | 1.44 | 1.32 | 0.1043 | 0.0462 | 0.004521 |
| `78xRqwW8` | AVERAGE | pending 后确认 ACTIVE | `0.70*group_rank(-mdl77_2liquidityriskfactor_impduration, subindustry)+0.30*group_rank(-ts_delta(vwap, 10), subindustry)` | TOP3000 | INDUSTRY | 20 | 0.08 | 1.63 | 1.05 | 0.0518 | 0.0436 | 0.002376 |
| `d5nrxgbK` | AVERAGE | pending 后确认 ACTIVE | `0.70*group_rank(mdl77_2historicalgrowthfactor_slope4qocf3y, subindustry)+0.30*group_rank(-ts_delta(vwap, 10), subindustry)` | TOP3000 | INDUSTRY | 20 | 0.08 | 1.57 | 1.21 | 0.0741 | 0.0412 | 0.003597 |
| `akN9z1Zx` | AVERAGE | 直接 ACTIVE | `0.70*group_rank(mdl77_2liquidityriskfactor_netcashp, subindustry)+0.30*group_rank(-ts_delta(vwap, 10), subindustry)` | TOP3000 | MARKET | 20 | 0.08 | 1.66 | 1.38 | 0.0869 | 0.0405 | 0.004294 |
| `e7nZvk56` | AVERAGE | 直接 ACTIVE | `0.85*group_rank(-mdl77_2liquidityriskfactor_pcurlia, subindustry)+0.15*group_rank(-ts_delta(vwap, 10), subindustry)` | TOP3000 | MARKET | 20 | 0.08 | 1.27 | 1.05 | 0.0862 | 0.0226 | 0.007620 |
| `ZYjV69PY` | AVERAGE | pending 后确认 ACTIVE | `0.65*group_rank(-mdl77_2liquidityriskfactor_pcurlia, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP3000 | MARKET | 20 | 0.08 | 1.40 | 1.25 | 0.0989 | 0.0508 | 0.003899 |
| `QPnRLwg5` | GOOD | pending 后确认 ACTIVE | `0.65*group_rank(-mdl77_2liquidityriskfactor_covol, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP3000 | MARKET | 20 | 0.08 | 1.75 | 1.54 | 0.0969 | 0.0507 | 0.003821 |
| `0mAZAEpp` | AVERAGE | pending 后确认 ACTIVE | `trade_when(volume>adv20, 0.65*group_rank(mdl77_2liquidityriskfactor_voldiff_pc, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry), -1)` | TOP3000 | MARKET | 20 | 0.08 | 1.67 | 1.37 | 0.0836 | 0.1208 | 0.001384 |

## 每个成功 Alpha 的经济直觉

`P0nbR0ZM` 使用的是做空借券费用的长期变化。直觉是：如果某些股票的借券费用显著上升，说明市场上愿意付费做空的人变多，负面信息可能已经被部分投资者发现；表达式取负号并加上短期 VWAP 反转，是在捕捉“借券压力变化后的相对定价偏差”。交易对手可能是反应较慢、只看价格不看借券市场信息的投资者。

`RRNog0v1` 使用 `monchgsip`，属于流动性/短融或证券借贷相关的月度变化信息。这个 Alpha 是 GOOD，Sharpe 2.08、Fitness 1.62。它说明“借贷或流动性压力的变化”在今天这批搜索中是高质量信息源。交易对手可能是没有及时处理证券借贷市场变化的资金，或者只用传统财务和价格信号的模型。

`2rvodKWJ` 使用 `sigma` 流动性风险字段。可以理解为衡量股票流动性或风险波动的横截面特征。表达式对该字段取负，代表偏好某类更低风险或更稳定的股票，同时用 VWAP 短期反转做稳定器。它的 Fitness 较高但 Sharpe 低于今天的严格质量门槛，属于可提交但不是优质方向。

`78xRqwW8` 使用 `impduration`，可以理解为隐含期限或久期相关的流动性风险信息。它的收益和换手都较温和，最终 pending 后通过，说明这个字段与已提交集合的相关性尚可，但 Fitness 只有 1.05，质量边际较薄。

`d5nrxgbK` 是今天较少数不来自流动性风险模块的成功 Alpha。它使用历史经营现金流增长斜率 `slope4qocf3y`，直觉是经营现金流持续改善的公司可能更有基本面支撑。交易对手可能是短期价格驱动资金，或者没有充分纳入现金流趋势的模型。

`akN9z1Zx` 使用 `netcashp`，偏向现金/净现金相关的流动性风险字段。在 MARKET 中性化下通过，说明从行业或子行业强中性化切到市场中性化，有时可以保留字段本身的横截面结构，降低和旧 Alpha 的冲突。

`e7nZvk56` 使用 `pcurlia`，它的换手很低，Sharpe 和 Fitness 只是刚过平台线。这个 Alpha 的价值主要是补充低换手、低相关性，而不是贡献高质量等级。后续不应围绕它继续做小权重重复提交。

`ZYjV69PY` 也是 `pcurlia` 家族，但把稳定器从 VWAP 10 日反转换成 close 5 日反转，权重从 0.85/0.15 改为 0.65/0.35。它说明 close 稳定器在 MARKET 设置下对部分流动性字段更有效，但后续相邻变体很快拥挤。

`QPnRLwg5` 使用 `covol`，是今天第二个 GOOD。`covol` 可以理解为共同波动或流动性风险中的协同波动信息。这个因子在 MARKET 中性化下表现好，Sharpe 1.75、Fitness 1.54，说明“流动性压力和价格短期反转”的组合仍能产生质量较好的信号。

`0mAZAEpp` 使用 `voldiff_pc`，即 put/call 结构相关的成交量差异，并用 `trade_when(volume>adv20, ..., -1)` 做成交量过滤。`trade_when` 的意思是只在成交量高于 20 日均量时更新或持有信号，否则进入退出状态。这个设计改变了持仓路径，最终让一个原本容易卡在 SELF_CORRELATION 的 put/call 变体通过。

## 搜索路径

今天从低使用度的短借、地理敞口和流动性风险字段开始。早期最有效的是 `benchmark_fee` 和 `monchgsip`，直接拿到 2 个 ACTIVE，其中 `RRNog0v1` 是 GOOD。随后继续尝试地理敞口、销售敞口、短借变化等相近信号，但大部分因为 SELF_CORRELATION 被拒绝。

第二阶段转向 INDUSTRY 中性化下的流动性风险字段。`sigma`、`impduration` 和历史现金流增长字段分别产出 `2rvodKWJ`、`78xRqwW8`、`d5nrxgbK`。这个阶段的经验是：流动性风险模块本身有信号，但同一字段家族的简单变体相关性非常高。

第三阶段切到 MARKET 中性化。这个设置明显比 NONE、全局 `rank(...)`、TOP1000 更有效。`netcashp`、`pcurlia`、`covol` 在 MARKET 下贡献了 4 个 ACTIVE，其中 `QPnRLwg5` 是 GOOD。后续 close 稳定器比 VWAP 稳定器更适合最后一段挖掘。

最后一阶段为了凑满第 10 个 ACTIVE，尝试了 MARKET + `trade_when(volume>adv20, ...)`。大部分 pcurlia/covol/netcashp 的成交量过滤版本仍然 SELF_CORRELATION 失败，但 `voldiff_pc` 的成交量过滤版本 `0mAZAEpp` 通过。这说明成交量过滤不是万能去相关工具，但对期权 put/call 成交结构有实际帮助。

## 失败分析

今天最主要的失败原因是 SELF_CORRELATION。跨所有 2026-05-20 summary 统计，pending 中出现 SELF_CORRELATION 约 400 次，最终失败中 SELF_CORRELATION 约 107 次。这说明当天搜索已经进入“相同信息源太拥挤”的阶段，不应该继续围绕 `pcurlia`、`covol`、`netcashp` 做小权重或小窗口变化。

收尾时还重新检查了 7 个早期 `UNRESOLVED_404` 的候选：`E5qxARrG`、`mLqNndrx`、`le7POZv2`、`VkXbg3dG`、`78xRVYw8`、`le7P5m9n`、`xAepGPXm`。这些 Alpha 当时已经完成回测但提交确认没有最终结果；重新提交后全部因为 SELF_CORRELATION 被拒绝。因此它们不计入今日新增 ACTIVE，也不会改变最终 10 个 ACTIVE、2 个 GOOD 的结论。

LOW_FITNESS 和 LOW_SHARPE 也很多，分别约 284 次和 266 次。尤其是 option/short-interest 的一些候选字段，例如 `out_of_money_put_call_ratio`、`mdl77_2400_ctpmto`、部分 short sentiment 字段，在 MARKET + close 稳定器下没有达到质量线。它们不是完全不能用，但需要换表达式结构或换中性化设置，而不是继续原模板。

LOW_SUB_UNIVERSE_SHARPE 约 115 次，说明部分候选在整体上看起来不错，但在子宇宙中的表现不稳。比如 `voldiff_pc` 的直接表达式有很高 Sharpe/Fitness，但经常卡在相关性或子宇宙稳健性上。以后对高换手期权字段要更早检查子宇宙表现。

HIGH_TURNOVER 不是今天的主要问题。多数成功 Alpha 的 Turnover 低于 0.13，只有 `0mAZAEpp` 因为期权成交结构和 `trade_when` 设计达到 0.1208，但仍在可接受范围内。

## 今天学到的市场/数据状态

今天的账户环境明显偏拥挤。流动性风险字段能产出 ACTIVE，但同一家族的简单权重变化很容易与当天或历史已提交 Alpha 高相关。`pcurlia`、`covol`、`netcashp` 这几个字段已经从“可继续探索”变成“只适合少量结构性变换”的状态。

`MARKET` 中性化在今天比 `INDUSTRY` 后期、`NONE`、TOP1000 和全局 `rank(...)` 更有效。可能原因是 MARKET 保留了更多行业内/子行业内的相对结构，而表达式内部已经用了 `group_rank(..., subindustry)`，外部再做过强中性化会损失信号。

`trade_when(volume>adv20, ...)` 可以改变持仓路径，但不能自动解决自相关。它对 `voldiff_pc` 有帮助，对 `pcurlia`、`covol`、`netcashp` 大多仍然失败。

## 下一步建议

优先尝试新的信息源，而不是继续调今天成功字段的权重。具体方向：

1. 低使用度 earnings revision / earnings surprise：
   - `mdl77_earningmomentumfactor_fqsurstd`
   - `mdl77_2earningmomentumfactor400_mrspe`
   - `mdl77_oearningmomentumfactor_ratrev6m`
   - `mdl77_earningmomentumfactor_fy1epsskew`
   - 模板：`0.65*group_rank(field, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)`

2. 期权和 put/call 结构，但要减少重复：
   - 继续 `voldiff_pc`，但只尝试结构性变化，例如 `trade_when`、更长 decay、或不同成交量条件。
   - 谨慎尝试 `implied_volatility_mean_skew_60/90`、`implied_volatility_put_60/90`、`implied_volatility_call_60/90`，不要只复制 `out_of_money_put_call_ratio` 的失败模板。

3. 流动性风险字段的新结构：
   - 不再做 `pcurlia/covol/netcashp` 的 0.60/0.65/0.70 小权重变化。
   - 如果继续用这些字段，优先用不同事件门控、长窗口变化、或和非流动性基本面字段混合。

4. 基本面现金流和经营质量：
   - 今天 `slope4qocf3y` 成功，说明历史经营质量仍有空间。
   - 下一步可以试相邻但不是同义的现金流质量字段，要求 Sharpe > 1.50、Fitness > 1.15，并在 pending 时等待最终相关性结果。

## 下一次应该避免

- 避免继续围绕 `rel5yfwdep`、`q1aepsg`、`pcurlia`、`covol`、`netcashp` 做小权重调参。
- 避免把已经 SELF_CORRELATION 失败的表达式只改成 0.60/0.65/0.70 这种微调。
- 避免在 TOP1000 上重复今天的流动性模板，今天 TOP1000 明显削弱了指标。
- 避免全局 `rank(...)` 替代 `group_rank(..., subindustry)`，今天全局 rank 明显偏弱。
- 避免为了数量提交刚过线但没有新信息源的候选。今天虽然完成 10 个目标，但 8 个是 AVERAGE，账户仍然 AVERAGE-heavy，后续应该提高质量门槛。

## 追加任务：再挖 2 个 Alpha

### 目标和最终结果

在完成前面 10 个 Alpha 后，又追加了“再挖两个 Alpha”的目标。追加任务最终完成：

- 新增 ACTIVE：2 个。
- 等级分布：AVERAGE 1 个，GOOD 1 个。
- 新增后累计统计从 `42:6:1` 更新为 `43:7:1`，总数从 49 增加到 51。

### 追加新增 Alpha 明细

| Alpha id | 等级 | 状态 | 表达式 | Universe | Neutralization | Decay | Truncation | Sharpe | Fitness | Returns | Turnover | Margin | Self-correlation |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `vR57j5oA` | AVERAGE | 直接 ACTIVE | `0.65*group_rank(-ts_delta(implied_volatility_mean_skew_60, 20), subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP3000 | MARKET | 20 | 0.08 | 1.76 | 1.49 | 0.1151 | 0.1615 | 0.001425 | 0.5873 |
| `QPnR3xoM` | GOOD | 直接 ACTIVE | `0.65*group_rank(-mdl77_2earningmomentumfactor400_surp, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP3000 | MARKET | 20 | 0.08 | 1.99 | 1.65 | 0.0861 | 0.0628 | 0.002742 | 0.7585 |

### 追加成功因子的经济直觉

`vR57j5oA` 使用的是 60 日期权隐含波动率偏斜的 20 日变化，并取负号。隐含波动率偏斜可以粗略理解为期权市场对下跌风险和上涨风险的相对定价。如果偏斜快速变化，说明期权交易者对风险的定价在改变。这个 Alpha 试图捕捉“期权市场风险预期变化后，股票价格还没有完全反映”的机会。它的 Turnover 为 0.1615，比大部分基本面因子高，但仍低于 0.20 的偏好线。

`QPnR3xoM` 使用 `mdl77_2earningmomentumfactor400_surp`，属于 earnings surprise / 盈利惊喜相关字段。表达式取负号，说明在这个数据定义和当前市场环境下，字段较高的一侧未必更好，反向信号反而有效。它是 GOOD，Sharpe 1.99、Fitness 1.65，说明追加阶段最值得继续的是新的盈利惊喜字段，而不是继续调流动性风险字段。

### 追加搜索路径

追加阶段先建立基线：前一轮已经有 10 个新增 ACTIVE，因此本轮只统计新出现的 `vR57j5oA` 和 `QPnR3xoM`。候选文件是 `candidate_alphas_20260520_two_more_new_sources_v20.txt`，设置为 USA、TOP3000、MARKET、decay 20、truncation 0.08。

这批候选分两类：第一类是 option implied-volatility skew 和 put/call 隐含波动率结构；第二类是较少使用的 earnings momentum / surprise 字段。期权偏斜类里，原始水平值虽然指标很强，但多次因为 LOW_SUB_UNIVERSE_SHARPE 被跳过；真正通过的是 `-ts_delta(implied_volatility_mean_skew_60, 20)`，也就是“偏斜变化”而不是“偏斜水平”。

盈利惊喜类里，`qepsferr`、`sue` 等方向有些指标不错但 SELF_CORRELATION 失败；`-mdl77_2earningmomentumfactor400_surp` 成功并且成为 GOOD。说明同属 earnings surprise 家族时，也要切换具体字段和符号，不能只围绕已成功字段做小权重变化。

### 追加失败和收尾

追加阶段有两个已经启动但未被 runner 写入 summary 的候选：`pwnbRmmX` 和 `O0ndNwab`。我从 raw alpha JSON 恢复并补写到 `submit_summary.csv`，两者都低于提交门槛：

- `pwnbRmmX`：LOW_SHARPE、LOW_FITNESS。
- `O0ndNwab`：LOW_SHARPE、LOW_FITNESS、LOW_SUB_UNIVERSE_SHARPE。

这两个候选没有提交，不能计入 ACTIVE。追加阶段没有遗留需要继续确认的 pending submission。

### 追加后的下一步

下一轮优先继续 earnings surprise，但要换字段源，例如：

- `mdl77_2earningmomentumfactor400_surp` 的相邻但不重复字段：`sue`、`qepsferr`、`spe1yfvc` 可以换中性化或加入非价格基本面锚。
- 期权方向优先研究变化量：`ts_delta(implied_volatility_mean_skew_60, 20)` 成功，水平值容易 LOW_SUB_UNIVERSE_SHARPE。
- 避免继续简单提交 `implied_volatility_mean_skew_60/90` 水平值和 `implied_volatility_call-put` 水平差，因为这批已经显示子宇宙稳定性不足。
