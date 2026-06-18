"""
Trade review journal.

This script reads data/trades.csv, lets you choose a settled trade that has not
been reviewed yet, then records process-quality review fields.

The goal is to improve decision quality, not just track wins and losses.
"""

import csv
from pathlib import Path


TRADE_LOG_PATH = Path("data/trades.csv")

REVIEW_COLUMNS = [
    "review_market_valid",
    "review_estimate_sourced",
    "review_followed_stake_rules",
    "review_beat_closing_line",
    "review_emotional",
    "review_lesson",
]


def read_trades(path: Path = TRADE_LOG_PATH) -> tuple[list[dict], list[str]]:
    if not path.exists():
        raise FileNotFoundError(f"No trade log found at {path}")

    with path.open("r", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader), reader.fieldnames or []


def ensure_review_columns(trades: list[dict], fieldnames: list[str]) -> list[str]:
    updated_fieldnames = list(fieldnames)

    for column in REVIEW_COLUMNS:
        if column not in updated_fieldnames:
            updated_fieldnames.append(column)

        for trade in trades:
            trade.setdefault(column, "")

    return updated_fieldnames


def write_trades(
    trades: list[dict],
    fieldnames: list[str],
    path: Path = TRADE_LOG_PATH,
) -> None:
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(trades)


def is_settled(trade: dict) -> bool:
    result = trade.get("result", "").strip().lower()
    return result in {"win", "loss", "push"}


def is_reviewed(trade: dict) -> bool:
    lesson = trade.get("review_lesson", "").strip()
    market_valid = trade.get("review_market_valid", "").strip()

    return bool(lesson or market_valid)


def show_reviewable_trades(trades: list[dict]) -> list[int]:
    reviewable_indexes = []

    print("\n=== SETTLED TRADES NEEDING REVIEW ===")

    for index, trade in enumerate(trades):
        if not is_settled(trade):
            continue

        if is_reviewed(trade):
            continue

        reviewable_indexes.append(index)

        date = trade.get("date", "")
        mode = trade.get("mode", "")
        sport = trade.get("sport", "")
        event = trade.get("event", "")
        market = trade.get("market", "")
        result = trade.get("result", "")
        profit_loss = trade.get("profit_loss", "")

        print(
            f"{index}: {date} | {mode} | {sport} | "
            f"{event} | {market} | result={result} | P/L={profit_loss}"
        )

    if not reviewable_indexes:
        print("No settled trades need review.")

    return reviewable_indexes


def ask_yes_no(prompt: str) -> str:
    while True:
        answer = input(f"{prompt} [y/n]: ").strip().lower()

        if answer in {"y", "yes"}:
            return "yes"

        if answer in {"n", "no"}:
            return "no"

        print("Please enter y or n.")


def ask_lesson() -> str:
    while True:
        lesson = input("What did you learn from this trade? ").strip()

        if lesson:
            return lesson

        print("Lesson cannot be blank.")


def review_trade(trade: dict) -> None:
    print("\n=== TRADE REVIEW ===")
    print(f"Event: {trade.get('event', '')}")
    print(f"Market: {trade.get('market', '')}")
    print(f"Mode: {trade.get('mode', '')}")
    print(f"Result: {trade.get('result', '')}")
    print(f"P/L: {trade.get('profit_loss', '')}")
    print(f"CLV: {trade.get('clv', '')}")
    print()

    trade["review_market_valid"] = ask_yes_no(
        "Was the market comparison valid?"
    )
    trade["review_estimate_sourced"] = ask_yes_no(
        "Was the probability estimate sourced rather than guessed?"
    )
    trade["review_followed_stake_rules"] = ask_yes_no(
        "Did you follow the stake/risk rules?"
    )
    trade["review_beat_closing_line"] = ask_yes_no(
        "Did you beat the closing line?"
    )
    trade["review_emotional"] = ask_yes_no(
        "Was this trade emotional, tilted, chased, or impulsive?"
    )
    trade["review_lesson"] = ask_lesson()


def main() -> None:
    trades, fieldnames = read_trades()
    fieldnames = ensure_review_columns(trades, fieldnames)

    # Save immediately so review columns exist even if the user exits early.
    write_trades(trades, fieldnames)

    reviewable_indexes = show_reviewable_trades(trades)

    if not reviewable_indexes:
        write_trades(trades, fieldnames)
        return

    try:
        selected = int(input("\nEnter trade row number to review: ").strip())
    except ValueError:
        print("Invalid row number.")
        return

    if selected not in reviewable_indexes:
        print("Invalid selection or trade does not need review.")
        return

    trade = trades[selected]
    review_trade(trade)

    write_trades(trades, fieldnames)

    print("\n=== REVIEW SAVED ===")
    print(f"Event: {trade.get('event', '')}")
    print(f"Lesson: {trade.get('review_lesson', '')}")


if __name__ == "__main__":
    main()