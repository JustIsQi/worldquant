# 2026-05-22 因子挖掘策略总结

## 1. 今日目标和最终结果

今日目标是“再挖 10 个因子”。按照当前规则，只有新提交并且最终为 ACTIVE，且质量等级为 `AVERAGE`、`GOOD`、`EXCELLENT` 的 alpha 才计入目标；`INFERIOR`、更低等级、旧的 `ALREADY_ACTIVE` 都不计数。

最终结果：

- 新增可计数 ACTIVE alpha：10 个。
- 等级分布：GOOD 2 个，AVERAGE 8 个。
- 低质量 ACTIVE：0 个计入目标。
- 已启动候选均已收尾：最后一个未写入主汇总的 `KPk0p9op` 已手动补提确认，最终 SELF_CORRELATION 失败。

更新后的账户累计统计：

```text
INFERIOR : AVERAGE : GOOD : EXCELLENT = 1 : 61 : 13 : 2
Total = 77
```

## 2. 开始时的背景

本日开始前，`AGENTS.md` 记录的累计提交为：

```text
INFERIOR : AVERAGE : GOOD : EXCELLENT = 1 : 53 : 11 : 2
Total = 67
```

账户已经明显偏 AVERAGE-heavy。也就是说，已经有很多刚过线的普通因子，但 GOOD 和 EXCELLENT 的比例不够高。因此今天不能只追求数量，还要优先寻找更可能产出 GOOD 的信息源。

不过实际挖掘过程中，强信号家族大多非常拥挤。EPS、盈利质量、地理收入暴露、历史增长稳定性等方向都能跑出不错 Sharpe/Fitness，但提交时经常因为 SELF_CORRELATION 被拒绝。最后真正完成目标，主要依靠 TOP500/TOP500+INDUSTRY 设置下的短借和 short-interest 变化类字段。

## 3. 今日新增 ACTIVE Alpha 明细

| Alpha id | Grade | Expression | Universe | Neutralization | Decay | Truncation | Sharpe | Fitness | Returns | Turnover | Margin |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `ZYr6kPY0` | AVERAGE | `0.70*group_rank(ts_delta(mdl177_devnorthamericashortsentimentfactor_dmd_supply, 60), subindustry)+0.30*group_rank(-ts_delta(vwap, 10), subindustry)` | TOP500 | MARKET | 20 | 0.08 | 1.29 | 1.16 | 0.1003 | 0.0777 | 0.002579 |
| `omV76z2v` | AVERAGE | `0.65*group_rank(-mdl77_valuemomemtummodel_earningsexpectationmodule, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP3000 | MARKET | 20 | 0.08 | 1.90 | 1.23 | 0.0525 | 0.0793 | 0.001323 |
| `1YJe233X` | AVERAGE | `0.65*group_rank(-ts_delta(mdl77_voldiff_pc, 20), subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP3000 | SUBINDUSTRY | 20 | 0.08 | 1.84 | 1.26 | 0.0884 | 0.1900 | 0.000930 |
| `LLkjdGNL` | GOOD | `0.65*group_rank(-north_america_sales_exposure, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP3000 | MARKET | 20 | 0.05 | 1.76 | 1.67 | 0.1120 | 0.0564 | 0.003976 |
| `QPEJ9nop` | AVERAGE | `trade_when(volume>adv20, 0.70*group_rank(-north_america_sales_exposure, subindustry)+0.30*group_rank(-ts_delta(vwap, 10), subindustry), -1)` | TOP3000 | MARKET | 20 | 0.05 | 1.57 | 1.40 | 0.1000 | 0.0402 | 0.004971 |
| `blvkzlmM` | AVERAGE | `0.70*group_rank(ts_delta(mdl177_devnorthamericashortsentimentfactor_dmd_supply, 90), subindustry)+0.30*group_rank(-ts_delta(vwap, 10), subindustry)` | TOP500 | MARKET | 20 | 0.08 | 1.48 | 1.41 | 0.1136 | 0.0725 | 0.003133 |
| `88noXeMX` | AVERAGE | `0.70*group_rank(-ts_delta(mdl77_2liquidityriskfactor_monchgsip, 60), subindustry)+0.30*group_rank(-ts_delta(vwap, 10), subindustry)` | TOP500 | MARKET | 20 | 0.08 | 1.42 | 1.07 | 0.0756 | 0.1339 | 0.001129 |
| `kqQ7YnrK` | GOOD | `0.70*group_rank(ts_delta(mdl177_devnorthamericashortsentimentfactor_dmd_supply, 90), subindustry)+0.30*group_rank(-ts_delta(vwap, 10), subindustry)` | TOP500 | INDUSTRY | 20 | 0.08 | 1.74 | 1.62 | 0.1085 | 0.0767 | 0.002830 |
| `0mzlL3vK` | AVERAGE | `0.70*group_rank(-ts_delta(mdl77_2liquidityriskfactor_monchgsip, 90), subindustry)+0.30*group_rank(-ts_delta(vwap, 10), subindustry)` | TOP500 | INDUSTRY | 20 | 0.08 | 1.55 | 1.19 | 0.0794 | 0.1347 | 0.001179 |
| `lerqYJ8O` | AVERAGE | `0.65*group_rank(-ts_delta(mdl77_2liquidityriskfactor_monchgsip, 60), subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP500 | INDUSTRY | 20 | 0.08 | 1.66 | 1.26 | 0.0830 | 0.1431 | 0.001160 |

## 4. 每个成功因子的经济直觉

`ZYr6kPY0`、`blvkzlmM`、`kqQ7YnrK` 都使用 `dmd_supply` 的时间变化。可以把它理解为借券市场里“借券需求或供给结构的变化”。如果做空需求、可借供给或借券紧张程度在变化，说明某些资金正在改变对股票的看法。市场价格有时不会马上完全反映这种借券市场信息。

`kqQ7YnrK` 是同一信息源在 TOP500 + INDUSTRY 设置下的版本，等级为 GOOD。它说明今天真正有效的去相关方式不是继续调 0.70/0.75 小权重，而是改变 universe 和 neutralization，让组合暴露结构发生实质变化。

`88noXeMX`、`0mzlL3vK`、`lerqYJ8O` 使用 `monchgsip` 的负向变化。`sip` 可以粗略理解为 short interest 相关比例，`monchgsip` 是月度变化。取负号后，因子偏好 short interest 变化压力下降或反向的一侧。对手方可能是继续跟随拥挤空头、或者没有及时识别做空压力缓解的资金。

`LLkjdGNL` 和 `QPEJ9nop` 使用 `north_america_sales_exposure`。这是公司收入对北美地区的暴露。这里取负号，说明在当前样本和设置下，低北美收入暴露或较少受北美单一市场驱动的公司表现更好。`QPEJ9nop` 加了 `trade_when(volume>adv20, ..., -1)`，意思是只在成交量高于 20 日均量时持仓，否则退出，降低了换手和重叠。

`omV76z2v` 使用 earnings expectation module 的反向信号。它不是单个 EPS surprise 字段，而是一个模型模块，综合了盈利预期相关信息。反向通过，说明当前环境中“市场预期较热”的股票可能已经被充分定价，而预期较低的一侧反而更有后续修复空间。

`1YJe233X` 使用 `voldiff_pc` 的 20 日变化，属于期权或 put/call 成交结构相关信息。期权市场参与者常常比股票现货市场更快表达风险偏好变化，因此这类信号可能捕捉到期权端情绪变化还没有完全传导到股票价格的阶段。

## 5. 今日搜索路径

第一阶段继续从低使用度 EPS、analyst revision 和 earnings quality 字段开始。很多候选的 Sharpe/Fitness 很强，例如 `one_quarter_ahead_eps_growth`、`revision_fiscal_q1_eps_forecast`、`mdl77_2growthanalystmodel_qga_epstrend`，但提交时大多 SELF_CORRELATION 失败。结论是这类信息源仍有效，但账户里已经拥挤。

第二阶段尝试 option、short interest、borrow、sales exposure 和低使用度模块。`omV76z2v` 从 earnings expectation module 反向通过，`1YJe233X` 从 `voldiff_pc` 的变化通过，说明新模块和期权成交结构仍能贡献低相关 alpha。

第三阶段重点尝试低截断 `truncation=0.05`。这个改变让 `north_america_sales_exposure` 方向产出 `LLkjdGNL` 和 `QPEJ9nop`。低截断的作用是削弱极端持仓权重，可能降低和历史 alpha 的组合重叠。

第四阶段继续沿低截断和 decay 30 扩展，但 v16、v17 说明地理暴露已经很快拥挤。`emea_sales_exposure`、`latin_america_sales_exposure`、`asia_pacific_sales_exposure` 以及 sensitivity 模型字段，多数不是指标不够就是被 `LLkjdGNL/QPEJ9nop` 等新提交挤掉。

第五阶段转向 TOP500 的短借变化。`blvkzlmM` 使用 `dmd_supply` 90 日变化直接通过，`88noXeMX` 使用 `monchgsip` 60 日反向变化通过。随后切到 TOP500 + INDUSTRY，`kqQ7YnrK`、`0mzlL3vK`、`lerqYJ8O` 补齐最后 3 个。

## 6. 失败分析

SELF_CORRELATION 是今天最大的失败原因。强候选经常不是没有预测力，而是和已有 ACTIVE alpha 太像。例如 `dmd_supply` 的 120 日变化、`dmd_supply` 90 日 close 稳定器、`monchgsip` 60 日 MARKET 版本，都因为和当天或历史已提交 alpha 高相关而被拒绝。

LOW_FITNESS 和 LOW_SHARPE 主要出现在以下几类：

- EMEA、Latin America、Asia Pacific 静态 sales exposure。
- 一些 TOP500 短借字段，例如 `tni_ths`、`benchmark_fee` 在 TOP500 下指标明显不足。
- 信用、股息、管理信号和普通 value analyst 模块，很多只有 0.x Sharpe/Fitness。

LOW_SUB_UNIVERSE_SHARPE 不是主导问题，但在部分期权、股息估计和 TOP500 short-interest 候选中出现。说明有些候选整体看似还行，但在子股票池里不稳定。

HIGH_TURNOVER 没有成为硬失败，但 `voldiff_pc` 和 `monchgsip` 的换手都偏高。`1YJe233X` turnover 0.19，`0mzlL3vK` 和 `lerqYJ8O` 也在 0.13 到 0.14 附近。后续若继续此方向，最好尝试更长窗口或更高 decay。

## 7. 今日学到的市场和数据状态

当前账户对 EPS、earnings surprise、earnings quality 和地理收入暴露都已经很拥挤。强指标不等于可提交，尤其是同一字段家族里做小权重和小窗口变化，很容易只是在复制已有持仓。

真正有帮助的结构变化有两个：

- 改 universe：TOP500 让 `dmd_supply` 变化产生了新的可提交空间。
- 改 neutralization：TOP500 + INDUSTRY 让同一短借信息源再产出 GOOD 和 AVERAGE。

低截断有效，但窗口很短。`truncation=0.05` 救出了 `north_america_sales_exposure`，但相邻地理字段随后迅速自相关。因此低截断是工具，不是信息源本身。

## 8. 下一步应该尝试什么

优先继续短借和 short-interest 的结构性变体，而不是简单权重微调：

```text
0.70*group_rank(ts_delta(mdl177_devnorthamericashortsentimentfactor_dmd_supply, 90), subindustry)
+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

可以尝试：

- TOP500 + SECTOR neutralization。
- TOP1000 + INDUSTRY neutralization。
- decay 30 或 40，观察能否降低 turnover 和 self-correlation。
- `dmd_supply` 与非价格、非 sales-exposure 的慢速质量锚混合。

继续探索 `monchgsip`，但要控制换手：

```text
0.75*group_rank(-ts_delta(mdl77_2liquidityriskfactor_monchgsip, 120), subindustry)
+0.25*group_rank(-ts_delta(vwap, 10), subindustry)
```

还可以尝试：

- `mdl177_liquidityriskfactor_monchgsip_alt` 的 TOP500 + SECTOR 版本。
- `trade_when(volume>adv20, ...)` 只作为少量测试，不要机械套用。
- 将 close 5 日稳定器改成更慢的 `-ts_delta(vwap, 20)` 或降低价格项权重。

## 9. 下一步应该避免什么

避免继续在以下方向上做小权重重复：

- `north_america_sales_exposure` 的 0.65/0.70/0.75 小权重变化。
- `mdl77_2growthanalystmodel_qga_epstrend`、`long_term_growth_forecast_2`、`volatility_adjusted_three_year_eps_growth` 的同族反复提交。
- `dmd_supply` 90 日在同一 TOP500 + MARKET 或 TOP500 + INDUSTRY 设置下的小权重变化，因为已经直接撞到 `blvkzlmM` 或 `kqQ7YnrK`。
- `monchgsip` 60 日 MARKET 版本的小变体，因为 `88noXeMX` 已经占住这个位置。

下一轮如果目标仍是质量，应优先问：“这个候选和今天这 10 个新 ACTIVE 的信息源、universe、neutralization 是否真正不同？”如果答案只是权重或窗口略微不同，就很可能再次失败于 SELF_CORRELATION。
