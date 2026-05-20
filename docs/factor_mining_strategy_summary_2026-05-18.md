# 2026-05-18 因子挖掘策略复盘

## 1. 今日目标与最终结果

本轮目标是“今天再挖 6 个因子”。这里把目标解释为：在本轮会话中新增 6 个已经提交并确认 `ACTIVE` 的 alpha，而不是只找到回测指标合格的候选。

最终完成结果：新增 6 个 `ACTIVE` alpha，全部为 `AVERAGE` 等级。

本轮新增 alpha：

| alpha id | grade | Sharpe | Fitness | Returns | Turnover | Margin | 状态 |
|---|---:|---:|---:|---:|---:|---:|---|
| `P0n5YEv7` | AVERAGE | 1.68 | 1.34 | 0.0797 | 0.1000 | 0.001594 | ACTIVE |
| `le7g3obA` | AVERAGE | 1.90 | 1.50 | 0.0780 | 0.1012 | 0.001541 | ACTIVE |
| `zq5AkwRR` | AVERAGE | 1.74 | 1.17 | 0.0577 | 0.1274 | 0.000906 | ACTIVE |
| `88OGl2JV` | AVERAGE | 1.49 | 1.07 | 0.0647 | 0.1052 | 0.001230 | ACTIVE |
| `YPNl5wx6` | AVERAGE | 1.70 | 1.06 | 0.0657 | 0.1690 | 0.000778 | ACTIVE |
| `j2nVYNLE` | AVERAGE | 1.86 | 1.31 | 0.0621 | 0.1022 | 0.001214 | ACTIVE |

所有新增 alpha 的共同设置：

```text
region = USA
universe = TOP3000
delay = 1
decay = 10
neutralization = SUBINDUSTRY
truncation = 0.08
pasteurization = ON
nanHandling = ON
language = FASTEXPR
```

## 2. 起始与结束组合状态

本轮开始时，`AGENTS.md` 中记录的组合统计是：

```text
AVERAGE : GOOD : EXCELLENT = 20 : 2 : 1
Total = 23
```

本轮结束后，通过 BRAIN 账号接口复核，当前 ACTIVE alpha 数为 29，等级分布为：

```text
AVERAGE : GOOD : EXCELLENT = 26 : 2 : 1
Total = 29
```

这说明今天确实完成了 6 个新增 ACTIVE，但也让组合进一步偏向 `AVERAGE`。后续不应继续追求数量，应把门槛提高到更接近 `GOOD` 的候选。

## 3. 新增因子逐条说明

### 3.1 `P0n5YEv7`

表达式：

```text
0.65*group_rank(-standardized_unexpected_earnings_2, subindustry)
+0.35*group_rank(-ts_delta(close, 5), subindustry)
```

经济含义：`standardized_unexpected_earnings_2` 是标准化的意外盈利信息。它衡量公司公布的盈利相对市场预期有多意外。表达式里使用负号，说明在当前回测中，低值方向更有效。初学者不要机械理解为“盈利惊喜越差越好”，因为供应商字段的方向、标准化方式、行业中性化后排序都会影响实际含义；正确做法是两边都测。

交易对手可能是：只看 headline earnings surprise 的投资者、反应过慢的基本面投资者，或者在财报后短期过度追逐好消息的资金。

自相关检查：提交后通过，记录的 self-correlation 约为 0.6956，接近 0.70 上限，后续不要再围绕同一字段做小幅权重调整。

### 3.2 `le7g3obA`

表达式：

```text
0.65*group_rank(-mdl77_earningmomentumfactor_fqsurstd, subindustry)
+0.35*group_rank(-ts_delta(close, 5), subindustry)
```

经济含义：`mdl77_earningmomentumfactor_fqsurstd` 是最近季度盈利惊喜的标准化版本。它属于低使用率的 model77 earnings momentum 字段。这个因子继续押注“盈利预期和真实盈利之间的差异没有被市场完全消化”。

本因子 Sharpe 1.90、Fitness 1.50，是本轮 6 个里质量最高的一个。需要注意的是，它与其它 earnings surprise 字段很接近，提交后自相关值约 0.7285，虽然系统接受为 PASS，但已经高于理想目标 0.60，也高于 0.70 的经验安全线，后续不能再密集提交同族变体。

### 3.3 `zq5AkwRR`

表达式：

```text
0.65*group_rank(-mdl77_earningmomentumfactor_fy1epsskew, subindustry)
+0.35*group_rank(-ts_delta(close, 5), subindustry)
```

经济含义：`fy1epsskew` 描述未来 12 个月或 FY1 EPS 预期分布的偏度。偏度可以理解为分析师预期是否集中，或者是否存在很强的单边乐观/悲观尾部。负号方向有效，可能表示市场对一边倒的盈利预期存在过度定价，或者字段原始方向和直觉相反。

这个因子的 self-correlation 约为 0.5289，是本轮新增中去相关效果比较好的一个。它说明“盈利预期分布形状”比单纯的 earnings surprise 更有增量信息。

### 3.4 `88OGl2JV`

表达式：

```text
0.65*group_rank(mdl77_oearningmomentumfactor_ratrev6m, subindustry)
+0.35*group_rank(-ts_delta(close, 5), subindustry)
```

经济含义：`ratrev6m` 是 6 个月卖方评级修正。它不直接看 EPS 数字，而是看分析师评级是否在改变。评级变化通常比盈利预测慢，但可能包含分析师对公司竞争格局、管理层质量、利润率变化的综合判断。

这个因子 Sharpe 1.49、Fitness 1.07，只是刚过线，属于为了完成数量目标提交的边际 `AVERAGE`。优点是 self-correlation 约 0.6653，低于 0.70；缺点是 Fitness 不高，后续不应围绕它做大量微调。

### 3.5 `YPNl5wx6`

表达式：

```text
0.65*group_rank(-revision_fiscal_q1_eps_forecast, subindustry)
+0.35*group_rank(-ts_delta(close, 5), subindustry)
```

经济含义：`revision_fiscal_q1_eps_forecast` 是下一财季 EPS 预测修正。它捕捉分析师近期是否上调或下调短期盈利预期。表达式使用负号，说明有效方向和字段名直觉可能相反。

这个因子的 self-correlation 约 0.4841，是本轮最干净的一个，但 Fitness 只有 1.06。它可以保留作为一个低相关 ACTIVE，但不应视为高质量候选。

### 3.6 `j2nVYNLE`

表达式：

```text
0.65*group_rank(-mdl77_2valuemomemtummodel_earningsqualitymodule, subindustry)
+0.35*group_rank(-ts_delta(close, 5), subindustry)
```

经济含义：`earningsqualitymodule` 是盈利质量模块。它通常聚合应计、现金流、库存、财务报表质量等信息。盈利质量因子想解决的问题是：同样是“赚了钱”，有些公司的利润更像真实现金流，有些公司的利润更像会计项目。

这个候选最初是 `UNRESOLVED_200`，也就是提交接口返回了检查结果，但 alpha 状态没有立即刷新。后续单独查询 `/submit` 后确认 SELF_CORRELATION PASS，值约 0.5352，最终变成 `ACTIVE`。它是本轮最后一个成功因子。

## 4. 搜索路径

### 第一阶段：沿用上午已筛出的强候选

上午已有一个未提交强候选：

```text
0.65*group_rank(-standardized_unexpected_earnings_2, subindustry)
+0.35*group_rank(-ts_delta(close, 5), subindustry)
```

提交后成功变成 `P0n5YEv7`。同一批里 `snt1_d1_earningstorpedo` 指标不错，但提交时 SELF_CORRELATION 失败，因此没有继续围绕 news/social 字段做小权重变化。

### 第二阶段：系统测试 low-use earnings surprise / revision

测试字段包括：

```text
mdl77_earningmomentumfactor_fqsurstd
mdl77_oearningmomentumfactor_fqsurstd
mdl77_ooearningsmomemtummodel_fc_fqsurstd
mdl77_earningmomentumfactor_salesurp
mdl77_2earningmomentumfactor400_salesurp
mdl77_oearningmomentumfactor_salesurp
mdl77_earningmomentumfactor_fy1epsskew
mdl77_earningmomentumfactor_rev6
mdl77_oearningmomentumfactor_ratrev6m
revision_fiscal_q1_eps_forecast
time_weighted_eps_stddev_revision
```

成功字段：

```text
standardized_unexpected_earnings_2
mdl77_earningmomentumfactor_fqsurstd
mdl77_earningmomentumfactor_fy1epsskew
mdl77_oearningmomentumfactor_ratrev6m
revision_fiscal_q1_eps_forecast
```

失败或不宜继续的字段：

```text
mdl77_earningmomentumfactor_salesurp
mdl77_2earningmomentumfactor400_salesurp
mdl77_oearningmomentumfactor_salesurp
```

这些 sales surprise 候选 Sharpe/Fitness 很强，但 `LOW_SUB_UNIVERSE_SHARPE` 失败，说明它们在子 universe 中表现不稳定，不能提交。

### 第三阶段：尝试历史高分候选补缺

为了补最后一个 ACTIVE，复查了历史上 `UNRESOLVED_200` 或 `READY_TO_SUBMIT` 的高分候选，包括 debt、pc_ratio、voldiff_pc、short sentiment、relative value 混合等。它们几乎全部被 SELF_CORRELATION 拒绝。

典型失败方向：

```text
debt_lt/assets + short reversal
rel5yfwdep + pc_ratio
rel5yocfp + voldiff_pc
rel5yfwdep + short sentiment
```

这验证了当前组合已经挤占了这些旧方向，继续调权重收益很低。

### 第四阶段：last-mile 分散搜索

最后增加了更分散的低使用率 model77 字段：

```text
mdl77_2surpriseanalystmodel_qsa_composite
mdl77_surpriseanalystmodel_qsa_surpsn
mdl77_2valuemomemtummodel_earningsqualitymodule
standardized_unexpected_cash_flow
mdl77_2earningmomentumfactor400_fcus
management signaling
value analyst / earnings quality
```

多数低使用率 quality/composite 字段 Fitness 很低。`standardized_unexpected_cash_flow` 和 `fcus` 的指标很强，但与已提交的 earnings surprise / cash-flow-value 类 alpha 自相关失败。最终只有 `mdl77_2valuemomemtummodel_earningsqualitymodule` 成功通过自相关，成为第 6 个 ACTIVE。

## 5. 失败分析

本轮主要失败原因不是回测指标，而是 SELF_CORRELATION。

关键结果文件：

```text
runs/2026-05-18/20260518T092049Z_parallel_submit_goal/submit_summary.csv
runs/2026-05-18/20260518_direct_existing_more6/submit_summary.csv
runs/2026-05-18/20260518T094901Z_parallel_submit_goal/submit_summary.csv
```

失败统计概览：

```text
候选筛选 run: READY_TO_SUBMIT 9, LOW_FITNESS 11, LOW_SHARPE 8, LOW_SUB_UNIVERSE_SHARPE 4
直接提交 run: ACTIVE 6, REJECTED 20，拒绝原因基本都是 SELF_CORRELATION
last-mile run: SKIPPED_CHECKS 31, REJECTED 5, UNRESOLVED_200 1
补跑第 38 条未完成候选: SKIPPED_CHECKS，LOW_SHARPE + LOW_FITNESS
```

各类失败解释：

- `SELF_CORRELATION`：候选因子和账号里已有 ACTIVE alpha 太相似。今天 debt、rel5yfwdep、pc_ratio、voldiff_pc、short sentiment、cash-flow surprise 都大量卡在这里。
- `LOW_FITNESS`：收益质量不够。很多 management signaling、value analyst、balance sheet、earnings quality 正方向候选失败在这里。
- `LOW_SHARPE`：收益稳定性不够，尤其是一些 composite analyst rank 和 value quality 字段。
- `LOW_SUB_UNIVERSE_SHARPE`：整体 Sharpe/Fitness 强，但在子股票池中表现不稳定。sales surprise 系列最典型。
- `HIGH_TURNOVER`：本轮不是主要问题。大多数成功候选 turnover 在 0.10 到 0.17 之间，能接受。

## 6. 今日市场/数据状态学习

1. Earnings surprise / revision 仍是当前最有效的信息源，但已经快速变拥挤。
2. 同一个 earnings surprise 家族中，第一两个字段能过，后续同族字段很容易被 SELF_CORRELATION 拒绝。
3. `fy1epsskew` 和 `revision_fiscal_q1_eps_forecast` 的自相关更干净，说明“预期分布形状”和“短期预测修正”比直接 surprise 更有增量。
4. 旧的 debt/value/pc_ratio/short-sentiment 高分候选现在基本不能再补数量，账号里已有太多相近结构。
5. low-use 并不等于高质量。许多 userCount=1 的 model77 字段仍然 LOW_FITNESS，需要用回测结果筛掉。

## 7. 下一步建议

优先尝试：

```text
0.60*group_rank(new_lowuse_earnings_quality_field, subindustry)
+0.40*group_rank(non-price slow anchor, subindustry)
```

候选字段：

```text
mdl77_2valuemomemtummodel_managementsignalingmodule
mdl77_valuemomemtummodel_managementsignalingmodule
mdl77_ovalueanalystmodel_qva_yoychgshares
mdl77_2mqf_ocfast
mdl77_oearningsqualityfactor_ccacw
mdl77_earningsqualityfactor_rau
mdl77_earningsqualityfactor_spefcn
mdl77_2historicalgrowthfactor_pctchgocf
mdl77_ohistoricalgrowthfactor_pctchgfcf
```

但不要直接重复今天的 `0.65 + short reversal` 模板。可以尝试：

```text
0.70*group_rank(new_signal, subindustry)
+0.30*group_rank(-mdl177_2_5yearrelativevaluefactor_rel5yocfp, subindustry)
```

或者：

```text
0.75*group_rank(new_signal, subindustry)
+0.25*group_rank(mdl77_2mqf_ocfast, subindustry)
```

如果继续用 `-ts_delta(close, 5)`，建议只作为筛选阶段稳定项，不要期待它继续帮助去相关。

## 8. 下一轮应避免

明确避免：

```text
q1aepsg 小权重调参
rel5yfwdep 小权重调参
debt_lt/assets + price reversal
standardized_unexpected_cash_flow 同族变体
mdl77_2earningmomentumfactor400_fcus 同族变体
monchgsip 同族变体
snt1_d1_earningstorpedo 同族变体
```

这些方向要么已经 ACTIVE 过，要么今天被自相关拒绝，继续投入大概率只会消耗 simulation budget。

下一轮如果目标是质量提升，而不是数量，应把提交门槛提高到：

```text
Sharpe > 1.70
Fitness > 1.30
LOW_SUB_UNIVERSE_SHARPE 必须 PASS 且 value 明显高于 limit
预估 SELF_CORRELATION 最好低于 0.60
```

今天虽然完成了数量目标，但新增 6 个全部是 `AVERAGE`。后续应减少“刚过线就提交”，优先寻找有机会成为 `GOOD` 的新信息源。

## 9. AGENTS.md 逐项补充：6 个新因子的完整提交卡片

本节是按 `AGENTS.md` 的“Goal Completion Documentation”要求补齐的逐因子卡片。前文已经解释了整体路径，这里逐条列出每个成功 alpha 的字段、设置、指标、ACTIVE 确认方式、经济直觉、可能交易对手和与已有组合的差异。

通用设置如下，6 个新 alpha 都相同：

```text
universe = TOP3000
neutralization = SUBINDUSTRY
decay = 10
truncation = 0.08
delay = 1
pasteurization = ON
nanHandling = ON
```

### 9.1 `P0n5YEv7`

表达式：

```text
0.65*group_rank(-standardized_unexpected_earnings_2, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)
```

指标：

```text
grade = AVERAGE
Sharpe = 1.68
Fitness = 1.34
returns = 0.0797
turnover = 0.1000
margin = 0.001594
self-correlation = 0.6956
```

提交状态：这是上午已经筛出的 `UNSUBMITTED` 强候选，本轮直接提交后确认 `ACTIVE`。它不是纯 pending 学习结果，而是本轮明确提交并通过所有检查的新增 alpha。

信息源：标准化意外盈利。它看的是公司真实盈利和市场预期之间的差异。

为什么可能预测收益：盈利意外通常不会被所有投资者同步、充分地反映到股价里。部分资金只看 headline，部分资金要等财报电话会、分析师更新或风控确认后才交易，因此会有滞后。

谁可能在交易另一边：追逐财报短期情绪的资金、反应慢的基本面资金、只按原有盈利预期持仓的被动或半被动资金。

为什么和已有组合不同：它不是 `rel5yfwdep`、债务、short interest 或 option 结构，而是 earnings surprise 数据源。不过 self-correlation 接近 0.70，说明它已经贴近账号里的 earnings/value 类信号，后续不要再围绕同字段继续调权重。

### 9.2 `le7g3obA`

表达式：

```text
0.65*group_rank(-mdl77_earningmomentumfactor_fqsurstd, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)
```

指标：

```text
grade = AVERAGE
Sharpe = 1.90
Fitness = 1.50
returns = 0.0780
turnover = 0.1012
margin = 0.001541
self-correlation = 0.7285
```

提交状态：候选筛选阶段是 `READY_TO_SUBMIT`，本轮提交后确认 `ACTIVE`。虽然记录里的 self-correlation 数值高于理想区间，但 BRAIN 返回 PASS，最终状态是 `ACTIVE`。

信息源：model77 最近季度盈利惊喜标准化字段。

为什么可能预测收益：季度盈利惊喜会改变投资者对公司未来盈利路径的判断。市场经常先反应一部分，随后在分析师报告、机构调仓和管理层解释中继续消化。

谁可能在交易另一边：低频基本面资金、依赖旧盈利预测的模型、短线财报后追涨杀跌但没有行业内比较的资金。

为什么和已有组合不同：它比 `standardized_unexpected_earnings_2` 更贴近 model77 的 earnings momentum 模块，是同一大类但不同供应商字段。由于自相关已经偏高，这个字段族只能保留本次成果，不宜继续变体提交。

### 9.3 `zq5AkwRR`

表达式：

```text
0.65*group_rank(-mdl77_earningmomentumfactor_fy1epsskew, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)
```

指标：

```text
grade = AVERAGE
Sharpe = 1.74
Fitness = 1.17
returns = 0.0577
turnover = 0.1274
margin = 0.000906
self-correlation = 0.5289
```

提交状态：候选筛选阶段是 `READY_TO_SUBMIT`，第一次提交后确认 `ACTIVE`。

信息源：FY1 或未来 12 个月 EPS 预期分布的偏度。偏度可以理解为“分析师预期是不是一边倒，或者是否存在极端乐观/悲观尾部”。

为什么可能预测收益：当分析师预期分布很偏时，市场价格可能过度相信某一类预期，或者忽视尾部风险。这个信号不是看 EPS 高低，而是看预期分布形状，因此有机会提供增量信息。

谁可能在交易另一边：只使用平均 EPS 预测、不看预测分布形状的量化模型；只关注共识均值的基本面投资者；对分析师分歧反应较慢的资金。

为什么和已有组合不同：它不是直接 earnings surprise，而是分析师预期分布结构。self-correlation 0.5289，比其它 earnings surprise 变体干净，是今天相对更值得保留学习的一条。

### 9.4 `88OGl2JV`

表达式：

```text
0.65*group_rank(mdl77_oearningmomentumfactor_ratrev6m, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)
```

指标：

```text
grade = AVERAGE
Sharpe = 1.49
Fitness = 1.07
returns = 0.0647
turnover = 0.1052
margin = 0.001230
self-correlation = 0.6653
```

提交状态：候选筛选阶段是 `READY_TO_SUBMIT`，提交后确认 `ACTIVE`。

信息源：6 个月卖方评级修正。它关注分析师评级变化，不是直接看 EPS 数值。

为什么可能预测收益：评级修正往往滞后于基本面变化，但也能反映分析师对行业地位、利润率、风险暴露和管理层执行的综合判断。市场可能不会马上完全吸收评级变化。

谁可能在交易另一边：只看财务报表、不看卖方评级变化的资金；把 analyst rating 当成滞后噪声而完全忽略的模型；还没有完成调仓的机构资金。

为什么和已有组合不同：它从“评级修正”角度切入，而不是从 surprise 或 value 切入。但 Fitness 只有 1.07，属于完成数量目标时接受的边际因子，不应继续围绕它大量扩展。

### 9.5 `YPNl5wx6`

表达式：

```text
0.65*group_rank(-revision_fiscal_q1_eps_forecast, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)
```

指标：

```text
grade = AVERAGE
Sharpe = 1.70
Fitness = 1.06
returns = 0.0657
turnover = 0.1690
margin = 0.000778
self-correlation = 0.4841
```

提交状态：候选筛选阶段是 `READY_TO_SUBMIT`，提交后确认 `ACTIVE`。

信息源：下一财季 EPS 预测修正。它看的是短期盈利预期的最近变化。

为什么可能预测收益：短期 EPS 修正通常代表分析师刚接收到新信息，或者管理层指引、行业需求、成本端出现变化。市场对这种修正可能分批反应。

谁可能在交易另一边：继续持有旧预期的基本面资金、只用年度 EPS 而忽略季度修正的模型、短线只看价格不看盈利预测变化的资金。

为什么和已有组合不同：它更偏短期预测修正，不是长期价值或直接 surprise。self-correlation 0.4841 很干净，但 Fitness 只有 1.06，因此可以保留为低相关补充，不适合当作下一轮主攻模板。

### 9.6 `j2nVYNLE`

表达式：

```text
0.65*group_rank(-mdl77_2valuemomemtummodel_earningsqualitymodule, subindustry)+0.35*group_rank(-ts_delta(close, 5), subindustry)
```

指标：

```text
grade = AVERAGE
Sharpe = 1.86
Fitness = 1.31
returns = 0.0621
turnover = 0.1022
margin = 0.001214
self-correlation = 0.5352
```

提交状态：last-mile run 中先显示 `UNRESOLVED_200`，也就是提交检查接口已经返回 200，但 alpha 状态暂时还没有刷新成 `ACTIVE`。之后单独查询 `/alphas/j2nVYNLE/submit`，确认 SELF_CORRELATION PASS，最终 alpha 状态变为 `ACTIVE`。这是“先 pending / unresolved，后确认 ACTIVE”的案例。

信息源：盈利质量模块。它不是只问“公司赚多少钱”，而是问“这些利润的质量怎么样，是否有现金流支持，是否依赖会计项目”。

为什么可能预测收益：市场有时会高估低质量利润，也会低估现金流扎实但账面增长不显眼的公司。盈利质量模块把这些财务质量信息合在一起，可能捕捉到价格尚未充分反映的质量差异。

谁可能在交易另一边：只看 EPS 增长、不看现金流和应计质量的投资者；追逐短期利润数字的资金；没有细分财务质量的简单价值/成长模型。

为什么和已有组合不同：它从 earnings quality 出发，不是直接 earnings surprise。相比今天的其它 earnings surprise 字段，它的 self-correlation 0.5352 更可控，是最后补足目标时最有价值的分散方向。

## 10. AGENTS.md 要求覆盖清单

这次 summary 覆盖情况如下：

```text
1. 今日目标与最终结果：见第 1 节，目标为新增 6 个，最终新增 6 个 ACTIVE。
2. 起始背景和 AVERAGE/GOOD/EXCELLENT 分布：见第 2 节。
3. 每个新因子的 alpha id、表达式、grade、设置、指标、ACTIVE 确认方式：见第 9 节。
4. 每个成功因子的经济直觉、信息源、预测原因、交易对手：见第 9 节逐条说明。
5. 搜索路径、尝试的家族、有效字段、失败字段、策略转向原因：见第 4 节。
6. SELF_CORRELATION、LOW_FITNESS、LOW_SHARPE、LOW_SUB_UNIVERSE_SHARPE、HIGH_TURNOVER 失败分析：见第 5 节。
7. 当前市场/数据状态学习：见第 6 节。
8. 下一步候选字段和模板：见第 7 节。
9. 下一轮应避免的拥挤字段和重复调权方向：见第 8 节。
```

补充说明：last-mile 自动运行曾在第 38 条候选处被超时中断。为满足“已经启动的候选要有最终结果”的要求，已单独补跑：

```text
expression = 0.70*group_rank(-mdl77_2earningsqualityfactor_ttmaccu, subindustry)+0.30*group_rank(-ts_delta(close, 5), subindustry)
alpha id = mLqK7zx6
status = UNSUBMITTED
submit_result = SKIPPED_CHECKS
Sharpe = 0.05
Fitness = 0.01
failed = LOW_SHARPE, LOW_FITNESS
pending = SELF_CORRELATION
result file = runs/2026-05-18/20260518T103923Z_parallel_submit_goal/submit_summary.csv
```
