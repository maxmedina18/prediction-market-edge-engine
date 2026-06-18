import pytest

from engine import risk_guard


def test_risk_guard_allows_clean_test_trade():
    allowed, issues = risk_guard.risk_guard_check(
        bankroll=50,
        stake=1,
        confidence="high",
        verdict="SMALL TRADE OK",
        mode="test",
    )

    assert allowed is True
    assert issues == []


def test_risk_guard_blocks_low_confidence():
    allowed, issues = risk_guard.risk_guard_check(
        bankroll=50,
        stake=1,
        confidence="low",
        verdict="SMALL TRADE OK",
        mode="test",
    )

    assert allowed is False
    assert "Confidence is low." in issues


def test_risk_guard_blocks_pass_verdict():
    allowed, issues = risk_guard.risk_guard_check(
        bankroll=50,
        stake=1,
        confidence="high",
        verdict="PASS",
        mode="test",
    )

    assert allowed is False
    assert any("pass" in issue.lower() for issue in issues)


def test_risk_guard_blocks_reduce_verdict():
    allowed, issues = risk_guard.risk_guard_check(
        bankroll=50,
        stake=1,
        confidence="high",
        verdict="REDUCE SIZE",
        mode="test",
    )

    assert allowed is False
    assert any("requires size reduction" in issue.lower() for issue in issues)


def test_risk_guard_blocks_real_trade_above_learning_max(monkeypatch):
    monkeypatch.setattr(risk_guard, "daily_realized_pl", lambda mode="real": 0.0)

    allowed, issues = risk_guard.risk_guard_check(
        bankroll=100,
        stake=2,
        confidence="high",
        verdict="SMALL TRADE OK",
        mode="real",
        max_learning_stake=1.00,
        max_bankroll_fraction=0.02,
    )

    assert allowed is False
    assert any("learning-mode max" in issue for issue in issues)


def test_risk_guard_blocks_real_trade_above_bankroll_cap(monkeypatch):
    monkeypatch.setattr(risk_guard, "daily_realized_pl", lambda mode="real": 0.0)

    allowed, issues = risk_guard.risk_guard_check(
        bankroll=50,
        stake=2,
        confidence="high",
        verdict="SMALL TRADE OK",
        mode="real",
        max_learning_stake=10.00,
        max_bankroll_fraction=0.02,
    )

    assert allowed is False
    assert any("bankroll cap" in issue for issue in issues)


def test_risk_guard_blocks_daily_stop_loss(monkeypatch):
    monkeypatch.setattr(risk_guard, "daily_realized_pl", lambda mode="real": -3.00)

    allowed, issues = risk_guard.risk_guard_check(
        bankroll=50,
        stake=1,
        confidence="high",
        verdict="SMALL TRADE OK",
        mode="real",
        daily_loss_limit=-3.00,
    )

    assert allowed is False
    assert any("Daily loss limit hit" in issue for issue in issues)


def test_risk_guard_allows_clean_real_trade(monkeypatch):
    monkeypatch.setattr(risk_guard, "daily_realized_pl", lambda mode="real": 0.0)

    allowed, issues = risk_guard.risk_guard_check(
        bankroll=50,
        stake=1,
        confidence="high",
        verdict="SMALL TRADE OK",
        mode="real",
        max_learning_stake=1.00,
        max_bankroll_fraction=0.02,
        daily_loss_limit=-3.00,
    )

    assert allowed is True
    assert issues == []


def test_risk_guard_label_allowed():
    assert risk_guard.risk_guard_label(True) == "TRADE ALLOWED"


def test_risk_guard_label_blocked():
    assert risk_guard.risk_guard_label(False) == "TRADE BLOCKED"