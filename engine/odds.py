"""
Odds conversion utilities.

Supports:
- American odds to implied probability
- Decimal odds to implied probability
- Vig removal for 3-way soccer markets
"""


def american_to_implied_probability(odds: int) -> float:
    """
    Convert American odds to implied probability.

    Examples:
    -150 -> 150 / (150 + 100) = 60.00%
    +200 -> 100 / (200 + 100) = 33.33%
    """
    if odds == 0:
        raise ValueError("American odds cannot be zero.")

    if odds < 0:
        return abs(odds) / (abs(odds) + 100)

    return 100 / (odds + 100)


def decimal_to_implied_probability(odds: float) -> float:
    """
    Convert decimal odds to implied probability.

    Example:
    2.00 -> 50%
    1.50 -> 66.67%
    """
    if odds <= 1:
        raise ValueError("Decimal odds must be greater than 1.")

    return 1 / odds


def remove_vig(probabilities: list[float]) -> list[float]:
    """
    Remove sportsbook vig by normalizing probabilities so they sum to 1.

    Example:
    Raw probabilities:
    [0.66, 0.22, 0.17] sum to 1.05

    Fair probabilities:
    each probability / 1.05
    """
    total = sum(probabilities)

    if total <= 0:
        raise ValueError("Probability total must be positive.")

    return [probability / total for probability in probabilities]


def probability_gap(market_probability: float, fair_probability: float) -> float:
    """
    Calculate fair probability minus market probability.

    Positive gap = possible edge.
    """
    return fair_probability - market_probability