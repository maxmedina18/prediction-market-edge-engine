"""
Edge Engine V0

Command-line tool for analyzing binary prediction-market trades.

This version uses calibrated probability:
- raw_probability = your original estimate
- calibrated_prob = adjusted estimate based on your historical calibration

Early on, calibrated_prob will equal raw_probability because there is not enough
settled trade data yet. Later, once you have enough trades, the engine can
self-correct overconfidence.
"""

from engine.calibration import calibrated_probability
from engine.ev import (
    implied_probability,
    ev_per_contract,
    expected_profit_on_stake,
    expected_roi,
)
from engine.kelly import (
    full_kelly_fraction,
    fractional_kelly_fraction,
    suggested_kelly_stake,
    beginner_capped_stake,
)
from engine.logger import log_trade, today_string
from engine.verdict import get_trade_verdict


def pct(value: float) -> str:
    """Format decimal as percentage."""
    return f"{value * 100:.2f}%"


def money(value: float) -> str:
    """Format number as dollars."""
    return f"${value:.2f}"


def ask_float(prompt: str, default: float | None = None) -> float:
    """
    Ask user for a float input.

    If default is provided, pressing enter returns default.
    """
    while True:
        raw = input(prompt).strip()

        if raw == "" and default is not None:
            return default

        try:
            return float(raw)
        except ValueError:
            print("Please enter a valid number.")


def ask_confidence() -> str:
    """Ask user for confidence level."""
    while True:
        confidence = input("Confidence level [low/medium/high]: ").strip().lower()

        if confidence in {"low", "medium", "high"}:
            return confidence

        print("Please enter low, medium, or high.")


def main() -> None:
    print("\n=== KALSHI EDGE ENGINE V0 ===")
    print("Use decimals: 65c = 0.65, 70% = 0.70")
    print("--------------------------------\n")

    bankroll = ask_float("Bankroll: ")
    price = ask_float("Contract price: ")
    probability = ask_float("Your estimated probability: ")
    stake = ask_float("Stake: ")
    fee_rate = ask_float("Fee rate [default 0.07]: ", default=0.07)
    confidence = ask_confidence()

    implied = implied_probability(price)

    raw_probability = probability
    calibrated_prob = calibrated_probability(raw_probability)

    edge = calibrated_prob - implied

    ev = ev_per_contract(price, calibrated_prob, fee_rate)
    expected_profit = expected_profit_on_stake(
        price,
        calibrated_prob,
        stake,
        fee_rate,
    )
    roi = expected_roi(price, calibrated_prob, fee_rate)

    full_kelly = full_kelly_fraction(price, calibrated_prob)
    quarter_kelly = fractional_kelly_fraction(
        price,
        calibrated_prob,
        fraction=0.25,
    )
    quarter_kelly_stake = suggested_kelly_stake(
        bankroll,
        price,
        calibrated_prob,
        fraction=0.25,
    )
    capped_stake = beginner_capped_stake(
        bankroll,
        price,
        calibrated_prob,
    )

    verdict = get_trade_verdict(
        bankroll=bankroll,
        price=price,
        probability=calibrated_prob,
        stake=stake,
        fee_rate=fee_rate,
        confidence=confidence,
    )

    print("\n=== TRADE ANALYSIS ===")
    print(f"Market implied probability: {pct(implied)}")
    print(f"Raw estimated probability: {pct(raw_probability)}")
    print(f"Calibrated probability: {pct(calibrated_prob)}")
    print(f"Edge using calibrated probability: {pct(edge)}")
    print(f"EV per contract: {money(ev)}")
    print(f"Expected profit on stake: {money(expected_profit)}")
    print(f"Expected ROI: {pct(roi)}")
    print(f"Full Kelly: {pct(full_kelly)}")
    print(f"0.25 Kelly: {pct(quarter_kelly)}")
    print(f"0.25 Kelly stake: {money(quarter_kelly_stake)}")
    print(f"Beginner capped stake: {money(capped_stake)}")
    print(f"Verdict: {verdict}")

    print("\n=== COACH NOTE ===")

    if confidence == "low":
        print("Your estimate is low-confidence. Treat this as research, not a real edge.")
    elif verdict.startswith("REDUCE"):
        print("The idea may be okay, but your size is the problem.")
    elif verdict.startswith("PASS"):
        print("Do not force it. Passing is a profitable skill.")
    else:
        print("Small trade only. Log it, track CLV, and judge the process later.")

    should_log = input("\nLog this trade? [y/n]: ").strip().lower()

    if should_log == "y":
        sport = input("Sport: ").strip()
        event = input("Event: ").strip()
        market = input("Market: ").strip()
        notes = input("Notes: ").strip()

        log_trade(
            {
                "date": today_string(),
                "sport": sport,
                "event": event,
                "market": market,
                "price": price,
                "estimated_probability": raw_probability,
                "stake": stake,
                "bankroll": bankroll,
                "fee_rate": fee_rate,
                "confidence": confidence,
                "edge": edge,
                "ev_per_contract": ev,
                "expected_profit": expected_profit,
                "roi": roi,
                "full_kelly": full_kelly,
                "quarter_kelly": quarter_kelly,
                "beginner_capped_stake": capped_stake,
                "verdict": verdict,
                "result": "",
                "closing_price": "",
                "clv": "",
                "profit_loss": "",
                "notes": notes,
            }
        )

        print("Trade logged to data/trades.csv.")


if __name__ == "__main__":
    main()