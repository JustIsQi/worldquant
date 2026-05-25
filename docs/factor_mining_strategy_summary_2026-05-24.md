# 2026-05-24 因子挖掘策略总结

## 1. 今日目标与最终结果

今天的目标是“再挖 13 个因子”。按照项目规则，只有已经提交并且状态为 `ACTIVE`，且质量等级为 `AVERAGE`、`GOOD` 或 `EXCELLENT` 的因子才计数。

最终结果：完成 13 / 13 个 countable ACTIVE 因子。

- `AVERAGE`：11 个
- `GOOD`：2 个
- `EXCELLENT`：0 个
- 低等级或不明确等级：0 个计入目标

这次目标完成，但质量结构仍然偏向 `AVERAGE`。两个 `GOOD` 都来自增长分析师模型字段，说明分析师增长/盈利预期仍然是今天最有价值的信息源。

## 2. 开始时的账户背景

本轮开始前，`AGENTS.md` 中记录的累计提交结构是：

- `INFERIOR`：1
- `AVERAGE`：71
- `GOOD`：13
- `EXCELLENT`：2
- 合计：87

本轮新增 13 个 countable ACTIVE 后，累计结构更新为：

- `INFERIOR`：1
- `AVERAGE`：82
- `GOOD`：15
- `EXCELLENT`：2
- 合计：100

目标组合希望长期接近 `AVERAGE : GOOD : EXCELLENT = 5 : 4 : 1`。今天虽然完成数量，但新增结构是 `11 : 2 : 0`，仍然说明账户偏 AVERAGE，需要继续提高新信息源的占比，不能只靠同一批字段换 universe 或 neutralization。

## 3. 今日新挖出的 13 个因子

下面的指标含义：

- Sharpe：收益相对波动的稳定程度，越高越好。
- Fitness：WorldQuant 对收益、风险、换手等综合后的适应度，越高越好。
- Returns：回测年化收益。
- Turnover：换手率，越低通常越稳定，过高会增加交易成本风险。
- Margin：每单位交易带来的收益空间。

| # | Alpha id | 等级 | 表达式 | Universe / Neutralization / Decay / Truncation | Sharpe | Fitness | Returns | Turnover | Margin | 备注 |
|---|---|---|---|---|---:|---:|---:|---:|---:|---|
| 1 | `d5deWbaw` | AVERAGE | `0.65*group_rank(-one_year_ahead_eps_growth, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP1000 / SECTOR / 20 / 0.08 | 1.37 | 1.01 | 0.0681 | 0.0635 | 0.002144 | 直接 ACTIVE |
| 2 | `vRdaA8Zd` | AVERAGE | `0.65*group_rank(-mdl77_liquidityriskfactor_mad3yttmsale, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP1000 / SECTOR / 20 / 0.08 | 1.47 | 1.16 | 0.0772 | 0.0577 | 0.002678 | 直接 ACTIVE |
| 3 | `e7LevWRM` | GOOD | `0.65*group_rank(mdl77_2growthanalystmodel_qga_epscapex, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP3000 / SECTOR / 20 / 0.08 | 1.98 | 1.65 | 0.0865 | 0.0550 | 0.003148 | 直接 ACTIVE |
| 4 | `vRdabLjA` | AVERAGE | `0.65*group_rank(-two_year_relative_eps_growth, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP500 / MARKET / 20 / 0.08 | 1.71 | 1.43 | 0.0871 | 0.0640 | 0.002722 | 直接 ACTIVE |
| 5 | `1YJ686r6` | GOOD | `0.65*group_rank(-mdl77_2growthanalystmodel_qga_iarsales, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP3000 / SECTOR / 20 / 0.08 | 2.26 | 1.97 | 0.0949 | 0.0690 | 0.002750 | 直接 ACTIVE |
| 6 | `QPEmxGRQ` | AVERAGE | `0.65*group_rank(mdl77_2growthanalystmodel_qga_opmarginsales, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP3000 / SECTOR / 20 / 0.08 | 1.65 | 1.27 | 0.0743 | 0.0592 | 0.002512 | 直接 ACTIVE |
| 7 | `wpLwpdJ1` | AVERAGE | `0.65*group_rank(-mdl177_2_sensitivityfactor400_chgqtrepssurp, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP1000 / SECTOR / 20 / 0.08 | 1.77 | 1.29 | 0.0663 | 0.0767 | 0.001730 | 先 pending，后确认 ACTIVE |
| 8 | `9qJPYo9x` | AVERAGE | `0.65*group_rank(mdl77_2growthanalystmodel_qga_opmarginsales, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP500 / MARKET / 20 / 0.08 | 1.53 | 1.26 | 0.0846 | 0.0624 | 0.002711 | 提交后通过别名/确认看到 ACTIVE |
| 9 | `e7L8KOQz` | AVERAGE | `0.65*group_rank(-two_year_relative_eps_growth, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP200 / SECTOR / 20 / 0.08 | 1.46 | 1.29 | 0.0978 | 0.0678 | 0.002886 | TOP200 救回 |
| 10 | `gJxqPG2Q` | AVERAGE | `0.65*group_rank(mdl77_2growthanalystmodel2_qga_ltepssurprise, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP200 / SECTOR / 20 / 0.08 | 1.56 | 1.43 | 0.1052 | 0.0695 | 0.003027 | TOP200 救回 |
| 11 | `mLZ2rwq1` | AVERAGE | `0.65*group_rank(-mdl177_2_earningsqualityfactor_uar, subindustry)+0.35*group_rank(-ts_delta(vwap, 10), subindustry)` | TOP200 / SECTOR / 20 / 0.08 | 1.42 | 1.18 | 0.0857 | 0.0654 | 0.002623 | TOP200 救回 |
| 12 | `N1AWaopL` | AVERAGE | `0.65*group_rank(-mdl77_2historicalgrowthfactor_cv4qsales3y, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)` | TOP200 / SECTOR / 20 / 0.08 | 1.32 | 1.12 | 0.0896 | 0.0622 | 0.002880 | TOP200 高指标剩余候选 |
| 13 | `58M7jwXn` | AVERAGE | `0.70*group_rank(-ts_delta(mdl77_2liquidityriskfactor_monchgsip, 90), subindustry)+0.30*group_rank(-ts_delta(vwap, 10), subindustry)` | TOP200 / SECTOR / 20 / 0.08 | 1.31 | 1.08 | 0.0954 | 0.1393 | 0.001370 | 换手偏高但仍通过 |

## 4. 成功因子的经济直觉

`d5deWbaw` 使用未来一年 EPS 增长预期的反向信号。EPS 是每股盈利，分析师预测越乐观时，市场有时已经提前定价；反向做法可能捕捉“预期过热后的回落”。另一边的交易者可能是追逐高增长故事的投资者。

`vRdaA8Zd` 使用销售稳定性相关字段 `mad3yttmsale` 的反向信号。这个字段衡量过去三年销售的平均绝对波动。销售波动越大，经营质量可能越不稳定；反向排名偏向销售更稳定的公司。另一边可能是只看短期增长、不关心收入质量的资金。

`e7LevWRM` 使用 `qga_epscapex`，即 EPS 增长和资本开支之间的联系。直觉是：如果盈利增长和资本投入匹配得更好，增长可能更真实、更可持续。它拿到 GOOD，说明该信息源今天很强。

`vRdabLjA` 和 `e7L8KOQz` 都使用未来两年相对 EPS 增长的反向信号，但分别在 TOP500/MARKET 和 TOP200/SECTOR 设置下通过。这里的逻辑类似：过高的两年增长预期可能已经被价格反映，反向信号捕捉预期修正。

`1YJ686r6` 使用 `qga_iarsales` 的反向信号。这个字段大致描述存货和应收账款相对销售的联系。应收账款或存货相对销售异常可能暗示收入质量问题；反向信号偏向更干净的销售质量。它是今天最强的 GOOD。

`QPEmxGRQ` 和 `9qJPYo9x` 使用 `qga_opmarginsales`，即经营利润率和销售之间的关系。销售增长如果能转化成经营利润率改善，可能代表公司经营杠杆更好；如果只是卖得多但利润不跟上，质量较差。

`wpLwpdJ1` 使用真实盈利惊喜变化 `chgqtrepssurp` 的反向信号。盈利惊喜是实际盈利超过或低于预期的程度。反向通过说明在某些 universe 下，市场可能对近期惊喜变化反应过度。

`gJxqPG2Q` 使用长期 EPS 惊喜 `qga_ltepssurprise`。长期盈利预期的偏差比单季度 surprise 更慢，可能和机构调仓周期相关，所以在 TOP200/SECTOR 下仍能通过。

`mLZ2rwq1` 使用 `uar`，即应收账款异常变化的反向信号。应收账款异常上升可能意味着收入确认质量变差，反向信号偏向会计质量更稳的公司。

`N1AWaopL` 使用 `cv4qsales3y`，即多年销售增长稳定性/变异性相关信号的反向版本。它偏向历史销售增长更稳定的股票。

`58M7jwXn` 使用短兴趣变化 `monchgsip` 的 90 日变化反向信号。短兴趣上升通常代表市场借券做空需求变强；反向信号可能捕捉做空拥挤后回补或悲观情绪过度。

## 5. 搜索路径

第一批 `v1` 使用稳定性、修正、期权和做空字段，在 TOP500/SECTOR 下没有产生 ACTIVE，说明宽泛新字段直接套模板效果不够。

第二批 `v2` 回到已证明的信息源，在 TOP1000/SECTOR 下得到 `d5deWbaw` 和 `vRdaA8Zd`。TOP1000/INDUSTRY 随后没有新增，说明 INDUSTRY 中性化没有改善这些字段。

第三批 `v3` 在 TOP3000/SECTOR 和 TOP500/MARKET 上测试高指标矩阵。`qga_epscapex` 产生 GOOD；`two_year_relative_eps_growth` 在 TOP500/MARKET 通过。

第四批 `v4` 转向增长分析师模型、盈利质量和敏感度字段。这里产出 `1YJ686r6`、`QPEmxGRQ` 和后来确认的 `wpLwpdJ1`。这说明增长分析师模型字段是当天主线。

第五批 `v5` 继续围绕已工作的增长分析师字段做 TOP500/MARKET 和 TOP500/SECTOR 设置。只新增了 `9qJPYo9x`，之后同类变体大量自相关。

第六批 `v6` 尝试新鲜的 value-momentum 模块、earning-momentum 模块和 2400 option/sensitivity 字段。结果几乎全部 LOW_SHARPE/LOW_FITNESS，说明这些模块今天不适合作为主力。

第七批 `v7` 改为 TOP200/SECTOR 窄 universe 救援。这里新增 `e7L8KOQz`、`gJxqPG2Q`、`mLZ2rwq1`，证明窄 universe 能降低部分自相关压力，但 TOP200/MARKET 和 TOP200/INDUSTRY 没有继续成功。

第八批 `v8` 选择之前高指标但未在 TOP200 试过的剩余候选，最终新增 `N1AWaopL` 和 `58M7jwXn`，完成 13 个目标。

## 6. 失败分析

今天失败最多的是 `SELF_CORRELATION`。日志中包含大量同字段、同方向、相近权重或相近 universe 的候选。尤其是 `qga_epscapex`、`qga_opmarginsales`、`qga_ltepssurprise`、`one_year_ahead_eps_growth`、`two_year_relative_eps_growth` 和 `mad3yttmsale`，一旦有一个版本 ACTIVE，后续相邻变体很容易被判自相关。

`LOW_FITNESS` 和 `LOW_SHARPE` 也很常见。新尝试的 value-momentum 模块、部分 2400 期权/敏感度字段，在 TOP500/MARKET 下大多连基础指标都不过，说明不是所有“新字段”都有可交易信号。

`LOW_SUB_UNIVERSE_SHARPE` 在若干高 Sharpe 候选上出现，代表整体表现好，但子 universe 稳定性不够。对这种情况，换 universe 有时有用，但今天很多时候换设置后又变成自相关。

`HIGH_TURNOVER` 今天不是主要失败项，但 `58M7jwXn` 的 turnover 为 0.1393，高于其他成功因子。后续短兴趣变化类信号要注意换手，不要继续增加短窗口价格项。

## 7. 对当前市场/数据状态的学习

增长分析师字段仍然有效，但已经开始拥挤。`qga_epscapex`、`qga_iarsales`、`qga_opmarginsales` 和 `qga_ltepssurprise` 可以出 GOOD 或高质量 AVERAGE，但同族变体很快触发自相关。

窄 universe 是有效的最后救援手段。TOP200/SECTOR 帮助 `two_year_relative_eps_growth`、`qga_ltepssurprise`、`uar`、`cv4qsales3y` 和 `monchgsip` 通过。不过这更像设置救援，不是全新的 alpha 发现，不能长期依赖。

新模块级 value-momentum 信号今天表现弱。虽然它们听起来经济含义完整，但实际 Sharpe/Fitness 不够，说明模型组合字段可能过于泛化，或者与现有提交集没有形成可用边际。

短兴趣变化还能提供差异化，但容易受自相关和换手影响。`monchgsip` 最终通过一个 TOP200/SECTOR 版本，可作为下次继续研究的线索。

## 8. 下一步建议

优先尝试以下方向：

- 增长分析师模型的未充分使用字段，但不要再只调 `qga_epscapex` 和 `qga_opmarginsales` 权重。
- 低使用的 earnings surprise / revision 字段，例如 `mdl177_2_earningmomentumfactor400_numrevq1`、`numrevy1`、`hlep`、`sue`、`sucf`，但先做小规模测试。
- 短兴趣变化和借券需求字段，例如 `monchgsip`、`chg12msip`、`dmd_conc`、`dmd_supply`，优先用更慢的 60 到 120 日变化，降低 turnover。
- 会计质量字段中的应收、存货、销售质量方向，例如 `uar`、`uaccl`、`salerec`、`saleeps`，但要换数据源或 universe，避免和已有会计质量因子过近。

可以继续使用的模板：

```text
0.65*group_rank(new_signal, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)
```

```text
0.70*group_rank(ts_delta(slow_signal, 90), subindustry)+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

```text
trade_when(volume>adv20, 0.70*group_rank(new_signal, subindustry)+0.30*group_rank(-ts_delta(vwap, 10), subindustry), -1)
```

## 9. 下一次应避免的方向

不要继续围绕以下表达式做小权重微调：

- `qga_epscapex`
- `qga_iarsales`
- `qga_opmarginsales`
- `qga_ltepssurprise`
- `one_year_ahead_eps_growth`
- `two_year_relative_eps_growth`
- `mad3yttmsale`

这些字段今天已经贡献了因子，但后续相邻版本高度自相关。下一次如果继续使用它们，应该改变信息结构，例如改成更长窗口变化、与不同经济含义字段组合，或者干脆换数据源。

也不建议继续大批量跑 value-momentum module 级字段。今天它们主要是 LOW_SHARPE/LOW_FITNESS，说明短期内产出概率低。

TOP200/SECTOR 可以作为救援设置，但不能作为默认主策略。它能完成数量目标，却会让新增因子更像已有信号的窄 universe 版本，长期不利于提高 GOOD/EXCELLENT 比例。
