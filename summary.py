"""
Trade summary dashboard.

Reads data/trades.csv and reports:
- total trades
- settled/open trades
- win/loss/push counts
- win rate
- total P/L
- average CLV
- average EV
- average ROI
- best trade
- worst trade

Supports trade modes:
- real
- paper
- test
- all
"""

import csv
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


def main() -> None:
    print("\n=== EDGE ENGINE SUMMARY ===")

    all_trades = read_trades()

    if not all_trades:
        print("No trades found in data/trades.csv.")
        return

    mode_filter = ask_mode_filter()
    trades = filter_by_mode(all_trades, mode_filter)

    if not trades:
        print(f"No trades found for mode: {mode_filter}")
        return

    settled_trades = [
        trade
        for trade in trades
        if trade.get("result", "").strip().lower() in {"win", "loss", "push"}
    ]

    open_trades = [
        trade
        for trade in trades
        if trade.get("result", "").strip() == ""
    ]

    wins = [
        trade
        for trade in settled_trades
        if trade.get("result", "").strip().lower() == "win"
    ]

    losses = [
        trade
        for trade in settled_trades
        if trade.get("result", "").strip().lower() == "loss"
    ]

    pushes = [
        trade
        for trade in settled_trades
        if trade.get("result", "").strip().lower() == "push"
    ]

    win_rate = 0.0

    if wins or losses:
        win_rate = len(wins) / (len(wins) + len(losses))

    profit_losses = [
        safe_float(trade.get("profit_loss", ""))
        for trade in settled_trades
    ]
    profit_losses = [value for value in profit_losses if value is not None]

    clvs = [
        safe_float(trade.get("clv", ""))
        for trade in settled_trades
    ]
    clvs = [value for value in clvs if value is not None]

    evs = [
        safe_float(trade.get("ev_per_contract", ""))
        for trade in trades
    ]
    evs = [value for value in evs if value is not None]

    rois = [
        safe_float(trade.get("roi", ""))
        for trade in trades
    ]
    rois = [value for value in rois if value is not None]

    total_pl = sum(profit_losses)
    avg_clv = average(clvs)
    avg_ev = average(evs)
    avg_roi = average(rois)

    settled_with_pl = [
        trade
        for trade in settled_trades
        if safe_float(trade.get("profit_loss", "")) is not None
    ]

    best_trade = None
    worst_trade = None

    if settled_with_pl:
        best_trade = max(
            settled_with_pl,
            key=lambda trade: safe_float(trade.get("profit_loss", "")) or 0.0,
        )

        worst_trade = min(
            settled_with_pl,
            key=lambda trade: safe_float(trade.get("profit_loss", "")) or 0.0,
        )

    print(f"\nMode: {mode_filter}")
    print(f"Total trades: {len(trades)}")
    print(f"Settled trades: {len(settled_trades)}")
    print(f"Open trades: {len(open_trades)}")
    print(f"Wins: {len(wins)}")
    print(f"Losses: {len(losses)}")
    print(f"Pushes: {len(pushes)}")
    print(f"Win rate: {pct(win_rate)}")
    print(f"Total P/L: {money(total_pl)}")
    print(f"Average CLV: {avg_clv:.4f}")
    print(f"Average EV per contract: {money(avg_ev)}")
    print(f"Average ROI: {pct(avg_roi)}")

    if best_trade:
        print("\n=== BEST TRADE ===")
        print(f"Event: {best_trade.get('event', '')}")
        print(f"Market: {best_trade.get('market', '')}")
        print(f"P/L: {money(safe_float(best_trade.get('profit_loss', '')) or 0.0)}")

    if worst_trade:
        print("\n=== WORST TRADE ===")
        print(f"Event: {worst_trade.get('event', '')}")
        print(f"Market: {worst_trade.get('market', '')}")
        print(f"P/L: {money(safe_float(worst_trade.get('profit_loss', '')) or 0.0)}")

    print("\n=== COACH READ ===")

    if len(settled_trades) == 0:
        print("No settled trades yet. Settle trades before judging performance.")
    elif len(settled_trades) < 20:
        print("Sample size is tiny. Focus on process, sizing, and CLV, not ego.")
    elif total_pl < 0:
        print("You are negative. Reduce size and check whether losses are from bad picks or bad sizing.")
    else:
        print("Positive P/L. Keep sizing controlled and keep tracking CLV.")


if __name__ == "__main__":
    main()