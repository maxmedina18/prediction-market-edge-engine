"""
Settlement utilities for completed prediction-market trades.

Tracks:
- actual profit/loss
- closing line value
"""


from engine.ev import net_profit_if_win


def calculate_clv(entry_price: float, closing_price: float) -> float:
    """
    Closing line value for YES-style contracts.

    Positive CLV means the market moved in your favor.
    """
    if not 0 < entry_price < 1:
        raise ValueError(f"entry_price must be between 0 and 1, got {entry_price}")

    if not 0 < closing_price < 1:
        raise ValueError(f"closing_price must be between 0 and 1, got {closing_price}")

    return closing_price - entry_price


def calculate_profit_loss(
    price: float,
    stake: float,
    result: str,
    fee_rate: float = 0.07,
) -> float:
    """
    Calculate actual P/L.

    result options:
    - win
    - loss
    - push
    """
    if not 0 < price < 1:
        raise ValueError(f"price must be between 0 and 1, got {price}")

    if stake <= 0:
        raise ValueError(f"stake must be positive, got {stake}")

    result = result.lower().strip()

    if result not in {"win", "loss", "push"}:
        raise ValueError("result must be one of: win, loss, push")

    if result == "push":
        return 0.0

    if result == "loss":
        return -stake

    contracts = stake / price
    return contracts * net_profit_if_win(price, fee_rate)