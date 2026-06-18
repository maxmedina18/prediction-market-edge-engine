import pytest

from engine.odds import (
    american_to_implied_probability,
    decimal_to_implied_probability,
    remove_vig,
    probability_gap,
)


def test_american_negative_odds_to_implied_probability():
    assert american_to_implied_probability(-150) == pytest.approx(150 / 250)


def test_american_positive_odds_to_implied_probability():
    assert american_to_implied_probability(200) == pytest.approx(100 / 300)


def test_american_zero_odds_rejected():
    with pytest.raises(ValueError):
        american_to_implied_probability(0)


def test_decimal_odds_to_implied_probability():
    assert decimal_to_implied_probability(2.00) == pytest.approx(0.50)
    assert decimal_to_implied_probability(1.50) == pytest.approx(1 / 1.50)


@pytest.mark.parametrize("bad_decimal", [1.0, 0.99, 0, -2])
def test_invalid_decimal_odds_rejected(bad_decimal):
    with pytest.raises(ValueError):
        decimal_to_implied_probability(bad_decimal)


def test_remove_vig_normalizes_probabilities_to_one():
    raw = [0.66, 0.22, 0.17]
    fair = remove_vig(raw)

    assert sum(fair) == pytest.approx(1.0)


def test_remove_vig_preserves_order():
    raw = [0.66, 0.22, 0.17]
    fair = remove_vig(raw)

    assert fair[0] > fair[1] > fair[2]


def test_remove_vig_rejects_zero_total():
    with pytest.raises(ValueError):
        remove_vig([0, 0, 0])


def test_probability_gap_positive_edge():
    assert probability_gap(0.65, 0.71) == pytest.approx(0.06)


def test_probability_gap_negative_edge():
    assert probability_gap(0.71, 0.65) == pytest.approx(-0.06)