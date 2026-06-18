import csv
import json
from datetime import datetime
from pathlib import Path

from config import BANKROLL_JSON, TRADES_CSV, DAILY_LOSS_LIMIT


def load_bankroll():
    if not BANKROLL_JSON.exists():
        raise FileNotFoundError(
            f"Missing {BANKROLL_JSON}. Create data/bankroll.json first."
        )

    with open(BANKROLL_JSON, "r") as f:
        return json.load(f)


def load_trades():
    if not TRADES_CSV.exists():
        return []

    with open(TRADES_CSV, "r", newline="") as f:
        return list(csv.DictReader(f))


def safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except ValueError:
        return default


def get_today_string():
    return datetime.now().date().isoformat()


def is_today(date_value):
    if not date_value:
        return False

    today = get_today_string()

    # Handles normal ISO-style dates like 2026-06-18 or timestamps starting with date
    return str(date_value).startswith(today)


def calculate_daily_realized_pl(trades):
    total = 0.0

    for trade in trades:
        mode = trade.get("mode", "").lower()
        result = trade.get("result", "").lower()

        # Only count real settled trades from today
        if mode != "real":
            continue

        if result not in {"win", "loss", "push"}:
            continue

        # Try common date column names
        date_value = (
            trade.get("settled_at")
            or trade.get("settled_date")
            or trade.get("date")
            or trade.get("created_at")
        )

        if not is_today(date_value):
            continue

        total += safe_float(trade.get("profit_loss") or trade.get("p_l") or trade.get("pl"))

    return total


def calculate_open_exposure(trades):
    exposure = 0.0
    largest_trade = None
    largest_stake = 0.0

    for trade in trades:
        mode = trade.get("mode", "").lower()
        result = trade.get("result", "").lower()

        if mode != "real":
            continue

        # Open trades usually have blank result or "open"
        if result not in {"", "open"}:
            continue

        stake = safe_float(trade.get("stake"))

        exposure += stake

        if stake > largest_stake:
            largest_stake = stake
            largest_trade = trade

    return exposure, largest_trade, largest_stake


def main():
    bankroll = load_bankroll()
    trades = load_trades()

    current_bankroll = safe_float(bankroll.get("current_bankroll"))
    daily_loss_limit = safe_float(bankroll.get("daily_loss_limit"), DAILY_LOSS_LIMIT)

    today_pl = calculate_daily_realized_pl(trades)
    open_exposure, largest_trade, largest_stake = calculate_open_exposure(trades)

    remaining_loss_allowed = abs(daily_loss_limit - today_pl)

    trading_allowed = today_pl > daily_loss_limit

    print("\n=== DAILY RISK DASHBOARD ===")
    print(f"Date: {get_today_string()}")
    print(f"Current bankroll: ${current_bankroll:.2f}")
    print(f"Today realized P/L: ${today_pl:.2f}")
    print(f"Daily loss limit: ${daily_loss_limit:.2f}")
    print(f"Open exposure: ${open_exposure:.2f}")

    if largest_trade:
        label = (
            largest_trade.get("event")
            or largest_trade.get("market")
            or largest_trade.get("notes")
            or "Unnamed open trade"
        )
        print(f"Largest open trade: {label} — ${largest_stake:.2f}")
    else:
        print("Largest open trade: None")

    if trading_allowed:
        print(f"Remaining allowed loss before stop: ${remaining_loss_allowed:.2f}")
        print("Status: REAL TRADING ALLOWED")
    else:
        print("Remaining allowed loss before stop: $0.00")
        print("Status: REAL TRADING BLOCKED — DAILY STOP HIT")

    print()


if __name__ == "__main__":
    main()