import pytest

from engine.settlement import calculate_clv, calculate_profit_loss


def test_calculate_clv_positive():
    assert calculate_clv(entry_price=0.65, closing_price=0.70) == pytest.approx(0.05)


def test_calculate_clv_negative():
    assert calculate_clv(entry_price=0.70, closing_price=0.65) == pytest.approx(-0.05)


def test_profit_loss_win():
    result = calculate_profit_loss(
        price=0.65,
        stake=1.00,
        result="win",
        fee_rate=0.05,
    )

    # If you stake $1 at 65c, contracts = 1 / 0.65.
    # Gross payout = contracts * $1.
    # Profit before fee = gross payout - stake.
    expected_contracts = 1.00 / 0.65
    expected_profit_before_fee = expected_contracts - 1.00
    expected_fee = expected_profit_before_fee * 0.05
    expected_profit = expected_profit_before_fee - expected_fee

    assert result == pytest.approx(expected_profit)


def test_profit_loss_loss():
    result = calculate_profit_loss(
        price=0.65,
        stake=1.00,
        result="loss",
        fee_rate=0.05,
    )

    assert result == pytest.approx(-1.00)


def test_profit_loss_push():
    result = calculate_profit_loss(
        price=0.65,
        stake=1.00,
        result="push",
        fee_rate=0.05,
    )

    assert result == pytest.approx(0.00)