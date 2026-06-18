"""
Calibration dashboard.

This script checks whether your estimated probabilities match reality.

It only uses trades that have:
- estimated_probability filled in
- result = win or loss

Legacy manual entries with blank probabilities are skipped on purpose.
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


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def money(value: float) -> str:
    return f"${value:.2f}"


def average(values: list[float]) -> float:
    if not values:
        return 0.0

    return sum(values) / len(values)


def ask_mode_filter() -> str:
    while True:
        mode = input("Mode filter [real/paper/test/all]: ").strip().lower()

        if mode in {"real", "paper", "test", "all"}:
            return mode

        print("Please enter real, paper, test, or all.")


def filter_by_mode(trades: list[dict], mode_filter: str) -> list[dict]:
    if mode_filter == "all":
        return trades

    return [
        trade
        for trade in trades
        if trade.get("mode", "").strip().lower() == mode_filter
    ]


def result_to_score(result: str) -> float | None:
    result = result.strip().lower()

    if result == "win":
        return 1.0

    if result == "loss":
        return 0.0

    return None


def get_bucket(probability: float) -> tuple[float, float] | None:
    for low, high in BUCKETS:
        if low <= probability < high:
            return low, high

    if probability == 1.0:
        return BUCKETS[-1]

    return None


def main() -> None:
    print("\n=== CALIBRATION DASHBOARD ===")
    print("Checks whether your estimated probabilities match actual results.")
    print("Legacy manual entries with blank probabilities are skipped.\n")

    all_trades = read_trades()

    if not all_trades:
        print("No trades found in data/trades.csv.")
        return

    mode_filter = ask_mode_filter()
    trades = filter_by_mode(all_trades, mode_filter)

    if not trades:
        print(f"No trades found for mode: {mode_filter}")
        return

    usable_trades = []

    skipped_legacy_or_missing_prob = 0
    skipped_open_or_push = 0

    for trade in trades:
        estimated_probability = safe_float(trade.get("estimated_probability", ""))
        score = result_to_score(trade.get("result", ""))

        if estimated_probability is None:
            skipped_legacy_or_missing_prob += 1
            continue

        if score is None:
            skipped_open_or_push += 1
            continue

        usable_trades.append(
            {
                "trade": trade,
                "estimated_probability": estimated_probability,
                "score": score,
            }
        )

    print(f"Mode: {mode_filter}")
    print(f"Total trades scanned: {len(trades)}")
    print(f"Usable calibrated trades: {len(usable_trades)}")
    print(f"Skipped missing probability / legacy entries: {skipped_legacy_or_missing_prob}")
    print(f"Skipped open/push trades: {skipped_open_or_push}")

    if not usable_trades:
        print("\nNo settled win/loss trades with estimated probabilities found yet.")
        print("This is normal early on.")
        print("Use main.py for future trades so calibration can learn from them.")
        return

    print("\n=== BUCKET RESULTS ===")

    for low, high in BUCKETS:
        bucket_trades = [
            item
            for item in usable_trades
            if low <= item["estimated_probability"] < high
        ]

        if not bucket_trades:
            continue

        estimates = [item["estimated_probability"] for item in bucket_trades]
        scores = [item["score"] for item in bucket_trades]

        avg_estimate = average(estimates)
        win_rate = average(scores)
        error = win_rate - avg_estimate

        clvs = [
            safe_float(item["trade"].get("clv", ""))
            for item in bucket_trades
        ]
        clvs = [value for value in clvs if value is not None]

        profit_losses = [
            safe_float(item["trade"].get("profit_loss", ""))
            for item in bucket_trades
        ]
        profit_losses = [value for value in profit_losses if value is not None]

        print(f"\nBucket: {pct(low)} to {pct(high)}")
        print(f"Trades: {len(bucket_trades)}")
        print(f"Average estimate: {pct(avg_estimate)}")
        print(f"Actual win rate: {pct(win_rate)}")
        print(f"Calibration error: {pct(error)}")
        print(f"Average CLV: {average(clvs):.4f}")
        print(f"Total P/L: {money(sum(profit_losses))}")

        if len(bucket_trades) < 20:
            print("Sample warning: fewer than 20 trades in this bucket.")

    print("\n=== COACH READ ===")

    if len(usable_trades) < 20:
        print("Too early to judge calibration. You need more settled engine-logged trades.")
    else:
        print("Start looking for buckets where your estimated probability is consistently too high or too low.")


if __name__ == "__main__":
    main()