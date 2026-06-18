"""
Risk guard utilities.

This module acts as the anti-tilt firewall.

It blocks trades that violate learning-mode rules:
- max $1 real stake
- max 2% bankroll risk
- stop after daily realized loss limit
- block low-confidence trades
- block PASS / REDUCE verdicts
"""

import csv
from datetime import date
from pathlib import Path


TRADE_LOG_PATH = Path("data/trades.csv")


def safe_float(value: str) -> float | None:
    if value is None:
        return None

    value = str(value).strip()

    if value == "":
        return None

    try:
        return float(value)
    except ValueError:
        return None


def read_trades(path: Path = TRADE_LOG_PATH) -> list[dict]:
    if not path.exists():
        return []

    with path.open("r", newline="") as file:
        return list(csv.DictReader(file))


def today_string() -> str:
    return date.today().isoformat()


def daily_realized_pl(
    mode: str = "real",
    target_date: str | None = None,
    path: Path = TRADE_LOG_PATH,
) -> float:
    """
    Calculate realized P/L for a given date and mode.
    """
    if target_date is None:
        target_date = today_string()

    trades = read_trades(path)
    total = 0.0

    for trade in trades:
        trade_date = trade.get("date", "").strip()
        trade_mode = trade.get("mode", "").strip().lower()
        profit_loss = safe_float(trade.get("profit_loss", ""))

        if trade_date != target_date:
            continue

        if trade_mode != mode:
            continue

        if profit_loss is None:
            continue

        total += profit_loss

    return total


def risk_guard_check(
    bankroll: float,
    stake: float,
    confidence: str,
    verdict: str,
    mode: str,
    max_learning_stake: float = 1.00,
    max_bankroll_fraction: float = 0.02,
    daily_loss_limit: float = -3.00,
) -> tuple[bool, list[str]]:
    """
    Return:
    - allowed: bool
    - issues: list[str]
    """
    issues = []

    confidence = confidence.strip().lower()
    verdict_upper = verdict.strip().upper()
    mode = mode.strip().lower()

    max_bankroll_stake = bankroll * max_bankroll_fraction

    if mode == "real":
        today_pl = daily_realized_pl(mode="real")

        if today_pl <= daily_loss_limit:
            issues.append(
                f"Daily loss limit hit: today's realized P/L is ${today_pl:.2f}"
            )

        if stake > max_learning_stake:
            issues.append(
                f"Stake exceeds learning-mode max of ${max_learning_stake:.2f}"
            )

        if stake > max_bankroll_stake:
            issues.append(
                f"Stake exceeds {max_bankroll_fraction * 100:.1f}% bankroll cap of ${max_bankroll_stake:.2f}"
            )

    if confidence == "low":
        issues.append("Confidence is low.")

    if verdict_upper.startswith("REDUCE"):
        issues.append(f"Engine verdict requires size reduction: {verdict}")

    if verdict_upper.startswith("PASS"):
        issues.append(f"Engine verdict says pass: {verdict}")

    allowed = len(issues) == 0

    return allowed, issues


def risk_guard_label(allowed: bool) -> str:
    if allowed:
        return "TRADE ALLOWED"

    return "TRADE BLOCKED"