"""
Calibration dashboard for Edge Engine.

This script checks whether estimated probabilities match actual outcomes.

Example:
If you estimate 70% on many trades, do those trades win around 70%?
"""

import csv
from pathlib import Path


TRADE_LOG_PATH = Path("data/trades.csv")


BUCKETS = [
    (0.50, 0.55),
    (0.55, 0.60),
    (0.60, 0.65),
    (0.65, 0.70),
    (0.70, 0.75),
    (0.75, 0.80),
    (0.80, 0.85),
    (0.85, 0.90),
    (0.90, 0.95),
    (0.95, 1.00),
]


def safe_float(value: str) -> float | None:
    """Convert string to float safely."""
    if value is None:
        return None

    value = value.strip()

    if value == "":
        return None

    try:
        return float(value)
    except ValueError:
        return None


def read_trades(path: Path = TRADE_LOG_PATH) -> list[dict]:
    """Read trades from CSV."""
    if not path.exists():
        raise FileNotFoundError(f"No trade log found at {path}")

    with path.open("r", newline="") as file:
        return list(csv.DictReader(file))


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def money(value: float) -> str:
    return f"${value:.2f}"


def bucket_label(low: float, high: float) -> str:
    return f"{int(low * 100)}-{int(high * 100)}%"


def get_bucket(probability: float) -> tuple[float, float] | None:
    """
    Return the probability bucket for a given estimated probability.
    """
    for low, high in BUCKETS:
        if low <= probability < high:
            return low, high

    if probability == 1.0:
        return BUCKETS[-1]

    return None


def result_to_score(result: str) -> float | None:
    """
    Convert result into calibration score.

    win = 1
    loss = 0
    push = ignored
    """
    result = result.strip().lower()

    if result == "win":
        return 1.0

    if result == "loss":
        return 0.0

    return None


def average(values: list[float]) -> float:
    if not values:
        return 0.0

    return sum(values) / len(values)


def main() -> None:
    trades = read_trades()

    settled = [
        trade for trade in trades
        if trade.get("result", "").strip().lower() in {"win", "loss"}
    ]

    bucket_data: dict[tuple[float, float], list[dict]] = {
        bucket: [] for bucket in BUCKETS
    }

    for trade in settled:
        probability = safe_float(trade.get("estimated_probability", ""))
        result_score = result_to_score(trade.get("result", ""))

        if probability is None or result_score is None:
            continue

        bucket = get_bucket(probability)

        if bucket is None:
            continue

        trade["_result_score"] = result_score
        bucket_data[bucket].append(trade)

    print("\n=== CALIBRATION DASHBOARD ===")

    if not settled:
        print("No settled win/loss trades yet. Settle trades first, then rerun this.")
        return

    print(
        f"{'Bucket':<10} "
        f"{'Trades':<8} "
        f"{'Avg Est':<10} "
        f"{'Win Rate':<10} "
        f"{'Error':<10} "
        f"{'Avg CLV':<10} "
        f"{'Avg P/L':<10}"
    )

    print("-" * 78)

    all_errors = []

    for bucket, bucket_trades in bucket_data.items():
        if not bucket_trades:
            continue

        estimated_probs = [
            safe_float(trade.get("estimated_probability", "")) or 0.0
            for trade in bucket_trades
        ]

        scores = [
            trade["_result_score"]
            for trade in bucket_trades
        ]

        clvs = [
            safe_float(trade.get("clv", ""))
            for trade in bucket_trades
        ]
        clvs = [value for value in clvs if value is not None]

        profit_losses = [
            safe_float(trade.get("profit_loss", ""))
            for trade in bucket_trades
        ]
        profit_losses = [value for value in profit_losses if value is not None]

        avg_estimate = average(estimated_probs)
        win_rate = average(scores)
        calibration_error = win_rate - avg_estimate

        all_errors.append(abs(calibration_error))

        print(
            f"{bucket_label(*bucket):<10} "
            f"{len(bucket_trades):<8} "
            f"{pct(avg_estimate):<10} "
            f"{pct(win_rate):<10} "
            f"{pct(calibration_error):<10} "
            f"{average(clvs):<10.4f} "
            f"{money(average(profit_losses)):<10}"
        )

    print("\n=== COACH READ ===")

    total_settled = len(settled)

    if total_settled < 20:
        print("Sample size is tiny. Do not draw strong conclusions yet.")
        print("For now, just keep logging trades honestly.")
        return

    avg_abs_error = average(all_errors)

    if avg_abs_error <= 0.05:
        print("Strong calibration signal: your estimates are close to reality.")
    elif avg_abs_error <= 0.10:
        print("Decent but noisy: your estimates are usable, but need tightening.")
    else:
        print("Warning: your probability estimates are poorly calibrated.")
        print("You may be overconfident or misreading markets.")