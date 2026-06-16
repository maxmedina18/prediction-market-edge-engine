"""
Kelly Criterion position sizing for binary prediction-market contracts.

Important:
- Full Kelly is aggressive.
- This engine defaults to fractional Kelly because bankroll survival matters.
- For learning mode, we cap position size separately in verdict.py.
"""


def validate_probability(value: float, name: str) -> None:
    """Validate that a probability-like value is between 0 and 1."""
    if not 0 < value < 1:
        raise ValueError(f"{name} must be between 0 and 1, got {value}")


def full_kelly_fraction(price: float, probability: float) -> float:
    """
    Calculate full Kelly fraction for a binary contract.

    price = contract cost, e.g. 0.65
    probability = your estimated win probability, e.g. 0.70

    Formula:
    b = net odds received
    q = probability of loss
    Kelly = (b*p - q) / b
    """
    validate_probability(price, "price")
    validate_probability(probability, "probability")

    b = (1.0 - price) / price
    p = probability
    q = 1.0 - probability

    return (b * p - q) / b


def fractional_kelly_fraction(
    price: float,
    probability: float,
    fraction: float = 0.25,
) -> float:
    """
    Calculate fractional Kelly.

    Example:
    Full Kelly = 0.14
    0.25 Kelly = 0.035
    """
    if not 0 < fraction <= 1:
        raise ValueError(f"fraction must be between 0 and 1, got {fraction}")

    full_kelly = full_kelly_fraction(price, probability)

    return max(0.0, full_kelly * fraction)


def suggested_kelly_stake(
    bankroll: float,
    price: float,
    probability: float,
    fraction: float = 0.25,
) -> float:
    """
    Convert fractional Kelly percentage into dollar stake.
    """
    if bankroll <= 0:
        raise ValueError(f"bankroll must be positive, got {bankroll}")

    return bankroll * fractional_kelly_fraction(price, probability, fraction)


def beginner_capped_stake(
    bankroll: float,
    price: float,
    probability: float,
    fraction: float = 0.25,
    max_bankroll_fraction: float = 0.02,
) -> float:
    """
    Suggest a stake using fractional Kelly, capped by beginner bankroll rules.

    Example:
    Bankroll = 50
    Max bankroll fraction = 0.02
    Max beginner stake = 1 dollar
    """
    if not 0 < max_bankroll_fraction <= 1:
        raise ValueError(
            f"max_bankroll_fraction must be between 0 and 1, got {max_bankroll_fraction}"
        )

    kelly_stake = suggested_kelly_stake(bankroll, price, probability, fraction)
    cap = bankroll * max_bankroll_fraction

    return min(kelly_stake, cap)