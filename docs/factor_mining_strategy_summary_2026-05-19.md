# 2026-05-19 因子挖掘策略阶段性总结

> 说明：这是一次阶段性补录总结，不是目标完成总结。当前会话目标仍未完成，后续如果继续挖到新的 ACTIVE 因子，应在本文件后面追加新的“完成总结”或“后续进展”章节，不要覆盖本节。

## 1. 今日目标与当前结果

今日目标是：再挖 10 个新的 ACTIVE / 已提交因子，并且这 10 个里面至少包含 1 个 GOOD 或 EXCELLENT Alpha。

截至本阶段总结，结果如下：

- 新增 ACTIVE 因子：0 个
- 新增 GOOD / EXCELLENT 因子：0 个
- 目标完成度：0 / 10
- 当前目标状态：未完成

本阶段主要工作不是提交新因子，而是先寻找至少 1 个有机会成为 GOOD / EXCELLENT 的候选。这样做的原因是，当前账户已经明显 AVERAGE 偏多，如果继续先填满 10 个普通 ACTIVE，很可能进一步恶化组合质量。

## 2. 起始背景

开始 2026-05-19 这轮挖掘前，账户中已确认 ACTIVE 的因子数量为 29 个，等级分布为：

```text
AVERAGE : GOOD : EXCELLENT = 26 : 2 : 1
Total = 29
```

目标月度结构是：

```text
AVERAGE : GOOD : EXCELLENT = 5 : 4 : 1
```

这说明当前因子库的问题不是数量不够，而是 AVERAGE 占比过高。因此今天的策略应该优先寻找真正可能成为 GOOD / EXCELLENT 的新信息源，而不是把刚过线的 AVERAGE 因子继续提交进去。

## 3. 本阶段新挖出的因子

本阶段没有新提交并确认 ACTIVE 的因子。

因此没有可记录的成功因子卡片。下面这些 alpha id 都只是回测候选或历史 alpha 的复查结果，不是今天新增 ACTIVE：

- `blNzpOoq`, `LLnzeroL`, `qMnGbVYZ` 等：TOP1000 / SUBINDUSTRY 的候选，指标不达标，未提交。
- `0mAgQMx8`, `akNzPoLR`, `E5qzbLkK` 等：TOP3000 / INDUSTRY 的销售惊喜候选，主指标很强，但 LOW_SUB_UNIVERSE_SHARPE 失败，未提交。
- `RRNzdpp0`, `QPnzEPzp`, `QPnz2Qm5` 等：TOP3000 / SUBINDUSTRY 的销售惊喜加价值或质量锚候选，主指标很强，但仍然 LOW_SUB_UNIVERSE_SHARPE 失败，未提交。
- `xAeQ9Pgq`, `58Lz1Vp6`, `WjNbRmGj` 等历史 GOOD / EXCELLENT 候选：直接提交检查时被 SELF_CORRELATION 拒绝。

## 4. 本阶段成功因子的经济解释

因为本阶段没有新增 ACTIVE 因子，所以没有成功因子的经济解释。

但本阶段测试过的主要方向有明确经济含义：

- 销售惊喜类信号：例如 `mdl77_earningmomentumfactor_salesurp`。这类信号试图捕捉公司销售收入超预期或低于预期的信息。直觉上，如果市场还没有完全消化销售数据，销售超预期的公司后续可能被上调预期，销售低预期的公司可能继续承压。
- 现金流惊喜类信号：例如 `standardized_unexpected_cash_flow` 和 `mdl77_2earningmomentumfactor400_fcus`。这类信号关注公司现金流是否超出市场或历史预期。现金流比会计利润更难被短期调整，因此有时能反映经营质量。
- 估值锚和质量锚：例如 `mdl177_2_5yearrelativevaluefactor_rel5yocfp`、`mdl77_2valuemomemtummodel_earningsqualitymodule`。这些字段用于让短期事件信号不要完全依赖一个高波动的事件变量，而是与更慢的价值或质量维度结合。

本阶段的重要结论是：这些经济逻辑本身不弱，尤其是销售惊喜类信号，但当前它们在子股票池上的稳定性不足，暂时不能直接提交。

## 5. 搜索路径

### 5.1 GOOD / EXCELLENT 先行

因为目标要求 10 个新因子中至少有 1 个 GOOD 或 EXCELLENT，本阶段没有先去填数量，而是先做 GOOD / EXCELLENT 候选筛选。

第一批候选文件是：

```text
candidates/manual/candidate_alphas_20260519_good_hunt_v1.txt
```

运行设置：

```text
universe = TOP1000
neutralization = SUBINDUSTRY
decay = 10
truncation = 0.08
mode = no-submit
```

结果：

- 候选数量：29
- 新增 ACTIVE：0
- 主要失败：LOW_FITNESS、LOW_SHARPE
- 同时 SELF_CORRELATION 仍处于 pending，因此即使主指标过线也还需要进一步检查。

TOP1000 的结论是：较小股票池没有救活销售惊喜和现金流惊喜方向，反而把 Sharpe 和 Fitness 压低。

代表候选：

| alpha id | 表达式摘要 | Sharpe | Fitness | Turnover | 结果 |
|---|---|---:|---:|---:|---|
| `N1nzW1LL` | `-standardized_unexpected_cash_flow` + 20 日反转 | 1.37 | 0.97 | 0.0860 | LOW_FITNESS |
| `j2nGlNKQ` | `-mdl77_2earningmomentumfactor400_fcus` + 20 日反转 | 1.37 | 0.97 | 0.0860 | LOW_FITNESS |
| `P0nzqgwE` | `mdl77_growthanalystmodel_qga_ltepssurprise` + 10 日反转 | 1.14 | 0.75 | 0.0742 | LOW_SHARPE / LOW_FITNESS |

### 5.2 直接复查历史 GOOD / EXCELLENT 候选

第二步复查历史上看起来是 GOOD / EXCELLENT 的候选，尝试直接提交检查：

```text
runs/2026-05-19/20260519_direct_good_historical/submit_summary.csv
```

结果：

- 候选数量：12
- 新增 ACTIVE：0
- 全部被 SELF_CORRELATION 拒绝

这些候选的主指标并不差，很多 Sharpe 和 Fitness 都达到 GOOD / EXCELLENT 级别。但它们大多依赖 `rel5yfwdep` 或类似旧结构，和账户里已有因子太像。

代表候选：

| alpha id | 表达式摘要 | Sharpe | Fitness | Turnover | SELF_CORRELATION |
|---|---|---:|---:|---:|---:|
| `WjNbRmGj` | `rel5yfwdep` + 10 日反转 | 2.22 | 2.08 | 0.0906 | 0.9680 |
| `58Lz1Vp6` | `rel5yfwdep` + 10 日反转 | 2.21 | 2.10 | 0.1033 | 0.9419 |
| `LLnNw2Vm` | `rel5yfwdep` + 20 日反转 | 2.07 | 1.91 | 0.0792 | 0.8698 |
| `xAeQ9Pgq` | 纯 `rel5yfwdep` | 2.00 | 1.77 | 0.0354 | 0.9330 |

这一步的结论很明确：旧的高分方向已经拥挤，不能再靠改权重或改一点短期价格项来过关。

### 5.3 销售惊喜 rescue：TOP3000 / INDUSTRY

第三步回到销售惊喜方向，但改成 TOP3000 / INDUSTRY，希望通过更粗的行业中性化修复子股票池 Sharpe。

候选文件：

```text
candidates/manual/candidate_alphas_20260519_sales_rescue.txt
```

运行设置：

```text
universe = TOP3000
neutralization = INDUSTRY
decay = 10
truncation = 0.08
mode = no-submit
```

结果：

- 候选数量：9
- 新增 ACTIVE：0
- 所有候选都失败于 LOW_SUB_UNIVERSE_SHARPE
- 多个候选在主指标上达到 EXCELLENT 级别，但不能提交。

代表候选：

| alpha id | 表达式摘要 | Grade | Sharpe | Fitness | Returns | Turnover | 失败原因 |
|---|---|---|---:|---:|---:|---:|---|
| `0mAgQMx8` | `-mdl77_oearningmomentumfactor_salesurp` + 5 日反转 | EXCELLENT | 2.42 | 2.11 | 0.0951 | 0.1164 | LOW_SUB_UNIVERSE_SHARPE，value 0.78 < limit 1.05 |
| `akNzPoLR` | `-mdl77_oearningmomentumfactor_salesurp` + 5 日反转 | EXCELLENT | 2.38 | 2.02 | 0.0896 | 0.0990 | LOW_SUB_UNIVERSE_SHARPE |
| `E5qzbLkK` | `-mdl77_earningmomentumfactor_salesurp` + 5 日反转 | GOOD / EXCELLENT 级主指标 | 2.36 | 2.05 | 0.0943 | 0.1153 | LOW_SUB_UNIVERSE_SHARPE |

这说明销售惊喜方向的整体收益形状很强，但收益可能集中在某些股票子集或行业段里。WorldQuant 的 LOW_SUB_UNIVERSE_SHARPE 检查会惩罚这种不均匀性，所以不能只看总 Sharpe。

### 5.4 销售惊喜 rescue：TOP500 / SUBINDUSTRY

第四步尝试 TOP500 / SUBINDUSTRY，希望更大市值池能改善稳定性。

运行设置：

```text
universe = TOP500
neutralization = SUBINDUSTRY
decay = 10
truncation = 0.08
mode = no-submit
```

结果：

- 候选数量：9
- 新增 ACTIVE：0
- 主要失败：LOW_FITNESS、LOW_SHARPE

代表候选：

| alpha id | 表达式摘要 | Sharpe | Fitness | Turnover | 失败原因 |
|---|---|---:|---:|---:|---|
| `JjnzX6d2` | `-mdl77_earningmomentumfactor_salesurp` + 5 日反转 | 1.31 | 0.95 | 0.1305 | LOW_FITNESS |
| `blNzW9El` | `-mdl77_2earningmomentumfactor400_salesurp` + 5 日反转 | 1.31 | 0.95 | 0.1305 | LOW_FITNESS |
| `RRNzaK9z` | `-mdl77_earningmomentumfactor_salesurp` + 5 日反转 | 1.26 | 0.90 | 0.1123 | LOW_FITNESS |

TOP500 的结论是：销售惊喜信号在大市值股票里没有足够强，至少当前模板下不能提交。

### 5.5 销售惊喜 + 慢速价值 / 质量锚

第五步尝试把销售惊喜与更慢的价值或质量因子混合，目标是降低集中度、改善 LOW_SUB_UNIVERSE_SHARPE。

候选文件：

```text
candidates/manual/candidate_alphas_20260519_sales_value_blend.txt
```

运行设置：

```text
universe = TOP3000
neutralization = SUBINDUSTRY
decay = 10
truncation = 0.08
mode = no-submit
```

结果：

- 候选数量：18
- 新增 ACTIVE：0
- 全部失败于 LOW_SUB_UNIVERSE_SHARPE
- 主指标仍然非常强，但子股票池稳定性没有修复。

代表候选：

| alpha id | 表达式摘要 | Grade | Sharpe | Fitness | Returns | Turnover | 失败原因 |
|---|---|---|---:|---:|---:|---:|---|
| `RRNzdpp0` | 销售惊喜 + earnings quality module + 5 日反转 | EXCELLENT | 2.51 | 2.08 | 0.0856 | 0.0771 | LOW_SUB_UNIVERSE_SHARPE，value 0.84 < limit 1.09 |
| `QPnzEPzp` | 销售惊喜 + earnings quality module + 5 日反转 | EXCELLENT | 2.50 | 2.07 | 0.0861 | 0.0769 | LOW_SUB_UNIVERSE_SHARPE |
| `QPnz2Qm5` | 销售惊喜 + `rel5yocfp` + 5 日反转 | EXCELLENT 级主指标 | 2.42 | 2.21 | 0.1042 | 0.0768 | LOW_SUB_UNIVERSE_SHARPE |
| `xAeGe8dq` | 销售惊喜 + `rel5yocfp` + 5 日反转 | EXCELLENT 级主指标 | 2.43 | 2.21 | 0.1038 | 0.0771 | LOW_SUB_UNIVERSE_SHARPE |

这一步说明：简单加慢速锚不能解决销售惊喜家族的子股票池问题。继续在同一个字段附近微调权重，大概率只是继续得到“看起来很强但不能提交”的候选。

## 6. 失败分析

### 6.1 SELF_CORRELATION

SELF_CORRELATION 的意思是：新因子和账户里已有因子的持仓或收益行为太相似。WorldQuant 限制这个指标，是为了避免重复提交同一类交易逻辑。

本阶段最典型的是历史 GOOD / EXCELLENT 候选复查。它们的 Sharpe 和 Fitness 很好，但 self-correlation 值普遍远高于 0.70：

- `WjNbRmGj`: 0.9680
- `58Lz1Vp6`: 0.9419
- `xAeQ9Pgq`: 0.9330
- `A1nbJVNw`: 0.9934
- `QPnbwxoG`: 0.9990

这说明 `rel5yfwdep` 及其短期反转混合已经是拥挤方向。后续不应该继续在这一组表达式上微调。

### 6.2 LOW_FITNESS

Fitness 可以粗略理解为“综合质量分”，它不仅看收益和 Sharpe，也会受到换手、稳定性等因素影响。TOP1000 和 TOP500 的销售惊喜 / 现金流惊喜候选普遍出现 LOW_FITNESS。

典型例子：

- `N1nzW1LL`: Sharpe 1.37，Fitness 0.97，差一点过 Fitness，但仍不能提交。
- `JjnzX6d2`: Sharpe 1.31，Fitness 0.95。
- `RRNzaK9z`: Sharpe 1.26，Fitness 0.90。

这说明缩小 universe 并没有自动提高质量，反而可能让信号覆盖变窄，稳定性下降。

### 6.3 LOW_SHARPE

Sharpe 可以简单理解为“单位波动带来的收益”。Sharpe 太低表示收益不够稳定。

TOP1000 的第一批广泛候选里，LOW_SHARPE 很多：

- 29 个候选里 27 个 LOW_SHARPE
- 同时 29 个候选全部 LOW_FITNESS

这说明这批候选在 TOP1000 的设置下没有继续投入的价值。

### 6.4 LOW_SUB_UNIVERSE_SHARPE

LOW_SUB_UNIVERSE_SHARPE 是本阶段最重要的失败类型。它表示因子在整体股票池里表现很好，但拆到子股票池后表现不够稳定。

本阶段销售惊喜方向的典型现象是：

- TOP3000 / INDUSTRY：9 个候选全部 LOW_SUB_UNIVERSE_SHARPE。
- TOP3000 / SUBINDUSTRY 加价值或质量锚：18 个候选全部 LOW_SUB_UNIVERSE_SHARPE。
- 其中多个候选主指标达到 EXCELLENT，但仍不能提交。

这说明销售惊喜方向不是没有 alpha，而是 alpha 分布不够均匀。后续如果继续做这个方向，必须从“修复子股票池稳定性”的角度设计，而不是单纯提高 Sharpe。

### 6.5 HIGH_TURNOVER

本阶段没有出现 HIGH_TURNOVER 作为主要失败原因。大部分强候选的 turnover 在 0.07 到 0.13 左右，换手可接受。

因此当前瓶颈不是交易过于频繁，而是：

- 对旧方向：SELF_CORRELATION 太高。
- 对销售惊喜方向：LOW_SUB_UNIVERSE_SHARPE 太顽固。
- 对小股票池设置：Sharpe / Fitness 下降。

## 7. 对当前市场 / 数据状态的理解

本阶段暴露出三个重要状态：

第一，历史上好用的价值类字段，尤其是 `rel5yfwdep`，现在已经不能作为主锚继续复用。它的主指标仍然漂亮，但和已有因子太像，提交会被拒。

第二，销售惊喜类字段确实有很强的信号。多个候选的 Sharpe 超过 2.3，Fitness 超过 2.0，表明这类信息仍然可能预测收益。但它现在的问题是子股票池不稳定，可能表现集中在部分行业、市值段或流动性段。

第三，用简单的 universe 切换或权重微调无法解决核心问题。TOP500 降低了质量，TOP1000 也没有通过；把销售惊喜和 `rel5yocfp`、earnings quality module 混合，也没有修复 LOW_SUB_UNIVERSE_SHARPE。

因此下一步应该切换信息源，而不是继续围绕同一批销售惊喜字段做小幅调参。

## 8. 下一步建议

### 8.1 优先切换到期权波动率 / 偏度 / Put-Call 结构

建议下一批先测试期权相关字段，因为它们和财务惊喜、价值字段的信息来源不同，可能更容易避开 self-correlation。

候选字段：

- `out_of_money_put_call_ratio`
- `mdl77_2400_ctpmto`
- `mdl77_2400_impvol`
- `mdl77_2400_rmi`
- `mdl77_2liquidityriskfactor_atmputvol`
- `mdl77_liquidityriskfactor_atmcallvol`
- `mdl77_pricemomentumfactor_skew90drtn`
- `mdl77_opricemomentumfactor_skew90cortn`

起始模板：

```text
0.75*group_rank(option_signal, subindustry)
+0.25*group_rank(-ts_delta(close, 10), subindustry)
```

如果 turnover 偏高，可以改成：

```text
0.85*group_rank(option_signal, subindustry)
+0.15*group_rank(-ts_delta(close, 20), subindustry)
```

并优先用：

```text
decay = 20
truncation = 0.08
universe = TOP3000
neutralization = SUBINDUSTRY
```

### 8.2 尝试短融 / 借券 / 空头拥挤字段，但不要用旧价值锚

候选字段：

- `mdl77_devnorthamericashortsentimentfactor_conc_ratio`
- `mdl77_devnorthamericashortsentimentfactor_dmd_conc`
- `mdl77_devnorthamericashortsentimentfactor_dmd_supply`
- `mdl77_devnorthamericashortsentimentfactor_tni_ths`
- `mdl77_2liquidityriskfactor_sip`
- `mdl77_2liquidityriskfactor_monchgsip`

起始模板：

```text
0.70*group_rank(short_or_borrow_signal, subindustry)
+0.30*group_rank(-ts_delta(close, 10), subindustry)
```

或者：

```text
0.70*group_rank(short_or_borrow_signal, subindustry)
+0.30*group_rank(cash_flow_quality_signal, subindustry)
```

这里不要再用 `rel5yfwdep` 作为默认锚，否则很可能继续 SELF_CORRELATION。

### 8.3 销售惊喜方向暂时只保留为“待修复”方向

销售惊喜不是完全放弃，但下一次不应该继续做 0.40 / 0.45 / 0.50 这类权重微调。只有在能提出新的修复逻辑时再回头，例如：

- 换成更慢的时间处理，而不是只改混合权重。
- 使用不同 neutralization 层级并结合更强去集中化处理。
- 找到同类但不是 salesurp 的低用量字段，降低与当前候选的结构重复。

可再观察的字段：

- `mdl77_earningmomentumfactor_fqsurstd`
- `mdl77_2earningmomentumfactor400_mrspe`
- `mdl77_earningmomentumfactor_rev6`
- `mdl77_oearningmomentumfactor_ratrev6m`
- `mdl77_earningmomentumfactor_fy1epsskew`

### 8.4 如果必须填数量，仍应先拿到至少 1 个 GOOD / EXCELLENT

当前目标明确要求 10 个新因子里至少有 1 个 GOOD / EXCELLENT。因此建议继续保持顺序：

1. 先用新信息源找 1 个可提交的 GOOD / EXCELLENT。
2. 找到后再填剩余 ACTIVE 数量。
3. 剩余数量也不要接受太边缘的候选，尤其是 self-correlation 靠近 0.70 或 sub-universe 勉强过线的候选。

## 9. 下一步应避免的方向

短期内应避免：

- 继续围绕 `rel5yfwdep` 调权重。
- 继续围绕 `q1aepsg` 调权重。
- 继续直接提交历史 GOOD / EXCELLENT 候选。
- 继续在销售惊喜字段上只做 0.40 / 0.45 / 0.50 权重微调。
- 继续用 `ts_delta(close, 5)` 当万能稳定器。
- 为了填满 10 个数量而提交刚刚过线的 AVERAGE 候选。

这些方向不是完全没有信号，而是当前最可能导致两类浪费：

- 回测看起来不错，但 SELF_CORRELATION 拒绝。
- 主指标很好，但 LOW_SUB_UNIVERSE_SHARPE 拒绝。

## 10. 给后续继续挖掘的执行清单

后续接手时，建议按下面顺序继续：

1. 不要把当前目标标记为完成，因为还没有新增 ACTIVE。
2. 先开一批期权 / 波动率 / 偏度字段候选，使用 TOP3000 / SUBINDUSTRY，decay 20 优先。
3. 如果期权方向出现 GOOD / EXCELLENT 且没有 LOW_SUB_UNIVERSE_SHARPE，再提交检查 SELF_CORRELATION。
4. 如果期权方向失败，再切到短融 / 借券字段，不要回到 `rel5yfwdep`。
5. 达到 10 个新 ACTIVE 后，重新查询账户 ACTIVE 列表，确认新增 id 和等级。
6. 更新 `AGENTS.md` 的 Current Submission Statistics。
7. 在本文件追加最终完成总结，逐个记录新 ACTIVE 因子的 id、表达式、设置、指标和经济解释。

本阶段最关键的一句话结论是：销售惊喜方向强但暂时卡在子股票池稳定性，旧价值方向高分但已被 self-correlation 挡住，下一步必须换到期权结构或短融借券这类新信息源。

---

## 11. 后续进展补录：已新增 2 个 ACTIVE，但高等级目标仍未完成

本节记录在上面阶段性总结之后继续进行的挖掘。当前目标仍是“新增 10 个 ACTIVE，且至少 1 个 GOOD / EXCELLENT”。截至本补录：

- 新增 ACTIVE 因子：2 个
- 其中 AVERAGE：2 个
- 其中 GOOD / EXCELLENT：0 个
- 目标完成度：2 / 10
- 高等级条件：未完成

账户当前 ACTIVE 总数已变为 31，等级分布为：

```text
AVERAGE : GOOD : EXCELLENT = 28 : 2 : 1
```

### 11.1 新增 ACTIVE 因子 1：`kqnGaJzg`

- alpha id：`kqnGaJzg`
- 表达式：

```text
group_rank(-snt1_d1_nettargetpercent, subindustry)
```

- Grade：AVERAGE
- Universe：TOP3000
- Neutralization：SUBINDUSTRY
- Decay：10
- Truncation：0.08
- Sharpe：1.33
- Fitness：1.01
- Returns：0.0727
- Turnover：0.0347
- Margin：0.004198
- Self-correlation：0.6918
- 状态：提交后确认 ACTIVE

小白解释：`snt1_d1_nettargetpercent` 可以理解为分析师目标价调整的净方向。这里取负号，表示更偏向“目标价净上调比例较低或净下调压力较高”的股票。它能过 self-correlation 的关键原因是使用纯信号，没有再叠加常见的短期价格反转项，所以和已有因子相似度刚好低于 0.70。

但它只是 AVERAGE，说明虽然独特性勉强够，收益质量还没有达到 GOOD。

### 11.2 新增 ACTIVE 因子 2：`vR5GE9Nb`

- alpha id：`vR5GE9Nb`
- 表达式：

```text
0.65*group_rank(ts_zscore(snt1_d1_sellrecpercent, 60), subindustry)
+0.35*group_rank(-ts_delta(close, 5), subindustry)
```

- Grade：AVERAGE
- Universe：TOP3000
- Neutralization：SUBINDUSTRY
- Decay：10
- Truncation：0.08
- Sharpe：1.87
- Fitness：1.31
- Returns：0.0858
- Turnover：0.1751
- Margin：0.00098
- Self-correlation：0.6640
- 状态：提交后确认 ACTIVE

小白解释：`snt1_d1_sellrecpercent` 表示卖出评级相关的信息。`ts_zscore(..., 60)` 不是看当前卖出评级的绝对高低，而是看它相对过去 60 天是否异常偏高或偏低。这让因子更像“分析师悲观情绪的变化”而不是“分析师悲观情绪的水平”，因此和已有 SNT/earnings 因子更不一样。第二项 `-ts_delta(close, 5)` 是短期反转稳定器：最近跌得多的股票会得到更高分。

这个因子 Sharpe 较好，但换手更高，margin 偏低，因此仍是 AVERAGE。

### 11.3 新尝试过的方向

#### 期权、波动率和短融借券

候选文件：

```text
candidates/manual/candidate_alphas_20260519_option_short_pivot.txt
```

主要结论：

- 期权、波动率、偏度字段整体表现弱，大多 LOW_SHARPE / LOW_FITNESS。
- 短融集中度字段出现 2 个 READY_TO_SUBMIT：
  - `6XR0ekbp`
  - `e7nG3dNz`
- 这两个都是 AVERAGE，并且直接提交后都 SELF_CORRELATION 失败。

结论：短融字段仍有信号，但账户已有短融类 ACTIVE，直接使用相邻字段已经不够去相关。

#### SNT1 分析师情绪字段

候选文件：

```text
candidates/manual/candidate_alphas_20260519_snt_revision_diverse.txt
candidates/manual/candidate_alphas_20260519_snt_decorrelate_v1.txt
candidates/manual/candidate_alphas_20260519_snt_social_pivot.txt
candidates/manual/candidate_alphas_20260519_snt_ts_transform.txt
```

主要结论：

- SNT1 水平值能产生多个 GOOD 级候选，例如：
  - `QPnzK6GX`
  - `MPbz3Qv8`
  - `E5qzRNL1`
  - `6XR0dVnE`
  - `d5nzbNMJ`
- 但这些 GOOD 候选提交时全部 SELF_CORRELATION 失败，相关性大多在 0.76 到 0.83 附近。
- 纯 `-snt1_d1_nettargetpercent` 成功压到 0.6918 并成为 ACTIVE，但等级只有 AVERAGE。
- `ts_zscore(snt1_d1_sellrecpercent, 60)` 成功压到 0.6640 并成为 ACTIVE，但也只有 AVERAGE。

结论：SNT1 是可用信息源，但当前 GOOD 级版本太接近已有分析师/earnings 暴露。要继续用 SNT1，需要更多时间序列变换或更不同的非价格锚。

#### Sales surprise + sector neutralization

候选文件：

```text
candidates/manual/candidate_alphas_20260519_sales_neutralization_repair.txt
```

主要结论：

- 把 final neutralization 从 SUBINDUSTRY 改成 SECTOR 后，salesurp + `rel5yocfp` 的 LOW_SUB_UNIVERSE_SHARPE 被修复。
- 出现 1 个 EXCELLENT 和 5 个 GOOD READY 候选。
- 但全部提交后 SELF_CORRELATION 失败，相关性约 0.80 到 0.84。

结论：SECTOR neutralization 是修复 sub-universe 的有效办法，但 salesurp 家族仍然与已有 earnings/revision 因子过于接近，不能靠这个设置直接达成 GOOD/EXCELLENT。

#### 历史 GOOD 候选直接复查

直接复查了债务、pc_ratio、q1aepsg、现金流 surprise 等历史 GOOD 候选：

- `Grn1knZJ`
- `akNjodWw`
- `le7WZeJx`
- `le7p0VGO`
- `qMnnKN0E`
- `MPbKL6M9`
- `GrnQXA2G`
- `YPNl8lGA`

结果：全部 SELF_CORRELATION 失败。

结论：历史高分候选不能作为今天的捷径。现在的瓶颈是去相关，不是找不到高 Sharpe 表达式。

### 11.4 当前失败模式

本阶段最主要的失败模式是 SELF_CORRELATION：

- GOOD / EXCELLENT 候选很多，但绝大多数相关性高于 0.70。
- 有些候选非常接近通过，例如 0.7002、0.7072、0.7156，但仍被拒。
- 能通过的候选往往需要更“纯”或更不同的时间序列变换，但这样等级会下降到 AVERAGE。

LOW_SUB_UNIVERSE_SHARPE 的经验也更清楚：

- salesurp + `rel5yocfp` 在 SUBINDUSTRY 下失败。
- 改成 SECTOR 后 sub-universe 通过。
- 但 SECTOR 版本仍被 self-correlation 拒绝。

### 11.5 下一步应该怎么继续

当前最合理的继续方向：

1. 继续 SNT1 时间序列变换，但不要再提交当前水平值。
2. 对通过 ACTIVE 的两个 SNT 因子做“相邻但不同”的扩展，例如：

```text
group_rank(-ts_delta(snt1_d1_nettargetpercent, 60), subindustry)
group_rank(ts_zscore(snt1_d1_sellrecpercent, 120), subindustry)
group_rank(ts_rank(snt1_d1_sellrecpercent, 120), subindustry)
```

3. 测试更慢 decay，降低换手：

```text
decay = 20
```

4. 尝试不使用 `-ts_delta(close, 5)`，改用更不同的稳定器：

```text
group_rank(-(close-open), subindustry)
group_rank(-ts_delta(vwap, 10), subindustry)
group_rank(ts_delta(volume, 20), subindustry)
```

5. 如果继续寻找 GOOD / EXCELLENT，应优先测试“新信息源 + 时间序列变换”，而不是回到历史高分字段。

短期应避免：

- 继续直接提交 salesurp + `rel5yocfp` 的 SECTOR 版本。
- 继续提交 SNT1 当前水平值加 `-ts_delta(close, 5)` 的 GOOD 候选。
- 继续复查旧债务、q1aepsg、rel5yfwdep、pc_ratio 历史 GOOD。

当前最关键的一句话结论是：今天已经新增 2 个 ACTIVE，但都是 AVERAGE；高等级候选足够多，真正缺的是低 self-correlation 的 GOOD / EXCELLENT。

---

## 12. AGENTS.md 要求补正总结：当前阶段仍未完成目标

本节是按照 `AGENTS.md` 的“Goal Completion Documentation”要求补写的结构化总结。因为今天的目标还没有完成，所以这里不是最终完成总结，而是当前阶段的完整记录。后续如果继续挖到新的 ACTIVE 因子，应该继续在本文件追加，而不是覆盖本节。

### 12.1 今日目标和当前结果

今日目标：

```text
再挖 10 个新的 ACTIVE / submitted 因子，并且这 10 个里面至少包含 1 个 GOOD 或 EXCELLENT Alpha。
```

当前实际结果：

- 已确认今天新增 ACTIVE：2 个
- 其中 AVERAGE：2 个
- 其中 GOOD / EXCELLENT：0 个
- 目标进度：2 / 10
- 高等级要求：未满足
- 当前状态：继续挖掘中，不能标记 goal complete

因此，今天的目标还没有达到。当前只能说已经找到 2 个可提交、可通过 self-correlation 的新因子，但还没有完成数量目标，也还没有完成“至少 1 个 GOOD / EXCELLENT”的质量目标。

### 12.2 起始背景和账户结构

今天开始时，账户已经偏 AVERAGE-heavy。最新已确认账户结构为：

```text
AVERAGE : GOOD : EXCELLENT = 28 : 2 : 1
Total ACTIVE = 31
```

目标月度结构是：

```text
AVERAGE : GOOD : EXCELLENT = 5 : 4 : 1
```

这意味着当前的主要问题不是 ACTIVE 数量，而是等级结构偏弱。继续提交 AVERAGE 因子可以推进数量目标，但会让整体组合更偏离目标结构。因此今天的核心矛盾是：很多候选能做到高 Sharpe / 高 Fitness，但过不了 SELF_CORRELATION；能过 SELF_CORRELATION 的候选，等级又容易掉到 AVERAGE。

### 12.3 今天新增 ACTIVE 因子明细

#### 因子 1：`kqnGaJzg`

- alpha id：`kqnGaJzg`
- 表达式：

```text
group_rank(-snt1_d1_nettargetpercent, subindustry)
```

- Grade：AVERAGE
- Universe：TOP3000
- Neutralization：SUBINDUSTRY
- Decay：10
- Truncation：0.08
- Sharpe：1.33
- Fitness：1.01
- Returns：0.0727
- Turnover：0.0347
- Margin：0.004198
- Self-correlation：0.6918
- 状态：提交后确认 ACTIVE

小白解释：这个因子用的是分析师目标价相关的情绪数据。`snt1_d1_nettargetpercent` 可以理解为“目标价上调和下调之间的净比例”。取负号后，因子更偏向目标价净上调没那么强、甚至下调压力较大的股票。它能够通过 self-correlation，主要是因为表达式很纯，没有叠加账户里常见的 `-ts_delta(close, 5)` 短期反转模板，所以和已有因子相似度刚好低于 0.70。

它的不足是收益质量只刚好过基础门槛，Sharpe 1.33、Fitness 1.01，所以等级只是 AVERAGE。这个因子对今天的意义是证明 SNT1 目标价字段还有独立信息，但纯水平值不够强。

#### 因子 2：`vR5GE9Nb`

- alpha id：`vR5GE9Nb`
- 表达式：

```text
0.65*group_rank(ts_zscore(snt1_d1_sellrecpercent, 60), subindustry)
+0.35*group_rank(-ts_delta(close, 5), subindustry)
```

- Grade：AVERAGE
- Universe：TOP3000
- Neutralization：SUBINDUSTRY
- Decay：10
- Truncation：0.08
- Sharpe：1.87
- Fitness：1.31
- Returns：0.0858
- Turnover：0.1751
- Margin：0.00098
- Self-correlation：0.6640
- 状态：提交后确认 ACTIVE

小白解释：`snt1_d1_sellrecpercent` 反映分析师卖出评级相关信息。`ts_zscore(..., 60)` 不是直接看卖出评级比例高不高，而是看它相对过去 60 天是否异常。这样做会把“静态情绪水平”变成“情绪变化信号”，更容易和已有因子区分开。第二项 `-ts_delta(close, 5)` 是短期反转稳定器，意思是近期跌得多的股票会得到更高分。

这个因子的 Sharpe 和 Fitness 都比第一个更好，而且 self-correlation 只有 0.6640，说明去相关效果更好。但它的 Turnover 0.1751 较高，Margin 0.00098 较低，所以最终仍是 AVERAGE。

### 12.4 今天的搜索路径

今天不是单一路线，而是围绕“高质量但低相关”的目标尝试了多个方向。

第一类是销售惊喜和盈利动量字段，例如：

```text
mdl77_earningmomentumfactor_salesurp
mdl77_oearningmomentumfactor_salesurp
mdl77_2earningmomentumfactor400_salesurp
```

这类字段的整体 Sharpe / Fitness 很强，甚至出现过 EXCELLENT 级别候选。例如 `VkXzLXzM` 在 SECTOR neutralization 下 Sharpe 2.04、Fitness 2.02。但问题是：SUBINDUSTRY 设置下经常 LOW_SUB_UNIVERSE_SHARPE，改成 SECTOR 后又集中失败于 SELF_CORRELATION，相关性大约 0.80 到 0.84。因此它们暂时不能完成今天的 GOOD / EXCELLENT 目标。

第二类是历史高分候选复查，包括债务、`q1aepsg`、`pc_ratio`、现金流 surprise、`rel5yfwdep` 等方向。复查结果很明确：主指标好不代表还能提交，历史 GOOD / EXCELLENT 候选几乎全部 SELF_CORRELATION 失败。这个结果说明账户已有因子已经覆盖了这些老交易逻辑，继续改权重意义不大。

第三类是期权、波动率、偏度和 put/call 结构。这里测试了 `out_of_money_put_call_ratio`、`mdl77_2400_impvol`、`mdl77_2400_rmi`、ATM put/call vol、90 日 skew 等字段。大多数候选失败于 LOW_SHARPE 或 LOW_FITNESS，说明这些字段在当前模板下没有提供足够稳定的收益。

第四类是短融和借券字段。短融集中度方向出现过 AVERAGE 级 READY 候选，例如 `6XR0ekbp` 和 `e7nG3dNz`，但直接提交时仍然 SELF_CORRELATION 失败。说明短融方向不是完全没信号，而是账户已有短融类 ACTIVE 后，相邻字段也开始拥挤。

第五类是 SNT1 分析师情绪字段。这是今天唯一真正产出 ACTIVE 的方向。直接水平值能产生 GOOD 级候选，但多数提交后 self-correlation 在 0.76 到 0.83 附近失败。为了降低相关性，后面改用纯信号和时间序列变换，最终产生了 `kqnGaJzg` 与 `vR5GE9Nb` 两个 AVERAGE ACTIVE。

最新一轮未提交筛选是：

```text
candidates/manual/candidate_alphas_20260519_snt_long_decorrelate_v2.txt
runs/2026-05-19/20260519T042551Z_parallel_submit_goal/submit_summary.csv
```

设置：

```text
Universe = TOP3000
Neutralization = SUBINDUSTRY
Decay = 20
Truncation = 0.08
Mode = no-submit
```

这一轮没有直接产生 GOOD / EXCELLENT，但出现了多个 AVERAGE READY 候选，值得后续按质量顺序提交检查 self-correlation，例如：

| alpha id | 表达式摘要 | Sharpe | Fitness | Turnover |
|---|---|---:|---:|---:|
| `1YoPbxgJ` | `ts_rank(snt1_d1_downtargetpercent, 120)` + `-ts_delta(vwap, 10)` | 1.65 | 1.36 | 0.0632 |
| `kqnO2QL6` | `ts_delta(snt1_d1_downtargetpercent, 60)` + `-ts_delta(vwap, 10)` | 1.52 | 1.25 | 0.0651 |
| `O0nVPkdg` | `ts_rank(snt1_d1_downtargetpercent, 120)` + `-(close-open)` | 1.52 | 1.22 | 0.0681 |
| `LLnraLW2` | `-ts_delta(snt1_d1_nettargetpercent, 120)` + `-ts_delta(vwap, 10)` | 1.49 | 1.20 | 0.0645 |
| `58LebEZM` | `-ts_delta(snt1_d1_nettargetpercent, 60)` + `-ts_delta(vwap, 10)` | 1.49 | 1.19 | 0.0655 |

这些候选适合用来继续填 ACTIVE 数量，但根据当前结果，它们大概率仍是 AVERAGE，不能单独解决 GOOD / EXCELLENT 要求。

### 12.5 失败分析

#### SELF_CORRELATION

SELF_CORRELATION 是今天最大的瓶颈。它表示新因子和账户里已有因子太像，WorldQuant 不允许把同一类交易逻辑重复提交。今天很多候选在 Sharpe / Fitness 上已经够 GOOD 或 EXCELLENT，但被相关性挡住。

典型失败：

- salesurp + `rel5yocfp` 的 SECTOR 版本：主指标强，但 self-correlation 约 0.80 到 0.84。
- SNT1 当前水平值 + 短期反转：多个 GOOD 候选，self-correlation 多在 0.76 到 0.83。
- 历史 GOOD / EXCELLENT 候选：债务、`q1aepsg`、`pc_ratio`、现金流 surprise、`rel5yfwdep` 等方向全部失败。

这说明当前账户已经有明显的拥挤暴露。后续要先换信息源或换信号形态，而不是继续微调权重。

#### LOW_SUB_UNIVERSE_SHARPE

LOW_SUB_UNIVERSE_SHARPE 主要出现在销售惊喜方向。它的意思是：整体股票池表现强，但拆到子股票池后不够稳定。对初学者来说，可以理解为“平均成绩很好，但某些分组里表现不行”，这种因子容易依赖特定行业或特定股票段。

销售惊喜方向在 SUBINDUSTRY 下经常失败于这个检查。改成 SECTOR 可以修复一部分，但修复后又触发 SELF_CORRELATION。因此这个方向仍有经济价值，但当前不能直接成为可提交 GOOD / EXCELLENT。

#### LOW_FITNESS 和 LOW_SHARPE

LOW_FITNESS / LOW_SHARPE 主要出现在 TOP500 / TOP1000 缩小 universe、期权波动率字段、部分原始 analyst revision 字段上。缩小股票池没有自动提升质量，反而降低了稳定性；期权类字段在当前模板下也没有足够收益强度。

#### HIGH_TURNOVER

今天 HIGH_TURNOVER 不是主要失败来源。真正需要注意的是，`vR5GE9Nb` 的 Turnover 已经达到 0.1751，虽然没有触发失败，但 margin 变低。后续 SNT1 扩展应优先用 decay 20 或更慢窗口控制换手。

### 12.6 当前市场 / 数据状态理解

第一，旧价值、债务、短期反转、`rel5yfwdep` 一类逻辑已经很拥挤。它们不是没有收益，而是和账户已有因子太相似。

第二，销售惊喜和盈利动量字段依然有很强的经济信号。高 Sharpe / 高 Fitness 候选反复出现，说明市场可能仍没有完全吸收销售 surprise 信息。但这些收益在子股票池中不够均匀，且和已有 earnings / revision 因子相关性偏高。

第三，SNT1 分析师情绪是今天最有效的新信息源。它的水平值足够强，但容易相关；时间序列变换能降低相关性，但会牺牲等级。后续需要在“去相关”和“保留强度”之间找到更好的折中。

第四，当前阶段的核心不是找不到强候选，而是找不到“强且足够不同”的候选。GOOD / EXCELLENT 的突破口应来自更不同的信息源或更不同的信号定义。

### 12.7 下一步应该尝试什么

优先继续提交最新 decay 20 / vwap 稳定器的 SNT1 READY 候选，用来测试是否能把 ACTIVE 数量从 2 个推进到更多：

```text
0.70*group_rank(ts_rank(snt1_d1_downtargetpercent, 120), subindustry)
+0.30*group_rank(-ts_delta(vwap, 10), subindustry)

0.70*group_rank(ts_delta(snt1_d1_downtargetpercent, 60), subindustry)
+0.30*group_rank(-ts_delta(vwap, 10), subindustry)

0.70*group_rank(-ts_delta(snt1_d1_nettargetpercent, 120), subindustry)
+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

同时，为了追求 GOOD / EXCELLENT，不能只提交这些 AVERAGE READY。下一步应另开更不同的信息源：

- 非 SNT1 的新闻 / 事件字段，特别是和 earnings 不完全重叠的事件强度或舆情变化。
- 更慢的 analyst revision 变化率，但避免直接使用已经 self-correlation 失败的当前水平值。
- 短融字段的更长窗口时间序列变化，例如 60/120 日 delta、rank、zscore，而不是当前水平值。
- 期权方向如果继续做，应减少短期价格项权重，并测试更慢 decay；当前简单 put/call 和 skew 模板表现太弱。

### 12.8 下一步应该避免什么

短期内应避免：

- 继续围绕 `rel5yfwdep` 改权重。
- 继续直接提交 salesurp + `rel5yocfp` 的 SECTOR 版本。
- 继续提交 SNT1 当前水平值 + `-ts_delta(close, 5)` 的 GOOD 候选。
- 继续复查历史债务、`q1aepsg`、`pc_ratio`、现金流 surprise 的旧 GOOD 候选。
- 为了凑数量提交 Sharpe / Fitness 勉强过线但 self-correlation 没有明显余量的候选。

当前最重要的执行原则是：先找到至少 1 个低相关的 GOOD / EXCELLENT，再用 AVERAGE READY 候选补数量。否则即使完成 10 个 ACTIVE，也会进一步加重账户 AVERAGE-heavy 的问题。

---

## 13. 后续补录：新增 ACTIVE 已到 4 个，但 GOOD / EXCELLENT 仍未完成

本节记录在“AGENTS.md 要求补正总结”之后继续挖掘的结果。当前目标仍然没有完成。

当前结果：

- 今日新增 ACTIVE：4 个
- 今日新增 AVERAGE：4 个
- 今日新增 GOOD / EXCELLENT：0 个
- 目标进度：4 / 10
- 当前账户总 ACTIVE：33 个
- 当前账户等级结构：

```text
AVERAGE : GOOD : EXCELLENT = 30 : 2 : 1
```

### 13.1 新增 ACTIVE 因子 3：`78xMg0AQ`

- alpha id：`78xMg0AQ`
- 表达式：

```text
0.70*group_rank(-mdl77_oearningsqualityfactor_lccau, subindustry)
+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

- Grade：AVERAGE
- Universe：TOP3000
- Neutralization：SUBINDUSTRY
- Decay：20
- Truncation：0.08
- Sharpe：1.61
- Fitness：1.03
- Returns：0.0515
- Turnover：0.0490
- Margin：0.002104
- LOW_SUB_UNIVERSE_SHARPE：PASS，value 1.06，limit 0.70
- 状态：提交后确认 ACTIVE

小白解释：`mdl77_oearningsqualityfactor_lccau` 是“异常应计负债变化”相关字段。应计负债可以粗略理解为公司已经发生但还没有现金结算的负债项目。异常变化有时代表经营质量、费用确认或会计处理发生变化。这里取负号，表示偏好异常应计负债压力较低的一侧。这个因子的优点是和 SNT1、sales surprise、rel5y 旧价值锚明显不同，所以能通过提交检查；缺点是 Fitness 只有 1.03，等级仍是 AVERAGE。

### 13.2 新增 ACTIVE 因子 4：`gJmdaqEK`

- alpha id：`gJmdaqEK`
- 表达式：

```text
0.15*group_rank(-mdl177_2_5yearrelativevaluefactor_rel5yfwdep, subindustry)
+0.60*group_rank(-mdl77_oearningsqualityfactor_lccau, subindustry)
+0.25*group_rank(-ts_delta(vwap, 10), subindustry)
```

- Grade：AVERAGE
- Universe：TOP3000
- Neutralization：SUBINDUSTRY
- Decay：20
- Truncation：0.08
- Sharpe：1.98
- Fitness：1.49
- Returns：0.0706
- Turnover：0.0481
- Margin：0.002932
- LOW_SUB_UNIVERSE_SHARPE：PASS，value 1.30，limit 0.86
- 状态：提交后确认 ACTIVE

小白解释：这个因子是在 `78xMg0AQ` 的会计质量信号上，加了很小权重的历史强价值锚 `rel5yfwdep`。`rel5yfwdep` 过去能给出很高 Sharpe，但现在非常拥挤，权重稍高就会 SELF_CORRELATION 失败。因此这里把它降到 15%，主要仍由 `lccau` 会计质量信号驱动。这个版本成功 ACTIVE，Sharpe 和 Fitness 都比 `78xMg0AQ` 好，但 WorldQuant 最终等级仍是 AVERAGE，没有满足今天的 GOOD / EXCELLENT 条件。

### 13.3 本轮新增搜索路径

#### SNT1 decay 20 长窗口候选

提交了最新 decay 20 / vwap 稳定器的 SNT1 READY 候选，例如：

- `1YoPbxgJ`
- `kqnO2QL6`
- `O0nVPkdg`
- `LLnraLW2`
- `58LebEZM`

结果：全部 SELF_CORRELATION 失败，相关性约 0.87 到 0.90。结论是：SNT1 长窗口虽然让换手下降，但持仓形状仍然和已有分析师情绪 / earnings 暴露太像。

#### 低使用率会计质量与短融变化

测试了 `candidate_alphas_20260519_distinct_lowuse_v1.txt`。其中：

- `78xMg0AQ` 成功 ACTIVE。
- `QPngd2xG`、`kqnObL0O`、`WjN0wz3Z`、`LLnrb3me` 等被 SELF_CORRELATION 拒绝。

结论：会计质量异常字段是今天真正新增的独立信息源，但多数相邻变体仍然难以直接转化为高等级。

#### 会计质量 SECTOR 变体

测试了 `candidate_alphas_20260519_accounting_quality_variants.txt`，把部分表达式改到 SECTOR neutralization。结果主指标变强，但提交后全部 SELF_CORRELATION 失败，典型候选包括：

- `Xgkel0r0`: Sharpe 1.60，Fitness 1.38，SELF_CORRELATION 0.8044
- `Grnx379x`: Sharpe 1.57，Fitness 1.34，SELF_CORRELATION 0.8055
- `0mA6K6dv`: Sharpe 1.53，Fitness 1.34，SELF_CORRELATION 0.8145

结论：`lccau` 成功后，相邻会计质量组合很快变得 self-correlated，不能继续靠同族权重微调。

#### FANGMA 低使用率模型族

测试了 `candidate_alphas_20260519_fangma_lowuse_probe.txt`，包括 `mdl77_fangma_emf*`、`mam*`、`dvm*`、`gpam*` 等字段。结果几乎全部 LOW_SHARPE / LOW_FITNESS，没有 READY_TO_SUBMIT 候选。结论：虽然低使用率，但当前模板下没有足够收益强度。

#### 全市场 `rank()` 改形态

测试了 `candidate_alphas_20260519_global_rank_reformulations.txt`，希望用 `rank()` 改变持仓形状。结果主指标明显下降，基本没有可提交价值。结论：对这些字段来说，简单从 `group_rank` 改成 `rank` 会损失太多行业内相对信息。

#### 强锚降相关

测试了 `candidate_alphas_20260519_strong_anchor_decorrelate.txt` 和 `candidate_alphas_20260519_strong_anchor_low_weight.txt`。这一方向产生了很多 GOOD 级主指标候选，例如：

- `e7nvQnnd`: Sharpe 2.17，Fitness 1.96，Grade GOOD，但 SELF_CORRELATION 0.9134
- `xAeWbe1m`: Sharpe 2.18，Fitness 1.94，Grade GOOD，但 SELF_CORRELATION 0.8896
- `qMn37NYP`: Sharpe 2.00，Fitness 1.76，Grade GOOD，但 SELF_CORRELATION 0.7736
- `j2nxaPOZ`: Sharpe 1.90，Fitness 1.62，Grade GOOD，但 SELF_CORRELATION 0.7874

唯一通过的是 `gJmdaqEK`，但等级只有 AVERAGE。结论：强锚只要还有 10%-20% 权重，就仍然可能把指标拉高；但如果要达到 GOOD，self-correlation 仍然偏高。能通过的版本强锚更弱或形状更不同，等级又掉回 AVERAGE。

#### `trade_when` 高成交量过滤

测试了 `candidate_alphas_20260519_trade_when_good_rescue.txt`。`trade_when(volume>adv20, alpha, -1)` 能保留一部分强指标，例如：

- `Jjn11PeO`: Sharpe 1.89，Fitness 1.60
- `QPnggN2w`: Sharpe 1.97，Fitness 1.51

但提交后仍全部 SELF_CORRELATION 失败。结论：高成交量过滤能改变换手和路径，但没有足够改变核心持仓暴露。

### 13.4 当前失败模式更新

当前最主要失败模式仍是 SELF_CORRELATION，但细节更清楚了：

- GOOD 级候选不是没有，很多 Sharpe / Fitness 已经足够。
- 只要表达式里保留 `rel5yfwdep`、debt 或 SNT 当前/近似当前暴露，self-correlation 很容易高于 0.75。
- `lccau` 是低相关新源，但单独强度不够；加入强锚后能提高指标，但又重新触发 self-correlation。
- `trade_when`、SECTOR neutralization、`rank()` 改形态都没有从根本上解决高相关问题。

### 13.5 下一步建议

后续如果继续今天目标，建议分成两条线：

1. 补数量：可以继续寻找 `lccau` 之外的独立会计异常字段、短融时间序列变化字段，目标是 AVERAGE ACTIVE，把 4 / 10 推进到 10 / 10。
2. 找 GOOD / EXCELLENT：不要再围绕 `rel5yfwdep`、debt、salesurp、SNT1 当前水平调权重。更合理的是找全新信息源，例如非 earnings 的新闻事件、管理层行为、资本结构事件、分析师覆盖数量变化、异常成交/流动性结构。

短期最应该避免的是继续“强锚 + 新弱信号”的微调。今天已经证明这能制造 GOOD 级回测，但提交检查很难过。

---

## 14. AGENTS.md 合规补录：当前完整状态快照

本节专门补齐 `AGENTS.md` 的 `Goal Completion Documentation` 要求。因为当前目标还没有完成，所以这不是最终完成总结，而是截至当前时间的完整阶段性总结。后续如果继续挖到新的 ACTIVE 因子，应该在本节后继续追加，不要覆盖。

### 14.1 今日目标和当前结果

今日目标：

```text
新增 10 个 ACTIVE / submitted 因子，并且这 10 个里至少包含 1 个 GOOD 或 EXCELLENT Alpha。
```

截至本补录：

- 今日新增 ACTIVE 因子：4 个
- 今日新增 AVERAGE 因子：4 个
- 今日新增 GOOD / EXCELLENT 因子：0 个
- 目标进度：4 / 10
- 质量目标进度：0 / 1 个 GOOD 或 EXCELLENT
- 当前目标状态：未完成，不能标记 complete

当前账户统计已经同步到 `AGENTS.md`：

```text
AVERAGE : GOOD : EXCELLENT = 30 : 2 : 1
Total ACTIVE = 33
```

这意味着今天虽然新增了 4 个可用因子，但全部是 AVERAGE。当前最重要的问题不是完全找不到 ACTIVE，而是还没有找到一个能通过提交检查的 GOOD / EXCELLENT。

### 14.2 起始背景

本日开始时，账户大约是：

```text
AVERAGE : GOOD : EXCELLENT = 26 : 2 : 1
Total ACTIVE = 29
```

目标月度结构是：

```text
AVERAGE : GOOD : EXCELLENT = 5 : 4 : 1
```

所以今天的策略不应该只追求数量。因为账户已经 AVERAGE 偏多，如果继续提交大量边缘因子，虽然 ACTIVE 数量会上升，但整体组合质量会变差。因此本日优先寻找低相关、可能变成 GOOD / EXCELLENT 的新信息源。

### 14.3 今日新增 ACTIVE 因子明细

#### 因子 1：`kqnGaJzg`

- alpha id：`kqnGaJzg`
- 表达式：

```text
group_rank(-snt1_d1_nettargetpercent, subindustry)
```

- Grade：AVERAGE
- Universe：TOP3000
- Neutralization：SUBINDUSTRY
- Decay：10
- Truncation：0.08
- Sharpe：1.33
- Fitness：1.01
- Returns：0.0727
- Turnover：0.0347
- Margin：0.004198
- Self-correlation：0.6918
- 状态：提交后确认 ACTIVE

经济直觉：这个因子使用分析师目标价净变化相关数据。`snt1_d1_nettargetpercent` 可以理解为“目标价上调和下调之间的净比例”。取负号后，因子更偏向目标价上调没那么强、甚至出现下调压力的股票。这个方向有一点逆向交易含义：市场上追逐分析师上调的人可能已经把好消息买进去，而目标价情绪较弱的股票如果没有继续恶化，反而可能出现修复。它能通过 self-correlation 的原因是表达式很纯，没有叠加常见价格反转组件；缺点是 Sharpe 和 Fitness 都只是刚过线，所以等级只有 AVERAGE。

#### 因子 2：`vR5GE9Nb`

- alpha id：`vR5GE9Nb`
- 表达式：

```text
0.65*group_rank(ts_zscore(snt1_d1_sellrecpercent, 60), subindustry)
+0.35*group_rank(-ts_delta(close, 5), subindustry)
```

- Grade：AVERAGE
- Universe：TOP3000
- Neutralization：SUBINDUSTRY
- Decay：10
- Truncation：0.08
- Sharpe：1.87
- Fitness：1.31
- Returns：0.0858
- Turnover：0.1751
- Margin：0.00098
- Self-correlation：0.6640
- 状态：提交后确认 ACTIVE

经济直觉：`snt1_d1_sellrecpercent` 反映分析师卖出评级相关信息。`ts_zscore(..., 60)` 不是看卖出评级比例本身，而是看它相对过去 60 天是否异常。这样会把静态情绪水平改成情绪变化信号，更容易和已有因子区分开。第二项 `-ts_delta(close, 5)` 是短期反转稳定器，偏向最近下跌较多的股票。这个因子的对手方可能是仍在按旧评级或短期价格趋势交易的人。缺点是 Turnover 0.1751 较高，Margin 很低，所以虽然主指标不错，最终仍是 AVERAGE。

#### 因子 3：`78xMg0AQ`

- alpha id：`78xMg0AQ`
- 表达式：

```text
0.70*group_rank(-mdl77_oearningsqualityfactor_lccau, subindustry)
+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

- Grade：AVERAGE
- Universe：TOP3000
- Neutralization：SUBINDUSTRY
- Decay：20
- Truncation：0.08
- Sharpe：1.61
- Fitness：1.03
- Returns：0.0515
- Turnover：0.0490
- Margin：0.002104
- LOW_SUB_UNIVERSE_SHARPE：PASS，value 1.06，limit 0.70
- 状态：提交后确认 ACTIVE

经济直觉：`mdl77_oearningsqualityfactor_lccau` 是异常应计负债变化相关字段。应计负债可以理解为公司已经发生、但还没有用现金结算的负债项目。异常变化可能说明费用确认、经营质量或会计处理出现变化。取负号后，因子更偏好异常应计负债压力较低的一侧。这个因子的价值在于信息源和 SNT1、sales surprise、`rel5yfwdep` 都不同，所以能通过相关性检查；缺点是单独强度不够，Fitness 只有 1.03。

#### 因子 4：`gJmdaqEK`

- alpha id：`gJmdaqEK`
- 表达式：

```text
0.15*group_rank(-mdl177_2_5yearrelativevaluefactor_rel5yfwdep, subindustry)
+0.60*group_rank(-mdl77_oearningsqualityfactor_lccau, subindustry)
+0.25*group_rank(-ts_delta(vwap, 10), subindustry)
```

- Grade：AVERAGE
- Universe：TOP3000
- Neutralization：SUBINDUSTRY
- Decay：20
- Truncation：0.08
- Sharpe：1.98
- Fitness：1.49
- Returns：0.0706
- Turnover：0.0481
- Margin：0.002932
- LOW_SUB_UNIVERSE_SHARPE：PASS，value 1.30，limit 0.86
- 状态：提交后确认 ACTIVE

经济直觉：这个因子以 `lccau` 会计质量为主，加入 15% 的 `rel5yfwdep` 价值锚和 25% 的 10 日 VWAP 反转。`rel5yfwdep` 是历史上很强的价值类字段，但现在非常拥挤，权重稍高就会 SELF_CORRELATION 失败。这里把它降到 15%，让会计质量仍是主驱动。对手方可能是只看传统估值或短期价格走势、没有及时反映会计质量变化的交易者。这个因子主指标已经接近 GOOD 水平，但最终等级仍是 AVERAGE，说明低相关版本牺牲了部分质量。

### 14.4 搜索路径和策略变化

第一条路线是销售惊喜和盈利动量。测试过 `mdl77_earningmomentumfactor_salesurp`、`mdl77_oearningmomentumfactor_salesurp`、`mdl77_2earningmomentumfactor400_salesurp` 等字段。很多候选在主指标上达到 GOOD / EXCELLENT，例如 salesurp + `rel5yocfp` 或 earnings quality module 的组合，但经常失败于 LOW_SUB_UNIVERSE_SHARPE。改成 SECTOR neutralization 后，子股票池问题有所缓解，但又触发 SELF_CORRELATION，相关性约 0.80 到 0.84。因此这条路线经济逻辑强，但当前不能直接提交。

第二条路线是复查历史 GOOD / EXCELLENT 候选。复查过 `rel5yfwdep`、debt、`q1aepsg`、`pc_ratio`、现金流 surprise 等方向。结论很明确：历史高分不代表今天还能提交，这些候选几乎全部 SELF_CORRELATION 失败，很多相关性高于 0.90。这说明已有因子已经覆盖了这些老交易逻辑。

第三条路线是 SNT1 分析师情绪字段。直接当前水平值能产出 GOOD 级候选，但大多 self-correlation 高于 0.70。后来改成更纯的水平值或时间序列异常值，最终得到 `kqnGaJzg` 和 `vR5GE9Nb` 两个 ACTIVE，但等级都是 AVERAGE。结论是 SNT1 仍有独立信息，但要过相关性检查会损失一部分强度。

第四条路线是会计质量和异常应计字段。`mdl77_oearningsqualityfactor_lccau` 是今天最有实际产出的新信息源，得到 `78xMg0AQ` 和 `gJmdaqEK`。但是相邻会计质量变体、SECTOR 版本、强锚混合版本大多又回到 SELF_CORRELATION 问题。结论是这个方向可以继续扩展，但不能只围绕 `lccau` 做小权重微调。

第五条路线是 FANGMA、管理质量、全市场 `rank()` 改形态、`trade_when(volume>adv20, ...)` 高成交量过滤。FANGMA 和管理质量字段多数 LOW_SHARPE / LOW_FITNESS；全市场 `rank()` 损失了行业内相对信息；`trade_when` 能保留一部分强指标，但没有足够改变核心持仓暴露，提交后仍然 SELF_CORRELATION 失败。

### 14.5 失败分析

SELF_CORRELATION 是今天最主要失败来源。简单说，它表示新因子和账户里已有因子太像。今天的问题不是没有高分回测，而是高分版本往往依赖 `rel5yfwdep`、debt、salesurp、SNT1 当前水平或已有短融结构，最终和旧因子重叠。

LOW_SUB_UNIVERSE_SHARPE 主要出现在销售惊喜方向。整体 Sharpe 很强，但拆到子股票池后表现不够稳定。对初学者来说，这表示因子可能只在某些股票段或行业段有效，泛化不够均匀。

LOW_FITNESS / LOW_SHARPE 主要出现在 TOP500 / TOP1000 缩小 universe、期权波动字段、FANGMA 低使用率字段和管理质量字段。低使用率不等于有 alpha；如果字段本身和未来收益关系弱，低使用率也无法弥补。

HIGH_TURNOVER 今天不是主要阻碍，但 `vR5GE9Nb` 的 Turnover 已到 0.1751。后续继续做 SNT1 或短期价格稳定器时，应优先 decay 20 或更慢窗口。

### 14.6 当前市场和数据状态理解

当前账户的核心状态是：容易挖到 AVERAGE，难点是低相关 GOOD / EXCELLENT。旧价值、债务、现金流 surprise、`q1aepsg`、`pc_ratio` 等方向并非没有收益，而是已经被账户里已有因子占用。销售惊喜仍然有强经济信号，但当前收益分布不够均匀，且和已有 earnings / revision 暴露相似。SNT1 和 `lccau` 是今天实际能产出的新源，但它们过相关性检查后等级只剩 AVERAGE。

因此后续要避免“找一个新弱信号，再加历史强锚把指标拉高”的惯性做法。这样很容易制造 GOOD 回测，但提交时被 SELF_CORRELATION 拒绝。

### 14.7 下一步具体候选方向

继续补数量时，可以测试和 `lccau` 不同的会计异常字段、短融时间序列变化字段、分析师覆盖变化字段。优先用慢窗口和低换手模板：

```text
0.70*group_rank(ts_delta(new_low_use_field, 60), subindustry)
+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

```text
0.80*group_rank(ts_rank(new_low_use_field, 120), subindustry)
+0.20*group_rank(-ts_delta(vwap, 10), subindustry)
```

继续找 GOOD / EXCELLENT 时，建议优先换信息源，而不是继续调权重。下一批可以集中在：

- 非 earnings 的新闻事件字段。
- 管理层行为或公司治理变化字段，但要换掉本轮已经弱的模板。
- 分析师覆盖数量变化、覆盖分歧变化，而不是评级或目标价当前水平。
- 短融和借券字段的 60 / 120 日变化率，而不是当前水平值。
- 异常成交、流动性结构、成交覆盖变化字段。

### 14.8 下一步应避免

短期内应避免：

- 继续围绕 `rel5yfwdep` 做权重微调。
- 继续提交 salesurp + `rel5yocfp` 或 salesurp + earnings quality module 的近似版本。
- 继续复查历史 debt、`q1aepsg`、`pc_ratio`、现金流 surprise 旧候选。
- 继续用强锚把弱新信号拉成 GOOD 回测后直接提交。
- 为了凑满 10 个而提交明显边缘、没有低相关余量的 AVERAGE。

当前执行原则：先继续找至少 1 个低相关 GOOD / EXCELLENT；同时用全新信息源补 ACTIVE 数量。只有当新增数达到 10 个、且其中至少 1 个是 GOOD / EXCELLENT，并且 `AGENTS.md` 与本文件同步更新后，才能把今天目标标记为完成。

---

## 15. 后续补录：新增 ACTIVE 到 5 个，仍未出现 GOOD / EXCELLENT

本节记录 liquidity / analyst coverage / momentum-model probe 之后的最新结果。当前目标仍未完成。

当前结果：

- 今日新增 ACTIVE：5 个
- 今日新增 AVERAGE：5 个
- 今日新增 GOOD / EXCELLENT：0 个
- 目标进度：5 / 10
- 当前账户总 ACTIVE：34 个
- 当前账户等级结构：

```text
AVERAGE : GOOD : EXCELLENT = 31 : 2 : 1
```

### 15.1 新增 ACTIVE 因子 5：`ZYjMVQ20`

- alpha id：`ZYjMVQ20`
- 表达式：

```text
0.70*group_rank(-mdl77_400_visiratio, subindustry)
+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

- Grade：AVERAGE
- Universe：TOP3000
- Neutralization：SUBINDUSTRY
- Decay：20
- Truncation：0.08
- Sharpe：1.67
- Fitness：1.21
- Returns：0.0863
- Turnover：0.1644
- Margin：0.00105
- LOW_SUB_UNIVERSE_SHARPE：PASS，value 1.19，limit 0.72
- SELF_CORRELATION：PASS，value 0.4998，limit 0.70
- 状态：提交后确认 ACTIVE

小白解释：`mdl77_400_visiratio` 是 visibility ratio 相关字段，可以粗略理解为“股票被市场看见、覆盖或交易关注的程度”这一类信息。这里取负号，表示偏向可见度较低的一侧，再加上 10 日 VWAP 反转稳定器。经济直觉是，低可见度股票的信息扩散可能更慢，市场反应可能不充分；对手方可能是更偏好高关注、高流动性股票的资金。这个因子的 self-correlation 只有 0.4998，说明它和已有因子差异较大，是今天少数真正低相关的新源。但 Turnover 0.1644、Margin 0.00105，最终等级仍是 AVERAGE。

### 15.2 本轮提交检查结果

本轮 no-submit 文件：

```text
candidates/manual/candidate_alphas_20260519_liquidity_coverage_momentum_probe.txt
```

运行结果：

- 候选数量：32
- READY_TO_SUBMIT：2
- 提交后 ACTIVE：1
- 提交后 REJECTED：1
- 主要失败：LOW_SHARPE、LOW_FITNESS、LOW_SUB_UNIVERSE_SHARPE

两个 READY 候选的最终结果：

| alpha id | 表达式摘要 | Sharpe | Fitness | Turnover | 最终结果 |
|---|---|---:|---:|---:|---|
| `e7nvZe1l` | `-mdl77_liquidityriskfactor_numest` + 10 日 VWAP 反转 | 1.50 | 1.25 | 0.0459 | SELF_CORRELATION 失败，value 0.7723 |
| `ZYjMVQ20` | `-mdl77_400_visiratio` + 10 日 VWAP 反转 | 1.67 | 1.21 | 0.1644 | ACTIVE，self-correlation 0.4998 |

另一个主指标较强但未提交的候选是：

```text
0.70*group_rank(-north_america_sales_exposure, subindustry)
+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

它的 Sharpe 1.78、Fitness 1.49、Turnover 0.0464，但失败于 LOW_SUB_UNIVERSE_SHARPE，因此没有提交。这个结果说明地理收入暴露方向可能有信号，但当前模板在子股票池上不够稳定。

### 15.3 本轮新增结论

分析师覆盖/可见度方向比 FANGMA、管理质量和普通价格动量更有价值，因为它至少产出了一个低 self-correlation ACTIVE。`ZYjMVQ20` 的问题不是相关性，而是等级不够高。后续可以沿 visibility / coverage 方向做更慢的时间序列变化，例如 `ts_delta(..., 60)` 或 `ts_rank(..., 120)`，目标是在保持低相关的同时提升 Fitness。

但本轮也说明，简单的流动性、规模、beta、经营杠杆和 12 个月价格动量字段大多太弱。继续围绕这些弱字段做同样模板，产出 GOOD / EXCELLENT 的概率不高。

### 15.4 下一步

当前还差：

- 5 个新增 ACTIVE
- 至少 1 个 GOOD 或 EXCELLENT

下一步应继续找全新低相关信息源。优先方向：

- visibility / coverage 的时间序列变化版本。
- 地理收入暴露的子股票池稳定性修复版本，但只有修复 LOW_SUB_UNIVERSE_SHARPE 后再提交。
- 非 earnings 的新闻事件字段。
- 短融/借券字段的慢窗口变化率，而不是当前水平。

当前不应把目标标记完成。

## 16. 最终完成总结：10 个新增 ACTIVE，包含 2 个 GOOD

这一节是对 2026-05-19 当天目标的最终补充。前面的第 15 节停留在“还差 5 个新增 ACTIVE”的中间状态；后续继续挖掘后，目标已经完成。

### 16.1 今日目标和最终结果

今日目标：

```text
今天再挖 10 个因子，这 10 个中起码包含 1 个以上的 GOOD / EXCELLENT Alpha
```

最终结果：

- 本目标开始时，账户约有 29 个 ACTIVE alpha。
- 完成后，账户确认有 39 个 ACTIVE alpha。
- 因此，本轮新增 10 个 ACTIVE alpha。
- 10 个新增 alpha 中有 2 个 GOOD：`P0nKNO5K`、`E5qxOEEG`。
- 没有新增 EXCELLENT，但“至少 1 个 GOOD / EXCELLENT”的质量目标已经满足。

完成后的账户等级分布：

```text
AVERAGE : GOOD : EXCELLENT = 34 : 4 : 1
Total = 39
```

这个分布说明：数量目标完成了，且 GOOD 数量有所增加；但整体上仍然明显偏 AVERAGE。以后继续挖因子时，不能只追求 ACTIVE 数量，应该把提交门槛继续往 GOOD / EXCELLENT 倾斜。

### 16.2 今日新增 10 个 ACTIVE 因子总表

除特别说明外，以下因子均使用：

- Universe：TOP3000
- Neutralization：SUBINDUSTRY
- Truncation：0.08
- 状态：提交后确认 ACTIVE

| 序号 | alpha id | Grade | Decay | Sharpe | Fitness | Returns | Turnover | Margin |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `kqnGaJzg` | AVERAGE | 10 | 1.33 | 1.01 | 0.0727 | 0.0347 | 0.004198 |
| 2 | `vR5GE9Nb` | AVERAGE | 10 | 1.87 | 1.31 | 0.0858 | 0.1751 | 0.000980 |
| 3 | `78xMg0AQ` | AVERAGE | 20 | 1.61 | 1.03 | 0.0515 | 0.0490 | 0.002104 |
| 4 | `gJmdaqEK` | AVERAGE | 20 | 1.98 | 1.49 | 0.0706 | 0.0481 | 0.002932 |
| 5 | `ZYjMVQ20` | AVERAGE | 20 | 1.67 | 1.21 | 0.0863 | 0.1644 | 0.001050 |
| 6 | `P0nKNO5K` | GOOD | 20 | 1.80 | 1.60 | 0.0988 | 0.0805 | 0.002456 |
| 7 | `E5qxOEEG` | GOOD | 20 | 1.92 | 1.59 | 0.0856 | 0.0709 | 0.002416 |
| 8 | `le71L2Mx` | AVERAGE | 20 | 1.93 | 1.50 | 0.0992 | 0.1638 | 0.001211 |
| 9 | `O0ngN7w1` | AVERAGE | 20 | 1.30 | 1.21 | 0.1083 | 0.0504 | 0.004295 |
| 10 | `QPn6KZkQ` | AVERAGE | 20 | 1.28 | 1.13 | 0.0970 | 0.0482 | 0.004030 |

### 16.3 每个成功因子的表达式和小白解释

#### 1. `kqnGaJzg`：分析师目标价变化方向

表达式：

```text
group_rank(-snt1_d1_nettargetpercent, subindustry)
```

参数和结果：

- Grade：AVERAGE
- Decay：10
- Sharpe：1.33
- Fitness：1.01
- Returns：0.0727
- Turnover：0.0347
- Margin：0.004198
- SELF_CORRELATION：PASS，value 0.6918

经济直觉：`snt1_d1_nettargetpercent` 属于分析师目标价或观点变化相关数据。这里取负号，表示倾向于买入同一子行业内目标价变化相对更弱、或者市场预期没有被明显抬高的股票。小白可以把它理解成“不要追已经被分析师集体上调预期的股票，而是找还没有被充分推高的股票”。对手方可能是追逐卖方上调、短期情绪过热的资金。这个因子相关性接近上限，所以虽然 ACTIVE，但质量只是 AVERAGE。

#### 2. `vR5GE9Nb`：卖出评级比例的时间标准化信号

表达式：

```text
0.65*group_rank(ts_zscore(snt1_d1_sellrecpercent, 60), subindustry)
+0.35*group_rank(-ts_delta(close, 5), subindustry)
```

参数和结果：

- Grade：AVERAGE
- Decay：10
- Sharpe：1.87
- Fitness：1.31
- Returns：0.0858
- Turnover：0.1751
- Margin：0.000980
- SELF_CORRELATION：PASS，value 0.6640

经济直觉：`snt1_d1_sellrecpercent` 可以理解为卖方分析师给出负面评级的比例。`ts_zscore(..., 60)` 是把最近数值和过去 60 天历史相比，看它是不是异常偏高或偏低。这个因子再加入 5 日价格反转，用来降低纯情绪信号的波动。它的 Sharpe 和 Fitness 不错，但 Turnover 0.1751 偏高，Margin 较薄，因此仍是 AVERAGE。

#### 3. `78xMg0AQ`：应计质量 / 盈利质量信号

表达式：

```text
0.70*group_rank(-mdl77_oearningsqualityfactor_lccau, subindustry)
+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

参数和结果：

- Grade：AVERAGE
- Decay：20
- Sharpe：1.61
- Fitness：1.03
- Returns：0.0515
- Turnover：0.0490
- Margin：0.002104

经济直觉：`mdl77_oearningsqualityfactor_lccau` 属于 earnings quality，也就是盈利质量相关字段。盈利质量类因子通常试图区分“利润是真实现金流支持的”还是“利润更多来自会计应计项”。这里取负号，说明在这个数据定义下，较低的一侧在回测中更有利。对手方可能是只看表面利润、不细看利润质量的资金。这个因子的优点是换手低，缺点是 Fitness 刚过线，强度不足。

#### 4. `gJmdaqEK`：盈利质量加少量相对价值锚

表达式：

```text
0.15*group_rank(-mdl177_2_5yearrelativevaluefactor_rel5yfwdep, subindustry)
+0.60*group_rank(-mdl77_oearningsqualityfactor_lccau, subindustry)
+0.25*group_rank(-ts_delta(vwap, 10), subindustry)
```

参数和结果：

- Grade：AVERAGE
- Decay：20
- Sharpe：1.98
- Fitness：1.49
- Returns：0.0706
- Turnover：0.0481
- Margin：0.002932

经济直觉：这个因子以盈利质量为主，加入少量 `rel5yfwdep` 相对价值锚，再加 10 日 VWAP 反转。相对价值锚可以理解为“同一行业里估值或基本面相对更便宜的一侧”。它的主指标比 `78xMg0AQ` 更好，但因为 `rel5yfwdep` 已经在历史提交中被多次使用，未来不能继续把它当作默认补丁，否则容易造成 self-correlation 风险。

#### 5. `ZYjMVQ20`：可见度 / 覆盖度水平信号

表达式：

```text
0.70*group_rank(-mdl77_400_visiratio, subindustry)
+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

参数和结果：

- Grade：AVERAGE
- Decay：20
- Sharpe：1.67
- Fitness：1.21
- Returns：0.0863
- Turnover：0.1644
- Margin：0.001050
- SELF_CORRELATION：PASS，value 0.4998

经济直觉：`mdl77_400_visiratio` 是 visibility ratio 相关字段，可以粗略理解为股票被市场关注、覆盖或看见的程度。这个因子偏向可见度较低的一侧。低可见度股票的信息扩散可能更慢，短期被错误定价的概率更高。它最重要的优点是 self-correlation 只有 0.4998，说明和已有因子差异明显；缺点是 Turnover 偏高、Margin 较薄。

#### 6. `P0nKNO5K`：借券成本变化信号，本日 GOOD

表达式：

```text
0.70*group_rank(-ts_delta(mdl77_devnorthamericashortsentimentfactor_benchmark_fee, 60), subindustry)
+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

参数和结果：

- Grade：GOOD
- Decay：20
- Sharpe：1.80
- Fitness：1.60
- Returns：0.0988
- Turnover：0.0805
- Margin：0.002456
- SELF_CORRELATION：平台提交检查显示 PASS；记录中显示 value 0.7346，高于常用 0.70 经验线，因此后续不要过度依赖这个方向的相近变体。

经济直觉：`benchmark_fee` 是借券成本或做空成本相关字段。借券成本上升，通常代表做空需求变强或可借股票变紧。这里使用 60 日变化并取负号，说明不是简单买入“当前做空最拥挤”的股票，而是利用借券成本变化的方向。小白可以把它理解成“观察做空市场最近两个月的压力变化，并和行业内其他股票比较”。对手方可能是被迫追随拥挤空头或忽略借券市场变化的资金。这个因子是本日第一个 GOOD，说明短融/借券的慢变化仍然是高价值方向。

#### 7. `E5qxOEEG`：亚太收入暴露变化信号，本日 GOOD

表达式：

```text
0.70*group_rank(ts_delta(asia_pacific_sales_exposure, 60), subindustry)
+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

参数和结果：

- Grade：GOOD
- Decay：20
- Sharpe：1.92
- Fitness：1.59
- Returns：0.0856
- Turnover：0.0709
- Margin：0.002416
- SELF_CORRELATION：PASS，value 0.6550

经济直觉：`asia_pacific_sales_exposure` 描述公司收入对亚太地区的暴露程度。`ts_delta(..., 60)` 看的是 60 天变化，而不是静态水平。这个因子的逻辑是：收入地区暴露的变化可能代表公司基本面、宏观敏感度或投资者预期正在变化。市场可能不会马上完全定价这种地理收入结构变化。它是 GOOD，且 self-correlation 低于 0.70，是今天最值得继续扩展的方向之一。

#### 8. `le71L2Mx`：可见度变化信号

表达式：

```text
0.70*group_rank(-ts_delta(mdl77_400_visiratio, 60), subindustry)
+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

参数和结果：

- Grade：AVERAGE
- Decay：20
- Sharpe：1.93
- Fitness：1.50
- Returns：0.0992
- Turnover：0.1638
- Margin：0.001211

经济直觉：这个因子不是看 visibility ratio 的当前水平，而是看 60 天变化。它偏向可见度下降的一侧。直觉是，市场关注度下降可能导致价格发现变慢，或者部分资金撤出后出现可交易的错价。它的 Sharpe 和 Fitness 都不错，但 Turnover 和 Margin 让最终等级停在 AVERAGE。和 `ZYjMVQ20` 一起看，visibility / coverage 家族确实有信号，但需要更好地控制换手和交易成本。

#### 9. `O0ngN7w1`：流动性风险 pcurlia 信号

表达式：

```text
0.70*group_rank(-mdl77_2liquidityriskfactor_pcurlia, subindustry)
+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

参数和结果：

- Grade：AVERAGE
- Decay：20
- Sharpe：1.30
- Fitness：1.21
- Returns：0.1083
- Turnover：0.0504
- Margin：0.004295

经济直觉：`mdl77_2liquidityriskfactor_pcurlia` 属于流动性风险相关字段。流动性风险因子试图区分“更难交易、流动性更差”或“流动性风险被补偿”的股票。这里取负号，说明该字段较低的一侧在本模板下更有利。它的 Sharpe 不高，但 Margin 0.004295 较好、Turnover 低，适合当作低换手补充因子，而不是主攻 GOOD 的方向。

#### 10. `QPn6KZkQ`：流动性风险 sigma 信号

表达式：

```text
0.70*group_rank(-mdl77_2liquidityriskfactor_sigma, subindustry)
+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

参数和结果：

- Grade：AVERAGE
- Decay：20
- Sharpe：1.28
- Fitness：1.13
- Returns：0.0970
- Turnover：0.0482
- Margin：0.004030

经济直觉：`sigma` 在很多风险模型中与波动或不确定性有关。这个因子偏向字段值较低的一侧，并用行业内排名做标准化。它和 `O0ngN7w1` 类似，主指标不算强，但低换手、Margin 较好。它更像是为了补齐数量目标的稳健 AVERAGE，而不是未来应该重点复制的 GOOD 候选来源。

### 16.4 今日搜索路径

今天的搜索不是一次性命中，而是经历了几次方向切换。

第一阶段是分析师情绪和推荐数据。`snt1_d1_nettargetpercent`、`snt1_d1_sellrecpercent` 产出了前两个 AVERAGE。这个方向说明 analyst sentiment 仍有一定信息含量，但很多高指标候选容易被 SELF_CORRELATION 卡住，因为之前已经提交过相近的分析师情绪因子。

第二阶段是 earnings quality，也就是盈利质量。`mdl77_oearningsqualityfactor_lccau` 产出了 `78xMg0AQ` 和 `gJmdaqEK`。这个方向的好处是换手低、解释性强；问题是单独使用时 Fitness 不够高，加旧的 `rel5yfwdep` 虽能改善指标，但会增加拥挤和重复风险。

第三阶段是 visibility / coverage / geography / borrow fee。这里是今天的突破口：`ZYjMVQ20`、`P0nKNO5K`、`E5qxOEEG`、`le71L2Mx` 都来自这个扩展搜索。其中 `P0nKNO5K` 和 `E5qxOEEG` 是 GOOD，说明“短融/借券慢变化”和“地理收入暴露变化”比普通价格或普通估值更有机会产出高等级 alpha。

第四阶段是最后补齐数量的 liquidity risk。`O0ngN7w1` 和 `QPn6KZkQ` 指标不如 GOOD 候选，但低换手、Margin 较高，帮助完成 10 个 ACTIVE 的数量目标。

### 16.5 失败分析

SELF_CORRELATION：今天最典型的问题。分析师情绪、旧相对价值锚、部分 earnings quality 变体都容易和已有提交相似。经验上，如果只是换权重，或者把同一字段从 0.65 改到 0.70，大概率不能真正解决 self-correlation。应该换信息源，或者从水平值切到时间变化、从单一地区切到地理暴露变化。

LOW_FITNESS：普通 news event、普通价格动量、部分管理质量和规模/beta 类字段经常 Sharpe 尚可但 Fitness 不够。Fitness 可以粗略理解为平台对收益、风险、换手、稳定性的综合评分。LOW_FITNESS 说明这个信号即使有方向，也不够稳定或交易质量不够好。

LOW_SHARPE：很多新闻、事件和简单动量字段的 Sharpe 直接不过线。Sharpe 可以理解为单位波动带来的收益。LOW_SHARPE 的方向不适合继续细调，除非有很强的经济理由或可以换更慢窗口。

LOW_SUB_UNIVERSE_SHARPE：地理收入暴露的一些静态版本主指标很好，但子股票池 Sharpe 不够。这说明因子可能只在部分股票群体有效，稳定性不够。处理办法不是直接提交，而是换窗口、换 neutralization，或者让信号更慢、更基本面化。

HIGH_TURNOVER：visibility 和部分分析师情绪因子的换手偏高。Turnover 是组合换仓速度，越高越容易被交易成本吃掉。今天高换手因子即使 Sharpe/Fitness 好，也大多停在 AVERAGE。后续需要减少短期反转权重，或使用更长窗口、decay 20 以上。

### 16.6 今天学到的市场 / 数据状态

第一，旧的 `rel5yfwdep` 仍然有用，但已经拥挤。它可以少量稳定表达式，不应该继续当主信号。

第二，GOOD 更可能来自“新信息源”，而不是旧信号微调。今天两个 GOOD 分别来自借券成本变化和亚太收入暴露变化，都不是简单重复之前的 earnings / value / reversal 模板。

第三，时间变化比静态水平更值得关注。`ts_delta(..., 60)` 在 borrow fee、sales exposure、visibility ratio 上都表现出价值，因为它捕捉的是“信息正在变化”，而不是一个长期拥挤的水平因子。

第四，低换手不是唯一目标。`O0ngN7w1`、`QPn6KZkQ` 换手低、Margin 好，但等级仍是 AVERAGE。未来要同时看 Sharpe、Fitness、相关性和等级，不要只因为低换手就提交。

### 16.7 下一步应该优先尝试

优先方向一：地理收入暴露变化。

可尝试字段：

```text
asia_pacific_sales_exposure
north_america_sales_exposure
europe_sales_exposure
emerging_market_sales_exposure
```

可尝试模板：

```text
0.70*group_rank(ts_delta(field, 60), subindustry)
+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

以及反号版本：

```text
0.70*group_rank(-ts_delta(field, 60), subindustry)
+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

优先方向二：短融 / 借券慢变化。

可尝试字段：

```text
mdl77_devnorthamericashortsentimentfactor_benchmark_fee
mdl77_devnorthamericashortsentimentfactor_dmd_conc
mdl77_devnorthamericashortsentimentfactor_dmd_supply
mdl77_devnorthamericashortsentimentfactor_tni_ths
```

可尝试模板：

```text
0.70*group_rank(-ts_delta(field, 60), subindustry)
+0.30*group_rank(-ts_delta(vwap, 10), subindustry)
```

优先方向三：visibility / coverage 降换手版本。

可尝试模板：

```text
0.80*group_rank(-ts_delta(mdl77_400_visiratio, 120), subindustry)
+0.20*group_rank(-ts_delta(vwap, 10), subindustry)
```

或者减少短期反转权重：

```text
0.85*group_rank(-mdl77_400_visiratio, subindustry)
+0.15*group_rank(-ts_delta(vwap, 10), subindustry)
```

优先方向四：earnings quality 的新字段，而不是继续围绕 `lccau` 微调。

可尝试字段：

```text
mdl77_earningmomentumfactor_fqsurstd
mdl77_earningmomentumfactor_salesurp
mdl77_2earningmomentumfactor400_mrspe
mdl77_earningmomentumfactor_rev6
mdl77_oearningmomentumfactor_ratrev6m
mdl77_earningmomentumfactor_fy1epsskew
```

### 16.8 下一步应该避免

不要继续大量调 `rel5yfwdep` 权重。它现在更适合少量辅助，不适合做主信号。

不要继续只改 `lccau` 的 0.70 / 0.60 / 0.50 权重。今天已经证明它能产出 AVERAGE，但继续细调大概率遇到 self-correlation 或质量上限。

不要为了凑数量提交明显边缘的 ACTIVE。今天虽然完成了 10 个 ACTIVE，但最终分布变成 `34 : 4 : 1`，AVERAGE 仍然太多。后续如果目标是改善月度质量，应该把门槛提高到 Sharpe > 1.50、Fitness > 1.15，且 self-correlation 最好低于 0.60。

不要在 HIGH_TURNOVER 的 option / sentiment / visibility 变体上反复试短窗口。高换手即使过线，也很难成为 GOOD。应优先用 60 日或 120 日变化、decay 20 以上、较小的短期价格反转权重。

不要把 LOW_SUB_UNIVERSE_SHARPE 当作小问题。它说明因子在子股票池里不稳定，未来要先修复稳定性，再考虑提交。

### 16.9 最终结论

2026-05-19 的目标已经完成：新增 10 个 ACTIVE alpha，其中 2 个为 GOOD，满足“至少 1 个 GOOD / EXCELLENT”的质量要求。

今天最有价值的经验不是某一个权重，而是方向选择：新信息源明显比旧模板微调更重要。后续最应该继续的方向是地理收入暴露变化、短融/借券慢变化、visibility / coverage 的降换手版本，以及低使用率的 earnings surprise / revision 字段。最应该避免的是围绕已拥挤字段做细小权重扫描。
