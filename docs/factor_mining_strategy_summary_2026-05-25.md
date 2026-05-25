# 2026-05-25 因子挖掘策略总结

## 1. 今日目标和最终结果

今日目标是“再挖 5 个因子”。按照项目规则，只有已经提交成功、状态为 `ACTIVE`，并且质量等级为 `AVERAGE`、`GOOD`、`EXCELLENT` 的新因子才计入目标。

最终结果：完成目标，共新增 5 个 countable ACTIVE 因子。

- `GOOD`: 1 个
- `AVERAGE`: 4 个
- `EXCELLENT`: 0 个

今日新增后，当前累计提交统计更新为：

- `INFERIOR`: 1
- `AVERAGE`: 86
- `GOOD`: 16
- `EXCELLENT`: 2
- 合计: 105

这说明因子库仍然偏 `AVERAGE`，后续不应该只追求数量，而要继续优先寻找更独立、更有机会成为 `GOOD` 或 `EXCELLENT` 的信息源。

## 2. 开始时的背景

开始时的累计统计是：

- `INFERIOR`: 1
- `AVERAGE`: 82
- `GOOD`: 15
- `EXCELLENT`: 2
- 合计: 100

前几天的经验显示，以下方向已经比较拥挤：

- `rel5yfwdep`、短期价格反转、单纯权重微调很容易触发 `SELF_CORRELATION`。
- 短融、借券、期权、盈利惊喜、分析师修正仍然有效，但同一个字段族成功一两次之后会迅速变拥挤。
- 2026-05-24 新增了较多成长分析师和增长质量类因子，今天不能继续只在同一批表达式附近调权重。

因此今天的主线是：先找新的信息源，只有在指标明显改善时才增加稳定组件。

## 3. 今日新增的 5 个因子

### 3.1 `vRdzrgb3` - GOOD

表达式：

```text
0.70*group_rank(ts_delta(mdl177_devnorthamericashortsentimentfactor_dmd_conc, 120), subindustry)+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

设置：

- Universe: `TOP200`
- Neutralization: `SECTOR`
- Decay: `20`
- Truncation: `0.08`
- 状态: 立即提交后 `ACTIVE`
- Grade: `GOOD`

指标：

- Sharpe: `1.60`
- Fitness: `1.69`
- Returns: `0.1400`
- Turnover: `0.0930`
- Margin: `0.003010`

经济含义：

这个因子使用的是空头需求集中度的 120 日变化。简单理解，如果做空需求在少数股票上变得更集中，市场可能正在更一致地表达负面观点。因子不是直接使用原始水平，而是看较长窗口的变化，减少了短期噪声。另一个小组件 `-ts_delta(vwap, 10)` 相当于加入温和的短期反转，帮助降低拥挤和换手。交易对手可能是反应较慢的多头资金，或者被迫跟随基本面坏消息调仓的投资者。

### 3.2 `1YJmN7Qk` - AVERAGE

表达式：

```text
0.70*group_rank(ts_delta(mdl177_5shortsentimentfactor_conc_ratio, 120), subindustry)+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

设置：

- Universe: `TOP500`
- Neutralization: `MARKET`
- Decay: `20`
- Truncation: `0.08`
- 状态: 立即提交后 `ACTIVE`
- Grade: `AVERAGE`

指标：

- Sharpe: `1.40`
- Fitness: `1.02`
- Returns: `0.0664`
- Turnover: `0.0825`
- Margin: `0.001610`

经济含义：

这个因子也来自空头情绪，但使用的是 short concentration ratio，也就是空头仓位集中程度。它捕捉的是空头参与者是否在更集中地押注某些股票。和第一个因子相比，Universe 更宽、Neutralization 更粗，因此质量只有 `AVERAGE`，但仍然提供了一个和已有组合不完全相同的短融信息角度。

### 3.3 `kqQmGVoz` - AVERAGE

表达式：

```text
0.70*group_rank(ts_delta(mdl177_devnorthamericashortsentimentfactor_act_util, 120), subindustry)+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

设置：

- Universe: `TOP200`
- Neutralization: `SECTOR`
- Decay: `20`
- Truncation: `0.08`
- 状态: 立即提交后 `ACTIVE`
- Grade: `AVERAGE`

指标：

- Sharpe: `1.45`
- Fitness: `1.40`
- Returns: `0.1162`
- Turnover: `0.0738`
- Margin: `0.003148`

经济含义：

这个因子使用的是实际借券利用率变化。借券利用率可以理解为空头或借券需求相对于可借股票供给的紧张程度。利用率上升通常说明市场上愿意做空或需要借券的人变多，可能对应未来收益压力。它和前两个因子同属短融信息，但字段含义不同：一个看需求集中度，一个看整体利用率。

### 3.4 `A1kOK8rg` - AVERAGE

表达式：

```text
0.70*group_rank(-ts_delta(mdl77_earningsqualityfactor_rau, 60), subindustry)+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

设置：

- Universe: `TOP200`
- Neutralization: `MARKET`
- Decay: `20`
- Truncation: `0.08`
- 状态: 初始提交后等待 `SELF_CORRELATION` 检查，随后确认 `ACTIVE`
- Grade: `AVERAGE`

指标：

- Sharpe: `1.35`
- Fitness: `1.11`
- Returns: `0.0845`
- Turnover: `0.0674`
- Margin: `0.002507`

经济含义：

`RAU` 是 unexpected change in accounts receivable，可以粗略理解为“应收账款的异常变化”。应收账款异常上升有时意味着收入质量变差，因为公司确认了收入但现金还没有收回来。这里使用负号和 60 日变化，等于偏好应收账款压力下降、财务质量改善的公司。这个因子和短融类信号不同，属于会计质量方向。

### 3.5 `QPE5V26M` - AVERAGE

表达式：

```text
0.65*group_rank(mdl77_oearningmomentumfactor_ratrev6m, subindustry)+0.35*group_rank(-ts_delta(vwap, 10), subindustry)
```

设置：

- Universe: `TOP500`
- Neutralization: `MARKET`
- Decay: `20`
- Truncation: `0.08`
- 状态: 立即提交后 `ACTIVE`
- Grade: `AVERAGE`

指标：

- Sharpe: `1.48`
- Fitness: `1.14`
- Returns: `0.0739`
- Turnover: `0.0657`
- Margin: `0.002251`

经济含义：

这个因子使用的是 6 个月分析师评级修正。对初学者来说，可以把它理解为“分析师整体看法是否在变好”。评级修正比单次评级更有用，因为它反映的是方向变化，而不是静态观点。市场有时不会立刻完全吸收分析师观点变化，尤其是在组合经理需要等正式报告、委员会或风控流程之后才调仓时，因子就可能捕捉到这种滞后。

## 4. 今日搜索路径

### 第一阶段：低使用率盈利修正、短融、期权

最开始测试了盈利修正、短融集中度、期权偏度等字段。盈利修正和期权多数没有通过基础指标，短融集中度方向最有效。

成功结果：

- `mdl177_devnorthamericashortsentimentfactor_dmd_conc`
- `mdl177_5shortsentimentfactor_conc_ratio`

失败或偏弱方向：

- 多个 earnings momentum 字段虽然有少数高 Sharpe 模拟结果，但提交阶段容易遇到 self-correlation 或低 Fitness。
- 期权 implied volatility 和 skew 变体换手偏高或 Fitness 不稳定。

### 第二阶段：短融利用率与相邻借券字段

在短融集中度成功后，继续尝试了 `act_util`、`util`、`days_to_cover`、`onloan_conc`、`lend_supply`、`sht_int` 等相邻字段。

成功结果：

- `mdl177_devnorthamericashortsentimentfactor_act_util`

失败经验：

- `days_to_cover`、`inv_conc`、`onloan_conc`、`lend_supply` 等大多基础指标不够强。
- 若继续在同一短融字段族里调窗口和权重，self-correlation 风险明显上升。

### 第三阶段：盈利质量、RAU、salerec

随后切到会计质量方向，尤其是应收账款异常变化和销售/应收关系。

成功结果：

- `mdl77_earningsqualityfactor_rau` 的 60 日反向变化最终确认 `ACTIVE`。

失败经验：

- `mdl77_oearningsqualityfactor_rau`、`mdl77_2earningsqualityfactor_rau`、`mdl77_400_rau` 等别名或近邻字段模拟指标不错，但提交后基本都因 `SELF_CORRELATION` 被拒。
- `salerec` 正向变化也有可提交指标，但最终同样被 `SELF_CORRELATION` 拒绝。

### 第四阶段：地域/销售暴露与敏感度字段

为摆脱 RAU/salerec 拥挤，测试了 EMEA、Latin America、sensitivity factor 里的 sales exposure。

结果：

- 多个候选模拟 Sharpe 和 Fitness 达标，例如 EMEA sales exposure 与 sensitivity factor aliases。
- 但提交后全部在最终确认中被 `SELF_CORRELATION` 拒绝。

结论：

这些字段过去已经贡献过可用因子，现在同类形状再次提交的相关性太高。后续不应继续在 EMEA/Latin America sales exposure 上调符号或窗口。

### 第五阶段：分析师价值模型和评级修正

最后切到更独立的分析师价值、评级修正和 forecast dispersion 字段。大多数 value analyst rank 字段基础指标偏弱，但 `ratrev6m` 给出了可提交且最终 `ACTIVE` 的结果。

成功结果：

- `mdl77_oearningmomentumfactor_ratrev6m`

失败经验：

- 多数 `qva_*` 字段在 `TOP500/MARKET` 下 Sharpe 和 Fitness 不足。
- `strevconf`、`stockrating`、`spe1yfvc` 在本轮设置下没有达到提交质量。

## 5. 失败分析

今日 `submit_summary.csv` 中总共记录了 315 条模拟/提交结果；另外对 pending 提交做了 24 条后续确认记录。主要失败类型：

- `LOW_SHARPE`: 266 次
- `LOW_FITNESS`: 265 次
- `LOW_SUB_UNIVERSE_SHARPE`: 20 次
- 明确记录的 `SELF_CORRELATION`: 34 次，其中后续确认阶段有 22 条最终被拒
- 另有大量候选在模拟结果里显示 `SELF_CORRELATION` pending，但因为同时有低 Sharpe 或低 Fitness，所以没有进入提交。

`SELF_CORRELATION` 的核心原因：

1. 短融字段内部的信息高度相近。`dmd_conc`、`conc_ratio`、`act_util` 成功后，继续测试 `util`、`onloan_conc`、`lend_supply` 容易和已有短融因子重叠。
2. RAU 字段的多个别名本质上是同一会计信息源。即使表达式换了字段名，平台仍会识别出相关性。
3. 地域销售暴露类字段过去已经有成功因子，今天用同类 `ts_delta + short reversal` 模板再次提交，相关性空间不够。

低 Fitness / 低 Sharpe 的核心原因：

1. 很多 value analyst rank 字段是慢变量，和 `MARKET` neutralization 搭配后横截面解释力不足。
2. 期权和短期情绪字段有时收益强但换手或子宇宙稳定性不够。
3. 单纯把字段放进 `group_rank(field, subindustry)`，如果字段本身覆盖率低或更新慢，通常需要更合适的窗口变换，而不是直接提交。

## 6. 今日对市场和数据状态的理解

今天最重要的观察是：平台当前仍然接受“短融/借券需求变化”类新信息，但只接受真正改变字段含义或覆盖面的版本。只要进入同一字段族的别名和小窗口变化，相关性检查会很快变严格。

第二个观察是，会计质量类字段仍可用，但 RAU 只能算一次主要成功。后续继续提交 RAU、UAR、salerec 的别名，大概率会被判为重复。

第三个观察是，分析师评级修正仍有空间。`ratrev6m` 的成功说明，市场对分析师评级变化仍有滞后吸收，但这个方向不能只测试静态 `stockrating`，更应该看“变化”或“修正”。

## 7. 下一步建议

优先尝试：

```text
0.65*group_rank(mdl77_oearningmomentumfactor_ratrev6m, subindustry)+0.35*group_rank(-ts_delta(vwap, 10), subindustry)
```

的相邻但不重复方向，例如：

- `mdl77_ratrev6m`
- `mdl77_2earningmomentumfactor400_ratrev6m`
- `mdl177_2_globaldevnorthamerica_v502_ratrev6m`
- `mdl77_2gdna_ratrev6m`

但不要只改 0.65/0.35 权重。更合理的是改变：

- Universe: `TOP200`、`TOP1000`
- Neutralization: `SECTOR` 或 `INDUSTRY`
- 变换: `ts_delta(field, 60)`、`ts_rank(field, 120)`、`ts_zscore(field, 120)`

也可以继续探索低使用率但经济意义清晰的字段：

- 分析师修正置信度：`mdl77_2put_put_strevconf`
- FY1/FY2 预测分歧：`mdl77_oearningmomentumfactor_spe1yfvc`
- 长期增长变化：`mdl177_earningmomentumfactor_chg6mltg`
- 现金流与盈利质量：`mdl77_2mqf_cfroi`、`mdl77_2mqf_ocfroi`
- 价值质量组合：`mdl77_2valueanalystmodel_qva_earnquality`，但需要换成更慢的 `ts_rank` 或行业中性设置

推荐模板：

```text
0.70*group_rank(ts_delta(new_revision_signal, 60), subindustry)
+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

```text
0.65*group_rank(ts_rank(new_quality_signal, 120), subindustry)
+0.35*group_rank(-ts_delta(vwap, 10), subindustry)
```

```text
0.60*group_rank(new_revision_signal, subindustry)
+0.40*group_rank(-ts_delta(close, 5), subindustry)
```

## 8. 下一步应避免

短期内应避免：

- 继续提交 RAU、UAR、salerec 的别名版本。
- 继续围绕今天三个短融成功因子做窗口 90/120/150/180 的小范围扫参。
- 继续测试 EMEA/Latin America sales exposure 的同形状表达式。
- 只对已成功表达式做 0.65、0.70、0.75 的权重微调。
- 在 `rel5yfwdep` 或纯价格反转上寻找“救场”因子。

如果下一次目标仍是数量型目标，可以接受 `AVERAGE`，但需要至少每 1-2 个成功因子切换一次信息源。如果目标是提高组合质量，则应把提交门槛提高到 Sharpe > 1.50、Fitness > 1.15，并优先找自相关空间更大的字段族。
