"""
Calibration utilities.

These functions adjust raw estimated probabilities based on historical
performance in similar probability buckets.
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

    value = value.strip()

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


def get_bucket(probability: float) -> tuple[float, float] | None:
    for low, high in BUCKETS:
        if low <= probability < high:
            return low, high

    if probability == 1.0:
        return BUCKETS[-1]

    return None


def result_to_score(result: str) -> float | None:
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


def historical_bucket_win_rate(
    probability: float,
    trades: list[dict] | None = None,
    min_samples: int = 20,
) -> float | None:
    """
    Return historical win rate for the bucket containing the given probability.

    Returns None if there are not enough settled trades in that bucket.
    """
    if trades is None:
        trades = read_trades()

    bucket = get_bucket(probability)

    if bucket is None:
        return None

    low, high = bucket
    scores = []

    for trade in trades:
        estimated_probability = safe_float(trade.get("estimated_probability", ""))
        score = result_to_score(trade.get("result", ""))

        if estimated_probability is None or score is None:
            continue

        if low <= estimated_probability < high:
            scores.append(score)

    if len(scores) < min_samples:
        return None

    return average(scores)


def calibrated_probability(
    raw_probability: float,
    trades: list[dict] | None = None,
    min_samples: int = 20,
    blend_weight: float = 0.50,
) -> float:
    """
    Blend raw probability with historical bucket win rate.

    If there are not enough historical trades, return raw_probability.

    blend_weight:
    - 0.50 means 50% raw estimate, 50% historical bucket result.
    - Higher means trust historical calibration more.
    """
    if not 0 < raw_probability < 1:
        raise ValueError(f"raw_probability must be between 0 and 1, got {raw_probability}")

    if not 0 <= blend_weight <= 1:
        raise ValueError(f"blend_weight must be between 0 and 1, got {blend_weight}")

    historical_rate = historical_bucket_win_rate(
        probability=raw_probability,
        trades=trades,
        min_samples=min_samples,
    )

    if historical_rate is None:
        return raw_probability

    return (1 - blend_weight) * raw_probability + blend_weight * historical_rate