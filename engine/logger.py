"""
Trade logging utilities.

This module writes analyzed trades to data/trades.csv so we can track:
- EV
- CLV
- confidence
- outcomes
- calibration
- bankroll performance
"""

import csv
from datetime import date
from pathlib import Path


TRADE_LOG_PATH = Path("data/trades.csv")


FIELDNAMES = [
    "date",
    "sport",
    "event",
    "market",
    "price",
    "estimated_probability",
    "stake",
    "bankroll",
    "fee_rate",
    "confidence",
    "edge",
    "ev_per_contract",
    "expected_profit",
    "roi",
    "full_kelly",
    "quarter_kelly",
    "beginner_capped_stake",
    "verdict",
    "result",
    "closing_price",
    "clv",
    "notes",
]


def ensure_trade_log_exists(path: Path = TRADE_LOG_PATH) -> None:
    """
    Create the trade log with headers if it does not exist.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists() or path.stat().st_size == 0:
        with path.open("w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()


def log_trade(row: dict, path: Path = TRADE_LOG_PATH) -> None:
    """
    Append one analyzed trade to the CSV log.
    """
    ensure_trade_log_exists(path)

    clean_row = {field: row.get(field, "") for field in FIELDNAMES}

    with path.open("a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writerow(clean_row)


def today_string() -> str:
    """
    Return today's date in ISO format.
    """
    return date.today().isoformat()