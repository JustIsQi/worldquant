# 每日挖因子流程

> 第一次接触？先读 [factor_mining_theory_for_beginners.md](factor_mining_theory_for_beginners.md)
> 把因子家族、FAIL 排查决策树、每日迭代节奏过一遍，再回来看怎么跑命令。

## 0. 先拉一份数据字段清单（首次或每月一次）

```bash
python3 -m wq_miner.data_fields --config configs/daily.yaml
```

写到 `state/data_fields.json`，后续 daily 会用它过滤"用了不存在字段的表达式"。

## 一键 dry run

```bash
python3 -m wq_miner.daily --config configs/daily.yaml --dry-run
```

这个命令只生成当天候选池和 `report.md`，不会调用 WorldQuant BRAIN，也不会 submit。

## 真实运行

```bash
python3 -m wq_miner.daily --config configs/daily.yaml
```

默认配置会读取 `.env` 或环境变量中的账号信息，目标是凑够 3 个 ACTIVE alpha。运行产物写入：

当前默认 Simulation 并发可以设为 3：`configs/daily.yaml` 中
`run.workers: 3` 和 `run.max_inflight: 3` 会同时控制最多 3 个候选在回测/提交流程里并行。

```text
runs/YYYY-MM-DD/<run_id>_daily/
```

目录里会有：

- `candidates.txt`：当天实际使用的候选池。
- `raw/`：BRAIN simulation 和 alpha 原始 JSON。
- `submit_summary.csv`：机器可读结果。
- `report.md`：给人看的日报。

## 单独生成候选

```bash
python3 -m wq_miner.generate_candidates --config configs/daily.yaml --date 2026-05-11
```

## 从历史 run 生成日报

```bash
python3 -m wq_miner.report --run runs/2026-05-11/<run_id>_daily
```

## 调参优先级

- 想降低换手：提高 `brain.decay`，减少短窗口价格项权重。
- 当前可用 Simulation 并发：保持 `run.workers: 3` 和 `run.max_inflight: 3`。
- 如果遇到限流：降低 `run.workers` 和 `run.max_inflight`，减少并发请求。
- 想只回测不提交：把 `configs/daily.yaml` 的 `run.auto_submit` 改为 `false`。
- 想多试人工想法：把表达式放进 `candidates/manual/*.txt`。
