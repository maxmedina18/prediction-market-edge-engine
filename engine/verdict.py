"""
Trade verdict logic.

This module turns raw EV and sizing math into a decision:
- PASS
- REDUCE SIZE
- SMALL TRADE OK
- INVESTIGATE FURTHER
"""

from engine.ev import ev_per_contract
from engine.kelly import beginner_capped_stake


def get_trade_verdict(
    bankroll: float,
    price: float,
    probability: float,
    stake: float,
    fee_rate: float = 0.07,
    min_edge: float = 0.05,
    max_bankroll_fraction: float = 0.02,
    confidence: str = "low",
) -> str:
    """
    Return a plain-English trade verdict.

    confidence options:
    - low
    - medium
    - high
    """
    if bankroll <= 0:
        raise ValueError(f"bankroll must be positive, got {bankroll}")

    if stake <= 0:
        raise ValueError(f"stake must be positive, got {stake}")

    confidence = confidence.lower().strip()

    if confidence not in {"low", "medium", "high"}:
        raise ValueError("confidence must be one of: low, medium, high")

    edge = probability - price
    ev = ev_per_contract(price, probability, fee_rate)
    max_stake = bankroll * max_bankroll_fraction
    capped_kelly_stake = beginner_capped_stake(
        bankroll=bankroll,
        price=price,
        probability=probability,
        max_bankroll_fraction=max_bankroll_fraction,
    )

    if confidence == "low":
        return "INVESTIGATE FURTHER - probability estimate confidence is low"

    if edge < min_edge:
        return "PASS - edge is too small"

    if ev <= 0:
        return "PASS - negative post-fee EV"

    if stake > max_stake:
        return f"REDUCE SIZE - stake exceeds beginner cap of ${max_stake:.2f}"

    if stake > capped_kelly_stake:
        return f"REDUCE SIZE - stake exceeds capped Kelly suggestion of ${capped_kelly_stake:.2f}"

    return "SMALL TRADE OK"