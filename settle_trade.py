"""
Settle a logged trade.

This script reads data/trades.csv, lets you choose an open trade by row number,
then updates:
- result
- closing_price
- clv
- profit_loss
- current bankroll, but only for real trades
"""

import csv
from pathlib import Path

from engine.settlement import calculate_clv, calculate_profit_loss
from engine.bankroll import load_bankroll, save_bankroll


TRADE_LOG_PATH = Path("data/trades.csv")


def read_trades(path: Path = TRADE_LOG_PATH) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"No trade log found at {path}")

    with path.open("r", newline="") as file:
        return list(csv.DictReader(file))


def write_trades(trades: list[dict], path: Path = TRADE_LOG_PATH) -> None:
    if not trades:
        raise ValueError("No trades to write.")

    fieldnames = trades[0].keys()

    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(trades)


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


def update_bankroll_after_settlement(mode: str, profit_loss: float) -> None:
    """
    Update bankroll only when a real-money trade is settled.
    Paper and test trades should not affect bankroll.json.
    """
    if mode.lower() != "real":
        return

    bankroll_data = load_bankroll()
    current_bankroll = float(bankroll_data.get("current_bankroll", 0.0))

    new_bankroll = round(current_bankroll + float(profit_loss), 2)
    bankroll_data["current_bankroll"] = new_bankroll

    save_bankroll(bankroll_data)

    print(
        f"Bankroll updated: ${current_bankroll:.2f} -> "
        f"${new_bankroll:.2f}"
    )


def show_open_trades(trades: list[dict]) -> list[int]:
    open_indexes = []

    print("\n=== OPEN TRADES ===")

    for index, trade in enumerate(trades):
        result = trade.get("result", "").strip().lower()

        if result == "":
            open_indexes.append(index)

            mode = trade.get("mode", "")
            date = trade.get("date", "")
            sport = trade.get("sport", "")
            event = trade.get("event", "")
            market = trade.get("market", "")
            price = trade.get("price", "")
            stake = trade.get("stake", "")

            print(
                f"{index}: {date} | {mode} | {sport} | "
                f"{event} | {market} | price={price} | stake={stake}"
            )

    if not open_indexes:
        print("No open trades found.")

    return open_indexes


def ask_result() -> str:
    while True:
        result = input("Result [win/loss/push]: ").strip().lower()

        if result in {"win", "loss", "push"}:
            return result

        print("Please enter win, loss, or push.")


def ask_float(prompt: str) -> float:
    while True:
        raw = input(prompt).strip()

        try:
            return float(raw)
        except ValueError:
            print("Please enter a valid number.")


def main() -> None:
    trades = read_trades()

    if not trades:
        print("No trades found in data/trades.csv.")
        return

    open_indexes = show_open_trades(trades)

    if not open_indexes:
        return

    try:
        selected = int(input("\nEnter trade row number to settle: ").strip())
    except ValueError:
        print("Invalid row number.")
        return

    if selected not in open_indexes:
        print("Invalid selection or trade is already settled.")
        return

    trade = trades[selected]

    mode = trade.get("mode", "").strip().lower()
    entry_price = safe_float(trade.get("price", ""))
    stake = safe_float(trade.get("stake", ""))
    fee_rate = safe_float(trade.get("fee_rate", ""))

    if entry_price is None:
        print("Cannot settle trade: missing or invalid price.")
        return

    if stake is None:
        print("Cannot settle trade: missing or invalid stake.")
        return

    if fee_rate is None:
        fee_rate = 0.07

    result = ask_result()
    closing_price = ask_float("Closing price before settlement/final resolution: ")

    clv = calculate_clv(entry_price, closing_price)
    profit_loss = calculate_profit_loss(
        price=entry_price,
        stake=stake,
        result=result,
        fee_rate=fee_rate,
    )

    update_bankroll_after_settlement(mode, profit_loss)

    trade["result"] = result
    trade["closing_price"] = closing_price
    trade["clv"] = clv
    trade["profit_loss"] = profit_loss

    write_trades(trades)

    print("\n=== TRADE SETTLED ===")
    print(f"Event: {trade.get('event', '')}")
    print(f"Market: {trade.get('market', '')}")
    print(f"Mode: {mode}")
    print(f"Result: {result}")
    print(f"CLV: {clv:.4f}")
    print(f"Profit/Loss: ${profit_loss:.2f}")


if __name__ == "__main__":
    main()