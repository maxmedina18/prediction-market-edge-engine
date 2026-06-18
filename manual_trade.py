"""
Manual legacy trade importer.

Writes directly to data/trades.csv.

Use this for historical / already-settled trades where you know final P/L
but do not want to run the full EV engine.

These entries leave estimated_probability blank so calibration skips them.
"""

import csv
from datetime import date
from pathlib import Path


TRADE_LOG_PATH = Path(__file__).resolve().parent / "data" / "trades.csv"

FIELDNAMES = [
    "date",
    "mode",
    "sport",
    "event",
    "market",
    "price",
    "estimated_probability",
    "calibrated_probability",
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
    "profit_loss",
    "notes",
]


def today_string() -> str:
    return date.today().isoformat()


def ensure_trade_log_exists() -> None:
    TRADE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not TRADE_LOG_PATH.exists() or TRADE_LOG_PATH.stat().st_size == 0:
        with TRADE_LOG_PATH.open("w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()


def append_trade(row: dict) -> None:
    ensure_trade_log_exists()

    clean_row = {field: row.get(field, "") for field in FIELDNAMES}

    with TRADE_LOG_PATH.open("a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writerow(clean_row)


def ask_text(prompt: str, default: str | None = None) -> str:
    raw = input(prompt).strip()

    if raw == "" and default is not None:
        return default

    if raw.lower() == "blank" and default is not None:
        return default

    return raw


def ask_float(prompt: str) -> float:
    while True:
        raw = input(prompt).strip()

        try:
            return float(raw)
        except ValueError:
            print("Please enter a valid number.")


def ask_mode() -> str:
    while True:
        mode = input("Mode [real/paper/test]: ").strip().lower()

        if mode in {"real", "paper", "test"}:
            return mode

        print("Please enter real, paper, or test.")


def ask_result() -> str:
    while True:
        result = input("Result [win/loss/push]: ").strip().lower()

        if result in {"win", "loss", "push"}:
            return result

        print("Please enter win, loss, or push.")


def main() -> None:
    print("\n=== MANUAL LEGACY TRADE IMPORTER ===")
    print("Use this for already-settled trades and combos/parlays.")
    print("Estimated probability is left blank so calibration skips it.")
    print("--------------------------------\n")

    trade_date = ask_text("Date [YYYY-MM-DD, blank=today]: ", default=today_string())
    mode = ask_mode()
    sport = ask_text("Sport: ")
    event = ask_text("Event: ")
    market = ask_text("Market: ")
    stake = ask_float("Stake / initial cost: ")
    result = ask_result()
    profit_loss = ask_float("Final profit/loss, e.g. 1.63 or -14.99: ")
    notes = ask_text("Notes: ")

    if result == "win":
        closing_price = "0.99"
    elif result == "loss":
        closing_price = "0.00"
    else:
        closing_price = ""

    row = {
        "date": trade_date,
        "mode": mode,
        "sport": sport,
        "event": event,
        "market": market,
        "price": "",
        "estimated_probability": "",
        "calibrated_probability": "",
        "stake": stake,
        "bankroll": "",
        "fee_rate": "0.00",
        "confidence": "low",
        "edge": "",
        "ev_per_contract": "",
        "expected_profit": "",
        "roi": "",
        "full_kelly": "",
        "quarter_kelly": "",
        "beginner_capped_stake": "",
        "verdict": "LEGACY MANUAL ENTRY",
        "result": result,
        "closing_price": closing_price,
        "clv": "",
        "profit_loss": profit_loss,
        "notes": notes,
    }

    append_trade(row)

    print("\nManual trade logged.")
    print(f"Wrote to: {TRADE_LOG_PATH}")
    print("Last row written:")
    print(",".join(str(row.get(field, "")) for field in FIELDNAMES))


if __name__ == "__main__":
    main()