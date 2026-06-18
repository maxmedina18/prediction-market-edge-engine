import pytest

from engine.kelly import (
    full_kelly_fraction,
    fractional_kelly_fraction,
    suggested_kelly_stake,
    beginner_capped_stake,
)


def test_full_kelly_positive_edge():
    result = full_kelly_fraction(price=0.65, probability=0.71)

    b = (1 - 0.65) / 0.65
    p = 0.71
    q = 1 - p
    expected = (b * p - q) / b

    assert result == pytest.approx(expected)
    assert result > 0


def test_full_kelly_negative_edge():
    result = full_kelly_fraction(price=0.65, probability=0.55)

    assert result < 0


def test_fractional_kelly_clips_negative_to_zero():
    result = fractional_kelly_fraction(
        price=0.65,
        probability=0.55,
        fraction=0.25,
    )

    assert result == pytest.approx(0.0)


def test_fractional_kelly_positive_edge():
    full = full_kelly_fraction(price=0.65, probability=0.71)
    result = fractional_kelly_fraction(
        price=0.65,
        probability=0.71,
        fraction=0.25,
    )

    assert result == pytest.approx(full * 0.25)


def test_suggested_kelly_stake():
    result = suggested_kelly_stake(
        bankroll=50,
        price=0.65,
        probability=0.71,
        fraction=0.25,
    )

    expected_fraction = fractional_kelly_fraction(
        price=0.65,
        probability=0.71,
        fraction=0.25,
    )

    assert result == pytest.approx(50 * expected_fraction)


def test_beginner_capped_stake_caps_at_bankroll_fraction():
    result = beginner_capped_stake(
        bankroll=50,
        price=0.65,
        probability=0.71,
        fraction=0.25,
        max_bankroll_fraction=0.02,
    )

    assert result <= 1.00
    assert result == pytest.approx(1.00)


def test_beginner_capped_stake_returns_lower_kelly_when_below_cap():
    result = beginner_capped_stake(
        bankroll=50,
        price=0.65,
        probability=0.66,
        fraction=0.25,
        max_bankroll_fraction=0.02,
    )

    assert result <= 1.00


@pytest.mark.parametrize("bad_bankroll", [0, -50])
def test_invalid_bankroll_rejected(bad_bankroll):
    with pytest.raises(ValueError):
        suggested_kelly_stake(
            bankroll=bad_bankroll,
            price=0.65,
            probability=0.71,
        )


@pytest.mark.parametrize("bad_fraction", [0, -0.25, 1.1])
def test_invalid_fraction_rejected(bad_fraction):
    with pytest.raises(ValueError):
        fractional_kelly_fraction(
            price=0.65,
            probability=0.71,
            fraction=bad_fraction,
        )