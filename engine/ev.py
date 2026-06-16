"""
Expected value calculations for binary prediction-market contracts.

Assumptions:
- Contract price is expressed as a decimal: 65c = 0.65
- Contract pays $1.00 if it wins
- If the contract loses, the full cost is lost
- Fee is applied to winnings/profit, not to total payout
"""


def validate_probability(value: float, name: str) -> None:
    """Validate that a probability-like value is between 0 and 1."""
    if not 0 < value < 1:
        raise ValueError(f"{name} must be between 0 and 1, got {value}")


def implied_probability(price: float) -> float:
    """
    Convert contract price into market-implied probability.

    Example:
    0.65 price -> 65% implied probability
    """
    validate_probability(price, "price")
    return price


def gross_profit_if_win(price: float) -> float:
    """
    Calculate gross profit per contract if it wins.

    Example:
    Buy at 0.65, receive 1.00 if correct.
    Gross profit = 1.00 - 0.65 = 0.35
    """
    validate_probability(price, "price")
    return 1.0 - price


def net_profit_if_win(price: float, fee_rate: float = 0.07) -> float:
    """
    Calculate net profit per winning contract after fees.

    Example:
    Gross profit = 0.35
    Fee rate = 0.07
    Net profit = 0.35 * 0.93
    """
    validate_probability(price, "price")

    if not 0 <= fee_rate < 1:
        raise ValueError(f"fee_rate must be between 0 and 1, got {fee_rate}")

    return gross_profit_if_win(price) * (1.0 - fee_rate)


def ev_per_contract(price: float, probability: float, fee_rate: float = 0.07) -> float:
    """
    Calculate expected value per contract.

    EV = P(win) * net_profit_if_win - P(loss) * cost
    """
    validate_probability(price, "price")
    validate_probability(probability, "probability")

    win_profit = net_profit_if_win(price, fee_rate)
    loss = price

    return probability * win_profit - (1.0 - probability) * loss


def expected_profit_on_stake(
    price: float,
    probability: float,
    stake: float,
    fee_rate: float = 0.07,
) -> float:
    """
    Calculate expected profit for a given stake.

    Number of contracts = stake / price
    Expected profit = contracts * EV per contract
    """
    if stake <= 0:
        raise ValueError(f"stake must be positive, got {stake}")

    contracts = stake / price
    return contracts * ev_per_contract(price, probability, fee_rate)


def expected_roi(price: float, probability: float, fee_rate: float = 0.07) -> float:
    """
    Calculate expected return on risk.

    ROI = EV per contract / contract cost
    """
    return ev_per_contract(price, probability, fee_rate) / price