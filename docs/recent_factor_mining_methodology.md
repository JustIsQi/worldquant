# 最近一次挖因子复盘与后续方法论

这份文档记录 2026-05-15 这轮挖因子的实际过程。目标不是只记住 4 个成功表达式，而是把背后的思路变成下一轮还能继续用的方法。

读者假设：你刚开始学量化，知道股票会涨跌，但还不熟悉因子、回测、提交检查和 self-correlation。

---

## 1. 这次到底挖到了什么

本轮最终确认 4 个新的 `ACTIVE` alpha：

| Alpha ID | Universe | 核心信号 | Sharpe | Fitness | 结果 |
|---|---:|---|---:|---:|---|
| `rKbJPA9m` | TOP3000 | 相对价值 + 盈利动量 | 1.60 | 1.33 | ACTIVE |
| `E5qglQXm` | TOP500 | 相对价值 + 盈利动量 | 1.47 | 1.15 | ACTIVE |
| `A1nnRKqY` | TOP3000 | 相对价值 + put/call ratio | 1.92 | 1.41 | ACTIVE |
| `e7nnpGmE` | TOP3000 | 相对价值 + short utilization | 1.27 | 1.23 | ACTIVE |

对应表达式：

```text
0.10*group_rank(-mdl177_2_5yearrelativevaluefactor_rel5yfwdep, subindustry)
+0.90*group_rank(-mdl177_2_earningmomentumfactor400_q1aepsg, subindustry)
```

这个表达式出了两个 ACTIVE：

- `rKbJPA9m`: TOP3000, neutralization=SECTOR
- `E5qglQXm`: TOP500, neutralization=INDUSTRY

```text
0.15*group_rank(-mdl177_2_5yearrelativevaluefactor_rel5yfwdep, subindustry)
+0.85*group_rank(-mdl177_2_pricemomentumfactor_pc_ratio, subindustry)
```

这个表达式出了：

- `A1nnRKqY`: TOP3000, neutralization=SUBINDUSTRY

```text
0.20*group_rank(-mdl177_2_5yearrelativevaluefactor_rel5yfwdep, subindustry)
+0.80*group_rank(mdl177_5shortsentimentfactor_act_util, subindustry)
```

这个表达式出了：

- `e7nnpGmE`: TOP3000, neutralization=SUBINDUSTRY

---

## 2. 新手先理解几个关键词

### 2.1 因子在做什么

一个 WorldQuant alpha 表达式本质上是在给每只股票打分。分数高的股票倾向于做多，分数低的股票倾向于做空。

比如：

```text
group_rank(-mdl177_2_pricemomentumfactor_pc_ratio, subindustry)
```

意思是：

1. 看每只股票的 put/call ratio。
2. 加负号，表示 put/call ratio 越高，分数越低。
3. 在同一个子行业里排名，避免把银行和软件公司直接比较。

### 2.2 为什么常用 `group_rank`

不同公司所属行业不同，财务结构和估值天然不同。银行高杠杆是业务模式，软件公司高杠杆可能是风险。

`group_rank(x, subindustry)` 的作用是：只在同一个子行业内部比较 `x`。这样能减少行业暴露，让表达式更像是在比较公司本身，而不是押注某个行业。

### 2.3 为什么看 Sharpe 和 Fitness

- Sharpe：收益是否稳定。越高越好。
- Fitness：WorldQuant 对 alpha 质量的综合评价，会惩罚高换手等问题。越高越好。
- Turnover：换手率。太高说明交易太频繁，真实交易成本可能吃掉收益。

这次有些候选 Sharpe 很高，但 Fitness 不够，比如短期价格反转方向：

```text
Sharpe 约 2.05，但 Fitness 只有 0.89 到 0.91
```

这类信号看起来赚钱，但交易太频繁或质量不够，不能只看 Sharpe。

### 2.4 为什么 `SELF_CORRELATION` 很关键

`SELF_CORRELATION` 失败表示：这个 alpha 和你已经提交成功的 alpha 太像了。

这次大量高分候选都死在这里。例如 q1 EPS 的很多权重变体、put/call ratio 的一些邻近表达式，Sharpe 和 Fitness 都不错，但和已经 ACTIVE 的 alpha 太相关，所以不能算新因子。

量化组合里，多样性比重复高分更重要。100 个高度相关的 alpha，实质上可能只是在押同一个方向。

---

## 3. 本轮挖掘过程复盘

### 3.1 第一阶段：从已知有效家族附近找

先尝试的是相对价值和盈利动量的组合。

核心思路：

- `mdl177_2_5yearrelativevaluefactor_rel5yfwdep` 是相对价值相关字段。
- `mdl177_2_earningmomentumfactor400_q1aepsg` 是盈利动量相关字段。
- 价值和盈利动量不是完全同一件事，组合后可能同时有估值和基本面改善两个来源。

为什么用负号：

```text
group_rank(-field, subindustry)
```

有些 model77 字段的数值方向并不一定是“越大越好”。实际挖掘里要用回测和经济含义一起判断方向。本轮有效方向是对这两个字段都取负。

成功点：

- 10% 相对价值 + 90% q1 EPS 动量，在不同 universe/neutralization 下拿到两个 ACTIVE。
- 同一表达式换 TOP500/INDUSTRY 还能过，是因为 universe 变了，组合持仓空间也变了，相关性检查没有完全卡死。

失败点：

- 很多权重微调，例如 12%、15%、20%、25% 相对价值权重，虽然指标不错，但因为和已有 ACTIVE 相关性太高，被 `SELF_CORRELATION` 拒绝。
- q1 EPS 的相邻字段变体也多数被 self-correlation 拒绝。

结论：

一旦某个表达式已经出了 ACTIVE，继续在同一字段、同一方向、只改一点权重，收益递减很快。可以试一两个 universe 或 neutralization 扩展，但不要无限重复。

### 3.2 第二阶段：试图用价格/量价方向补充

尝试过 close-vwap、短期反转、价格衰减等方向。

结果：

- Sharpe 可能很高，约 2.0。
- 但 Fitness 低，大约 0.8 到 0.9。
- 多数失败原因是 `LOW_FITNESS`。

为什么会这样：

短期价格信号通常换手高。今天涨跌、短期价差、成交量变化都变得很快，模型每天都想换仓。回测里看起来有信号，但 WorldQuant 的 Fitness 会惩罚这种不稳定或高交易成本特征。

结论：

短期价格信号可以作为辅助成分，但不要作为主线。除非你能明显降低 turnover，比如提高 decay、拉长窗口，或者只保留很小权重。

### 3.3 第三阶段：宽扫基本面 model 字段

尝试过一批 value、growth、quality、management quality、liquidity risk 字段。

结果：

- 前几条表现很弱。
- 典型结果是 Sharpe 0.5 到 1.0，Fitness 0.2 到 0.5。
- 继续大范围扫的性价比低，所以提前停止。

为什么会弱：

很多基本面字段本身已经被大量用户使用，或者字段和现有 alpha 方向重叠。还有一些字段覆盖率、更新频率和经济含义不够直接，单独用 `group_rank` 不一定形成稳定收益。

结论：

宽扫可以用来找方向，但不要一条脚本无脑跑到底。前几条如果都很弱，应及时换数据源或换构造方式。

### 3.4 第四阶段：转向低使用量 sentiment / option 字段

这一步是突破点。

先试了传统 analyst sentiment rank：

```text
snt1_d1_stockrank
snt1_d1_dynamicfocusrank
```

结果很弱，Sharpe 和 Fitness 都不够。

然后转向 model77 里的低使用量期权/情绪字段：

```text
mdl177_2_pricemomentumfactor_pc_ratio
mdl177_5shortsentimentfactor_act_util
```

成功点：

1. `put/call ratio` 方向拿到 `A1nnRKqY`。
2. `short utilization` 方向拿到 `e7nnpGmE`。

为什么这类字段更有机会：

- 它们不是普通价格、估值、盈利质量字段，和已有因子的相关性更低。
- 期权和融券数据代表另一类市场参与者的信息，比如期权交易者、做空者、证券借贷市场。
- 这些数据的经济含义和普通基本面不同，因此更容易贡献新的低相关 alpha。

---

## 4. 本轮最重要的经验

### 4.1 不要迷信高 Sharpe

本轮很多候选 Sharpe 很高，但没用。

例子：

- 价格衰减候选 Sharpe 约 2.05，但 Fitness 不足。
- put/call ratio 的一些候选 Sharpe 超过 2.0，但 self-correlation 失败。

真正能提交的 alpha 要同时满足：

1. Sharpe 够。
2. Fitness 够。
3. Turnover 不离谱。
4. Self-correlation 过。

### 4.2 成功后要立刻换“信息来源”

q1 EPS 组合出 ACTIVE 后，继续在 q1 EPS 附近挖，大部分都被 self-correlation 卡掉。

后来转向 put/call ratio 和 short utilization，才继续拿到新的 ACTIVE。

这说明：挖因子不是只找“好指标”，更是在找“不同的信息来源”。

### 4.3 先小批量筛选，再扩展设置

有效流程是：

1. 先用 TOP3000 + SUBINDUSTRY 跑一个方向。
2. 如果 Sharpe/Fitness 不够，直接放弃或改方向。
3. 如果过基本门槛但 self-correlation pending，再试 INDUSTRY、SECTOR、TOP500、TOP1000。
4. 如果一个方向已经明确弱，不要把所有 universe 都跑完。

这比“每个字段乘以所有设置”快很多。

### 4.4 符号要靠经济直觉和回测一起判断

例如 short utilization：

先跑负向：

```text
group_rank(-mdl177_5shortsentimentfactor_act_util, subindustry)
```

结果 Sharpe 约 -1.0，方向明显反了。

改成正向并混入相对价值：

```text
0.20*relative_value + 0.80*short_utilization
```

最后拿到 ACTIVE。

所以不要机械地认为“做空压力高一定要做空”。有时候高做空利用率代表 crowded short，后续反而可能反弹；也可能代表借券市场中的风险溢价。

---

## 5. 推荐的挖因子工作流

### Step 1：选一个信息来源

不要一上来就写复杂表达式。先问：这个数据代表谁的观点？

| 信息来源 | 代表什么 | 本轮表现 |
|---|---|---|
| 相对价值 | 股票相对自己历史或同行是否便宜 | 有效 |
| 盈利动量 | 分析师盈利预期是否改善 | 有效 |
| Put/call ratio | 期权市场的多空偏斜 | 有效 |
| Short utilization | 融券市场拥挤度或做空需求 | 有效 |
| 短期价格 | 最近几天涨跌、价量变化 | Sharpe 高但 Fitness 低 |
| 普通 analyst rank | 分析师综合评分 | 本轮较弱 |

### Step 2：先做行业内排名

优先模板：

```text
group_rank(field, subindustry)
group_rank(-field, subindustry)
```

如果方向不确定，两边都小批量试。

### Step 3：加一个稳定锚

本轮最有效的稳定锚是相对价值：

```text
group_rank(-mdl177_2_5yearrelativevaluefactor_rel5yfwdep, subindustry)
```

它的作用不是单独解释一切，而是给其他信号加一个慢变量底座。短期情绪、期权、融券字段可能比较噪声，混入 10% 到 30% 的相对价值，有时能提高 Fitness。

推荐权重顺序：

```text
0.10*relative_value + 0.90*new_signal
0.15*relative_value + 0.85*new_signal
0.20*relative_value + 0.80*new_signal
0.30*relative_value + 0.70*new_signal
```

不要一开始就扫 50 个权重。先试 2 到 4 个。

### Step 4：只扩展有希望的候选

如果候选满足：

- Sharpe 大于 1.25
- Fitness 大于 1.0
- 没有 LOW_SUB_UNIVERSE_SHARPE
- 只是 self-correlation pending 或提交未决

再扩展：

```text
neutralization: SUBINDUSTRY, INDUSTRY, SECTOR
universe: TOP3000, TOP1000, TOP500
decay: 6, 10, 12, 20
truncation: 0.05, 0.08
```

如果候选一开始就是 Sharpe 0.5、Fitness 0.2，不要继续扩展设置。

### Step 5：单独确认 pending

有些 alpha 提交后会停在：

```text
UNRESOLVED_200
pending ["SELF_CORRELATION"]
```

这不等于失败，也不等于成功。需要后续确认。

本轮 `A1nnRKqY` 和 `e7nnpGmE` 都经历过 pending，最后确认 ACTIVE。

---

## 6. 后续继续挖的方向

### 6.1 继续挖期权和融券，但换字段

已经成功：

```text
mdl177_2_pricemomentumfactor_pc_ratio
mdl177_5shortsentimentfactor_act_util
```

下一轮可以优先试这些相邻但不完全相同的字段：

```text
mdl177_2_liquidityriskfactor_voldiff_pc
mdl177_liquidityriskfactor_voldiff_pc_alt
mdl177_pricemomemtummodel_voldiff_pc
mdl177_5shortsentimentfactor_days_to_cover
mdl177_5shortsentimentfactor_benchmark_fee
mdl177_5shortsentimentfactor_dmd_supply
mdl177_5shortsentimentfactor_sht_int
mdl177_devnorthamericashortsentimentfactor_util
mdl177_devnorthamericashortsentimentfactor_days_to_cover
```

推荐模板：

```text
0.15*group_rank(-mdl177_2_5yearrelativevaluefactor_rel5yfwdep, subindustry)
+0.85*group_rank(field, subindustry)
```

和：

```text
0.15*group_rank(-mdl177_2_5yearrelativevaluefactor_rel5yfwdep, subindustry)
+0.85*group_rank(-field, subindustry)
```

原因：这类字段和传统基本面、价格反转、盈利动量的相关性更低，是当前最值得继续挖的方向。

### 6.2 不要继续深挖 q1 EPS 的微调权重

已经成功的 q1 EPS 方向：

```text
mdl177_2_earningmomentumfactor400_q1aepsg
```

后续不建议继续只做：

```text
0.12 / 0.15 / 0.20 / 0.25 权重微调
```

原因：本轮已经证明这些候选大多会被 self-correlation 拒绝。

如果还要挖盈利动量，应该换信息来源：

```text
mdl177_2_earningmomentumfactor400_sue
mdl177_2_earningmomentumfactor400_ratrev6m
mdl177_2_earningmomentumfactor400_stockrating
mdl177_2_globaldevnorthamerica_v502_fc_rev6
mdl177_2_globaldevnorthamerica_v502_fc_epsrm
```

并且只拿 q1 EPS 成功表达式当参考，不要复制。

### 6.3 价格类信号只做辅助，不做主线

本轮价格/价量方向的问题是 Fitness 低。

后续如果要试，应该用更慢的写法：

```text
ts_rank(returns, 120)
-ts_std_dev(returns, 60)
-ts_corr(close, volume, 60)
```

或者只作为小权重：

```text
0.80*fundamental_or_sentiment_signal + 0.20*price_signal
```

不要再用短窗口纯价格信号当主线。

### 6.4 尝试“价值 + 非传统数据”的组合

本轮最稳定的结构是：

```text
小权重相对价值 + 大权重新信息源
```

下一轮可以系统化：

| 锚 | 新信息源 | 目的 |
|---|---|---|
| 相对价值 | 期权 skew | 找估值便宜但期权情绪改善的股票 |
| 相对价值 | short utilization | 找估值/风险溢价和融券拥挤度组合 |
| 相对价值 | analyst revision | 找便宜且盈利预期改善的股票 |
| 相对价值 | quality/profitability | 避免 value trap |

### 6.5 记录失败，不要重复挖同一条死路

本轮明确不优先：

- q1 EPS 同字段微调权重。
- 同一个 put/call ratio 表达式的大量邻近变体。
- 短窗口纯价格/价量表达式。
- broad model field 无差别宽扫。
- 传统 analyst stockrank 单独使用。

---

## 7. 下一轮执行清单

### 候选生成顺序

1. 期权/融券字段，先 TOP3000 + SUBINDUSTRY。
2. 每个字段先测正负两个方向。
3. 每个方向最多测 2 个相对价值权重：0.15 和 0.20。
4. 只有 Sharpe/Fitness 过线后，再扩展 universe 和 neutralization。
5. pending 项单独确认，不要把 pending 当失败。

### 停止条件

遇到以下情况就停止当前方向：

- 连续 3 条 Sharpe 小于 1.0 且 Fitness 小于 0.7。
- 同一字段连续多个 high score 都 self-correlation。
- 仿真长时间卡在 0.1 或 0.35，先换方向，不要死等。
- 价格类信号 Sharpe 高但 Fitness 低，不继续调小参数硬凑。

### 成功后要做的事

1. 记录 alpha id、表达式、universe、neutralization、Sharpe、Fitness。
2. 远端重新 fetch alpha，确认 status 是 ACTIVE。
3. 写入 `state/active_alphas.json`。
4. 把失败方向写入 skip history 或文档。
5. 下一轮换信息来源，不要只复制成功表达式。

---

## 8. 一句话方法论

这次最有效的方法不是“疯狂扫参数”，而是：

```text
用一个稳定慢变量做锚，
叠加一个和已有 alpha 低相关的新信息源，
先小批量验证方向，
只对过线候选扩展设置，
最后严肃处理 self-correlation。
```

对新手来说，最重要的是养成这个习惯：每个 alpha 都要能回答三个问题。

1. 这个因子在赌什么？
2. 它和我已有的因子有什么不同？
3. 它为什么可能在未来继续有效？

如果这三个问题答不清楚，即使回测一时好看，也不要把它当成可靠方法。
