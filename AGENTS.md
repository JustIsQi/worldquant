# WorldQuant Factor Mining Agent Instructions

## Current Submission Statistics

Update this section at the end of every daily factor-mining task.

Last updated: 2026-05-25

Current submitted factor count:

- INFERIOR: 1
- AVERAGE: 86
- GOOD: 16
- EXCELLENT: 2
- Total: 105

Current mix:

```text
INFERIOR : AVERAGE : GOOD : EXCELLENT = 1 : 86 : 16 : 2
```

Target monthly mix:

```text
AVERAGE : GOOD : EXCELLENT = 5 : 4 : 1
```

Interpretation: the 2026-05-25 run added 5 countable ACTIVE alphas: 4
AVERAGE and 1 GOOD. The run reached the requested count, but the book remains
AVERAGE-heavy and the session encountered many SELF_CORRELATION rejects after
initial successes in short-borrow and receivables-quality fields. Future mining
should continue to switch information sources quickly after one or two wins in
a family.

## Strategic Objective

Future mining should optimize for quality, not only for the number of ACTIVE
alphas. The monthly target mix is:

```text
AVERAGE : GOOD : EXCELLENT = 5 : 4 : 1
```

Treat this as the default portfolio-quality goal. For every 10 new submitted
ACTIVE alphas, aim for roughly 5 AVERAGE, 4 GOOD, and 1 EXCELLENT. If the
current month is already AVERAGE-heavy, raise submission thresholds and spend
more budget on stronger candidates rather than accepting marginal ACTIVE
alphas.

## Countable Quality Grades

For mining goals, only count newly submitted ACTIVE alphas whose quality grade
is `AVERAGE`, `GOOD`, or `EXCELLENT`. Do not count `INFERIOR`, `Below average`,
or any lower/unclear quality label toward the requested target number, even if
the alpha is technically ACTIVE. Record those low-grade ACTIVE alphas for
learning and statistics, but keep mining until the requested count is satisfied
with countable-quality alphas.

## Current Lessons

The existing strategy has worked, but it is becoming crowded:

- `rel5yfwdep` appears in many submitted alphas and should no longer be the
  default anchor for every new candidate.
- `ts_delta(close, 5)` is useful as a de-correlation or stabilizing component,
  but repeated use raises self-correlation risk.
- Short interest, borrow, option, and earnings-estimate data have produced
  low-correlation ACTIVE alphas and remain the best sources of new signal.
- Continuing to tune weights around already-submitted expressions usually
  produces SELF_CORRELATION failures or low-quality AVERAGE alphas.
- Low-use earnings surprise and revision fields produced several new ACTIVE
  alphas on 2026-05-18, but nearby variants became crowded quickly; after one
  or two successes in a field family, switch field source rather than submitting
  same-family sign/weight variants.
- Cash-flow surprise and earnings-quality module fields can show strong
  Sharpe/Fitness, but many variants self-correlate with the new earnings
  surprise set. Use them selectively and require a strong self-correlation
  margin.
- On 2026-05-20, liquidity-risk fields under `MARKET` neutralization produced
  several ACTIVE alphas, including one GOOD from `covol`, but direct level and
  tiny-weight variants quickly became self-correlated. `trade_when(volume>adv20,
  ...)` helped one `voldiff_pc` candidate pass, but most gated variants still
  failed SELF_CORRELATION.
- Later on 2026-05-20, two additional ACTIVE alphas came from new sources:
  option implied-volatility skew change and `mdl77_2earningmomentumfactor400_surp`.
  The `surp` result was GOOD, reinforcing that new earnings-surprise fields are
  preferable to more liquidity-risk retuning.

The default mindset should be: find a new information source first, then use
small stabilizing components only if they improve Fitness and self-correlation.

## Quality Gate

Before submitting a candidate, prefer these stricter thresholds when the goal
is quality improvement:

- Sharpe > 1.50
- Fitness > 1.15
- Turnover < 0.20 when possible
- Self-correlation estimate or final check comfortably below 0.70, ideally
  below 0.60
- No LOW_SUB_UNIVERSE_SHARPE failure

Candidates below the standard WorldQuant pass line may still be useful for
learning, but should not be treated as monthly-quality submissions. When a
candidate is only barely ACTIVE, record the reason for submitting it.

## Operational Defaults

Current WorldQuant BRAIN Simulation concurrency can be set to 3. For daily
mining runs, keep both `run.workers` and `run.max_inflight` at `3` unless
WorldQuant rate limiting becomes severe. These two values together control
the effective number of candidates moving through simulation/submission in
parallel.

## Priority Mining Directions

### 1. Low-Use Earnings Surprise And Analyst Revision

This is the highest-priority direction for improving GOOD and EXCELLENT odds.
Recent successful or promising signals include:

- `skewness_leading_12m_eps_estimates`
- `quarterly_earnings_surprise_stddev`
- `standardized_unexpected_earnings_2`

Prioritize adjacent low-use fields such as:

- `mdl77_earningmomentumfactor_fqsurstd`
- `mdl77_earningmomentumfactor_salesurp`
- `mdl77_2earningmomentumfactor400_mrspe`
- `mdl77_earningmomentumfactor_rev6`
- `mdl77_oearningmomentumfactor_ratrev6m`
- `mdl77_earningmomentumfactor_fy1epsskew`

Useful starting template:

```text
0.65*group_rank(new_earnings_signal, subindustry)
+0.35*group_rank(-ts_delta(close, 5), subindustry)
```

Test both signs when the field meaning is ambiguous.

### 2. Option Volatility, Skew, And Put/Call Structure

`pc_ratio` and `voldiff_pc` have already worked. Continue in this family, but
control turnover more aggressively because some option-derived candidates have
high turnover.

Candidate fields to explore:

- `out_of_money_put_call_ratio`
- `mdl77_2400_ctpmto`
- `mdl77_2400_impvol`
- `mdl77_2400_rmi`
- `mdl77_2liquidityriskfactor_atmputvol`
- `mdl77_liquidityriskfactor_atmcallvol`
- `mdl77_pricemomentumfactor_skew90drtn`
- `mdl77_opricemomentumfactor_skew90cortn`

Prefer decay 20 or a smaller short-reversal component when turnover rises.

### 3. Short Interest And Borrow Market Fields

Short and borrow data remain useful, but avoid repeating the same
`rel5yfwdep + lend_supply/onloan_conc` structure. Explore adjacent fields and
use different anchors.

Candidate fields:

- `mdl77_devnorthamericashortsentimentfactor_conc_ratio`
- `mdl77_devnorthamericashortsentimentfactor_dmd_conc`
- `mdl77_devnorthamericashortsentimentfactor_dmd_supply`
- `mdl77_devnorthamericashortsentimentfactor_tni_ths`
- `mdl77_2liquidityriskfactor_sip`
- `mdl77_2liquidityriskfactor_monchgsip`

Preferred anchors instead of overusing `rel5yfwdep`:

- `rel5yocfp`
- industry-relative value fields
- cash-flow quality fields
- low-use profitability or earnings quality fields

### 4. News, Event, And Social Data

Treat this as a smaller exploratory bucket. Some analyst sentiment candidates,
such as `snt1_d1_earningstorpedo`, showed good metrics but self-correlation
risk. Do not keep only changing weights. Instead, vary the information source,
universe, neutralization, or non-price anchor.

## Directions To Deprioritize

Avoid spending significant budget on:

- More `q1aepsg` weight tuning
- More `rel5yfwdep` weight tuning
- More debt/liabilities variants
- Pure short-term price reversal
- High-turnover option variants unless decay or signal design reduces turnover
- Re-submitting the same expression under many settings without a clear
  self-correlation reason

These areas can still be used for small stabilizing components, but they should
not be the main source of new monthly submissions.

## Candidate Construction Rules

Start with simple, interpretable expressions:

```text
group_rank(field, subindustry)
group_rank(-field, subindustry)
```

Only add a second component when it improves Fitness, turnover, or
self-correlation. Good default mixes:

```text
0.65*group_rank(new_signal, subindustry)
+0.35*group_rank(-ts_delta(close, 5), subindustry)

0.70*group_rank(new_signal, subindustry)
+0.30*group_rank(slow_anchor, subindustry)

0.80*group_rank(new_signal, subindustry)
+0.20*group_rank(slow_anchor, subindustry)
```

Do not sweep many tiny weight changes. Try two to four defensible weights, then
move on if the family is not promising.

## Daily Review Workflow

After each run:

1. Classify candidates by information source, not just expression text.
2. Count ACTIVE results by grade and compare the month-to-date mix against
   the 5:4:1 target.
3. Update the `Current Submission Statistics` section in this file with the
   latest AVERAGE, GOOD, EXCELLENT, total count, current mix, and date.
4. If AVERAGE is dominating, raise the gate and stop submitting borderline
   candidates.
5. If SELF_CORRELATION dominates, switch information source instead of tuning
   weights.
6. If LOW_FITNESS dominates, reduce short-window price exposure, increase
   decay, or move to slower fundamental/analyst signals.
7. If HIGH_TURNOVER appears, lower the short-reversal component or prefer
   decay 20+.

Every new submitted alpha should have a short economic explanation: what
information source it uses, who may be on the other side of the trade, and why
it should be different from the existing submitted set.

## Goal Completion Documentation

When the user starts a mining goal such as:

```text
/goal 今天挖3个因子
```

interpret the number as the required count of newly mined ACTIVE/submitted
factors for the current session with a countable quality grade: `AVERAGE`,
`GOOD`, or `EXCELLENT`. `INFERIOR`, `Below average`, and lower/unclear grades
do not satisfy the target count. After the target count is reached, do not stop
with only a brief status update. Before marking the work complete, create a
detailed strategy summary under `docs/`.

If the daily target count has already been reached but there are still
unfinished candidates from the current session, do not stop immediately.
This includes candidates that are still backtesting, candidates with pending
submit/check results, and candidates that have passed simulation but have not
yet been submitted. Wait for these already-started candidates to reach a final
result, submit eligible candidates when appropriate, and record the final
outcomes before ending the task.

The summary filename must include the local date:

```text
docs/factor_mining_strategy_summary_YYYY-MM-DD.md
```

For example, on 2026-05-18:

```text
docs/factor_mining_strategy_summary_2026-05-18.md
```

If a file for the date already exists, append a new section instead of
overwriting useful prior notes.

The document is for a beginner in quantitative research. Write it in Chinese,
explain jargon, and avoid assuming the reader already understands alpha mining.
Make the summary as detailed as the run data allows.

Include at least:

1. Today's target and final result, including how many new factors were mined.
2. The starting context: current submitted factor mix, especially the
   AVERAGE/GOOD/EXCELLENT distribution if known.
3. Each newly mined factor:
   - alpha id
   - expression
   - grade if known
   - universe, neutralization, decay, truncation if known
   - Sharpe, Fitness, returns, turnover, margin if known
   - whether it was ACTIVE immediately, pending, or confirmed later
4. The economic intuition of each successful factor in beginner-friendly
   language: what information source it uses, why it may predict returns, and
   who may be on the other side of the trade.
5. The search path:
   - which candidate families were tried
   - which fields looked promising
   - which fields failed
   - why the strategy changed during the session
6. Failure analysis:
   - SELF_CORRELATION
   - LOW_FITNESS
   - LOW_SHARPE
   - LOW_SUB_UNIVERSE_SHARPE
   - HIGH_TURNOVER, if relevant
7. What was learned about the current market/data regime.
8. What should be tried next, with concrete candidate fields and templates.
9. What should be avoided next, especially crowded fields or repeated weight
   tuning that is likely to produce self-correlation.

The goal is that a future agent or a beginner reader can open the summary and
understand not only what was submitted, but why the day developed that way and
how to continue from the exact point where the session ended.
