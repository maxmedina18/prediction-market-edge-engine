import pytest

from engine.ev import (
    implied_probability,
    gross_profit_if_win,
    net_profit_if_win,
    ev_per_contract,
    expected_profit_on_stake,
    expected_roi,
)


def test_implied_probability_equals_price():
    assert implied_probability(0.65) == pytest.approx(0.65)


def test_gross_profit_if_win():
    assert gross_profit_if_win(0.65) == pytest.approx(0.35)


def test_net_profit_if_win_after_fee():
    assert net_profit_if_win(0.65, fee_rate=0.05) == pytest.approx(0.35 * 0.95)


def test_ev_per_contract_positive_edge():
    result = ev_per_contract(price=0.65, probability=0.71, fee_rate=0.05)

    expected = 0.71 * ((1 - 0.65) * 0.95) - 0.29 * 0.65

    assert result == pytest.approx(expected)


def test_ev_per_contract_negative_edge():
    result = ev_per_contract(price=0.65, probability=0.55, fee_rate=0.05)

    assert result < 0


def test_expected_profit_on_stake():
    result = expected_profit_on_stake(
        price=0.65,
        probability=0.71,
        stake=1.00,
        fee_rate=0.05,
    )

    ev = ev_per_contract(price=0.65, probability=0.71, fee_rate=0.05)
    expected = (1.00 / 0.65) * ev

    assert result == pytest.approx(expected)


def test_expected_roi():
    result = expected_roi(price=0.65, probability=0.71, fee_rate=0.05)

    ev = ev_per_contract(price=0.65, probability=0.71, fee_rate=0.05)
    expected = ev / 0.65

    assert result == pytest.approx(expected)


@pytest.mark.parametrize("bad_price", [0, 1, -0.1, 1.1])
def test_invalid_price_rejected(bad_price):
    with pytest.raises(ValueError):
        implied_probability(bad_price)


@pytest.mark.parametrize("bad_probability", [0, 1, -0.1, 1.1])
def test_invalid_probability_rejected(bad_probability):
    with pytest.raises(ValueError):
        ev_per_contract(price=0.65, probability=bad_probability)


@pytest.mark.parametrize("bad_stake", [0, -1])
def test_invalid_stake_rejected(bad_stake):
    with pytest.raises(ValueError):
        expected_profit_on_stake(
            price=0.65,
            probability=0.71,
            stake=bad_stake,
        )