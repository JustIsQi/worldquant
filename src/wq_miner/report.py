from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from .io_utils import read_csv_rows


def _render_family_section(
    rows: list[dict[str, str]],
    families: dict[str, Any],
    historical_skip_entries: list[dict[str, Any]],
) -> list[str]:
    from .candidates import family_of  # avoid circular at module load

    lines = ["", "## 按因子家族表现", "", "### 今日"]
    def _empty_bucket() -> dict[str, Any]:
        return {
            "attempted": 0,
            "active": 0,
            "already": 0,
            "submitted": 0,
            "failed": 0,
            "fail_reasons": Counter(),
        }

    today_stats: dict[str, dict[str, Any]] = {name: _empty_bucket() for name in families}
    today_stats["(其他)"] = _empty_bucket()
    for row in rows:
        name = family_of(row.get("expression", ""), families) or "(其他)"
        bucket = today_stats[name]
        bucket["attempted"] += 1
        result = row.get("submit_result") or ""
        if result == "ACTIVE":
            bucket["active"] += 1
        elif result == "ALREADY_ACTIVE":
            bucket["already"] += 1
        elif row.get("submit_http_status"):
            bucket["submitted"] += 1
        for fail in _json_list(row.get("failed")):
            bucket["failed"] += 1
            bucket["fail_reasons"][str(fail)] += 1

    header = "| family | attempted | active(new) | already | submitted | failed | top_fail |"
    separator = "|---|---|---|---|---|---|---|"
    lines.extend([header, separator])
    for name, bucket in today_stats.items():
        if bucket["attempted"] == 0 and name == "(其他)":
            continue
        top_fail = bucket["fail_reasons"].most_common(1)
        top = top_fail[0][0] if top_fail else "-"
        lines.append(
            f"| {name} | {bucket['attempted']} | {bucket['active']} | "
            f"{bucket['already']} | {bucket['submitted']} | {bucket['failed']} | {top} |"
        )

    if historical_skip_entries:
        lines.extend(["", "### 历史累计（skip_history.json）"])
        hist_by_family: Counter[str] = Counter()
        hist_top: dict[str, Counter[str]] = {}
        for entry in historical_skip_entries:
            fam = entry.get("family") or "(其他)"
            hist_by_family[fam] += 1
            hist_top.setdefault(fam, Counter())[str(entry.get("fail_reason") or "?")] += 1
        lines.append("| family | skipped | top_fail |")
        lines.append("|---|---|---|")
        for fam, count in hist_by_family.most_common():
            top = hist_top[fam].most_common(1)
            top_name = top[0][0] if top else "-"
            lines.append(f"| {fam} | {count} | {top_name} |")
    return lines


def trailing_week_active_count(runs_dir: Path, *, today: date | None = None, days: int = 7) -> int:
    if not runs_dir.exists():
        return 0
    today = today or date.today()
    cutoff = today - timedelta(days=days - 1)
    count = 0
    for day_dir in runs_dir.iterdir():
        if not day_dir.is_dir():
            continue
        try:
            day = date.fromisoformat(day_dir.name)
        except ValueError:
            continue
        if day < cutoff or day > today:
            continue
        for summary_path in day_dir.glob("*/submit_summary.csv"):
            for row in read_csv_rows(summary_path):
                if row.get("submit_result") == "ACTIVE":
                    count += 1
    return count


def _num(value: Any) -> float | None:
    try:
        if value in {None, ""}:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _json_list(value: str | None) -> list[Any]:
    if not value:
        return []
    try:
        data = json.loads(value)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def _best_rows(rows: list[dict[str, str]], limit: int = 8) -> list[dict[str, str]]:
    def score(row: dict[str, str]) -> tuple[float, float]:
        fitness = _num(row.get("fitness") or row.get("is_fitness")) or -999.0
        sharpe = _num(row.get("sharpe") or row.get("is_sharpe")) or -999.0
        return fitness, sharpe

    return sorted(rows, key=score, reverse=True)[:limit]


def _explain_expression(expression: str) -> str:
    if "liabilities/assets" in expression:
        return "用负债占资产比例给股票排序，核心是在测试财务杠杆信息是否能解释未来收益。"
    if "debt" in expression and "ts_delta" in expression:
        return "把债务类基本面信号和短期价格反转混在一起，目标是保留财务信息，同时降低和已有因子的相似度。"
    if "close-open" in expression or "vwap-close" in expression:
        return "用日内价格位置做反转判断，通常是在赌短期过度上涨或下跌会回归。"
    if "ts_corr" in expression:
        return "观察价格和成交量的相关性，尝试捕捉量价关系变化。"
    if "ts_std_dev" in expression:
        return "用波动率排序，测试高波动或低波动股票之后的收益差异。"
    return "这是一个给股票打分的规则，回测会检验高分股票相对低分股票是否更有优势。"


def _find_summary(run_dir: Path) -> Path | None:
    for name in ("submit_summary.csv", "summary.csv", "accepted.csv"):
        path = run_dir / name
        if path.exists():
            return path
    matches = sorted(run_dir.glob("*.csv"))
    return matches[0] if matches else None


def generate_report(
    run_dir: Path,
    *,
    target_active: int = 3,
    already_active: int = 0,
    dry_run: bool = False,
    candidate_count: int | None = None,
    target_active_per_week: int | None = None,
    weekly_active: int | None = None,
    families: dict[str, Any] | None = None,
    historical_skip_entries: list[dict[str, Any]] | None = None,
) -> Path:
    summary_path = _find_summary(run_dir)
    rows = read_csv_rows(summary_path) if summary_path else []
    active = [row for row in rows if row.get("submit_result") == "ACTIVE"]
    already_active_rows = [row for row in rows if row.get("submit_result") == "ALREADY_ACTIVE"]
    submitted = [
        row
        for row in rows
        if row.get("submit_http_status")
        and row.get("submit_result") not in {"ACTIVE", "ALREADY_ACTIVE", ""}
    ]
    unresolved = [row for row in rows if str(row.get("submit_result", "")).startswith("UNRESOLVED")]

    failures: Counter[str] = Counter()
    for row in rows:
        for name in _json_list(row.get("failed")):
            failures[str(name)] += 1
        for check in _json_list(row.get("checks")):
            if isinstance(check, dict) and check.get("result") == "FAIL":
                failures[str(check.get("name"))] += 1

    lines = [
        "# 每日挖因子报告",
        "",
        "## 今日结论",
    ]
    if dry_run:
        lines.append(
            f"- Dry run：已生成候选池，不调用 WorldQuant BRAIN API，也不会 submit。候选数：{candidate_count or 0}。"
        )
        if target_active_per_week is not None and weekly_active is not None:
            lines.append(
                f"- 近 7 天累计 ACTIVE：{weekly_active} / 周目标 {target_active_per_week}。"
            )
    else:
        lines.append(
            f"- 今日**新提交并** ACTIVE：{len(active)} / 日目标 {target_active}。"
        )
        if already_active_rows:
            lines.append(
                f"- 已 ACTIVE（账号里早已存在、本次未重复提交）：{len(already_active_rows)}。"
            )
        if target_active_per_week is not None and weekly_active is not None:
            lines.append(
                f"- 近 7 天累计 ACTIVE：{weekly_active} / 周目标 {target_active_per_week}。"
            )
        lines.append(f"- 历史累计 ACTIVE（state/active_alphas.json）：{already_active}。")
        if unresolved:
            lines.append(f"- 有 {len(unresolved)} 个候选提交后仍未最终确认，通常需要继续观察 SELF_CORRELATION。")
        if not rows:
            lines.append("- 没有找到可复盘的 CSV 结果。")

    lines.extend(["", "## ACTIVE / 提交 / 待确认 / 已存在"])
    if not rows:
        lines.append("- 暂无结果。")
    else:
        status_rows = [*active, *already_active_rows, *submitted, *unresolved]
        if not status_rows:
            lines.append("- 暂无 ACTIVE、提交或待确认记录。")
        for row in status_rows[:12]:
            lines.append(
                "- `{expr}` alpha={alpha} result={result} sharpe={sharpe} fitness={fitness} pending={pending}".format(
                    expr=row.get("expression", ""),
                    alpha=row.get("alpha_id") or "none",
                    result=row.get("submit_result") or row.get("status") or "UNKNOWN",
                    sharpe=row.get("sharpe") or row.get("is_sharpe") or "",
                    fitness=row.get("fitness") or row.get("is_fitness") or "",
                    pending=row.get("pending") or "",
                )
            )

    lines.extend(["", "## Top 候选因子"])
    for row in _best_rows(rows):
        lines.append(
            "- `{expr}` sharpe={sharpe} fitness={fitness} returns={returns} turnover={turnover} result={result}".format(
                expr=row.get("expression", ""),
                sharpe=row.get("sharpe") or row.get("is_sharpe") or "",
                fitness=row.get("fitness") or row.get("is_fitness") or "",
                returns=row.get("returns") or row.get("is_returns") or "",
                turnover=row.get("turnover") or row.get("is_turnover") or "",
                result=row.get("submit_result") or row.get("status") or "",
            )
        )
    if rows:
        lines.extend(["", "## 失败原因统计"])
        if failures:
            for name, count in failures.most_common():
                lines.append(f"- `{name}`: {count}")
        else:
            lines.append("- 本次没有明确 FAIL 检查。")
    else:
        lines.extend(["", "## 失败原因统计", "- 暂无结果。"])

    if families:
        lines.extend(_render_family_section(rows, families, historical_skip_entries or []))

    lines.extend(["", "## 小白解释：今天这些因子在赌什么"])
    explained: set[str] = set()
    for row in _best_rows(rows, limit=5):
        expression = row.get("expression", "")
        if not expression or expression in explained:
            continue
        explained.add(expression)
        lines.append(f"- `{expression}`：{_explain_expression(expression)}")
    if dry_run and not rows:
        lines.append("- 候选池会优先从低换手基本面因子出发，再混入量价反转成分来降低自相关。")

    lines.extend(
        [
            "",
            "## 明日候选方向",
            "- 如果低换手财务因子继续过核心指标，优先做去相关混合，而不是重复提交高度相似表达式。",
            "- 如果量价因子普遍 LOW_FITNESS，优先提高 decay 或降低纯价格信号权重。",
            "- 如果 HIGH_TURNOVER 增多，减少短窗口价格变化项，增加基本面或更长窗口平滑项。",
        ]
    )
    report_path = run_dir / "report.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--target-active", type=int, default=3)
    parser.add_argument("--already-active", type=int, default=0)
    args = parser.parse_args(argv)
    report_path = generate_report(
        args.run,
        target_active=args.target_active,
        already_active=args.already_active,
    )
    print(f"report={report_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
