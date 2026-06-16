"""
Summary dashboard for Edge Engine.

Reads data/trades.csv and reports:
- total trades
- settled trades
- open trades
- win rate
- total P/L
- average CLV
- average EV
- average ROI
"""

import csv
from pathlib import Path


TRADE_LOG_PATH = Path("data/trades.csv")


def safe_float(value: str) -> float | None:
    """
    Convert string to float safely.

    Empty strings become None.
    """
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
    """
    Read trades from CSV.
    """
    if not path.exists():
        raise FileNotFoundError(f"No trade log found at {path}")

    with path.open("r", newline="") as file:
        return list(csv.DictReader(file))


def money(value: float) -> str:
    return f"${value:.2f}"


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def average(values: list[float]) -> float:
    if not values:
        return 0.0

    return sum(values) / len(values)


def main() -> None:
    trades = read_trades()

    total_trades = len(trades)

    settled_trades = [
        trade for trade in trades
        if trade.get("result", "").strip().lower() in {"win", "loss", "push"}
    ]

    open_trades = [
        trade for trade in trades
        if trade.get("result", "").strip() == ""
    ]

    wins = [
        trade for trade in settled_trades
        if trade.get("result", "").strip().lower() == "win"
    ]

    losses = [
        trade for trade in settled_trades
        if trade.get("result", "").strip().lower() == "loss"
    ]

    pushes = [
        trade for trade in settled_trades
        if trade.get("result", "").strip().lower() == "push"
    ]

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
    win_rate = len(wins) / len(settled_trades) if settled_trades else 0.0

    avg_clv = average(clvs)
    avg_ev = average(evs)
    avg_roi = average(rois)

    best_trade = None
    worst_trade = None

    if settled_trades:
        settled_with_pl = [
            trade for trade in settled_trades
            if safe_float(trade.get("profit_loss", "")) is not None
        ]

        if settled_with_pl:
            best_trade = max(
                settled_with_pl,
                key=lambda trade: safe_float(trade.get("profit_loss", "")) or 0.0
            )
            worst_trade = min(
                settled_with_pl,
                key=lambda trade: safe_float(trade.get("profit_loss", "")) or 0.0
            )

    print("\n=== EDGE ENGINE SUMMARY ===")
    print(f"Total trades: {total_trades}")
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

    if len(settled_trades) < 20:
        print("Sample size is tiny. Do not draw strong conclusions yet.")
    elif avg_clv > 0 and total_pl > 0:
        print("Strong signal: positive P/L and positive CLV.")
    elif avg_clv > 0 and total_pl <= 0:
        print("Potentially good process, bad variance. Keep tracking.")
    elif avg_clv <= 0 and total_pl > 0:
        print("Warning: profitable so far, but CLV is weak. Could be luck.")
    else:
        print("Bad signal: losing money and not beating close. Tighten process.")


if __name__ == "__main__":
    main()