"""
Market validation utilities.

This module helps prevent fake edges caused by comparing mismatched markets.

Common mistakes:
- Comparing live odds to pregame odds
- Comparing full-match odds to first-half odds
- Comparing regulation-only markets to extra-time-inclusive markets
- Comparing different teams/outcomes
- Ignoring liquidity/spread
"""


VALID_TIMINGS = {"pregame", "live"}
VALID_PERIODS = {"full_match", "first_half", "second_half"}
VALID_SETTLEMENTS = {"regulation_only", "includes_extra_time", "unknown"}


def normalize_answer(answer: str) -> str:
    return answer.strip().lower()


def yes_no_to_bool(answer: str) -> bool:
    answer = normalize_answer(answer)

    if answer in {"y", "yes"}:
        return True

    if answer in {"n", "no"}:
        return False

    raise ValueError("Answer must be yes or no.")


def validate_market_comparison(
    same_event: bool,
    same_outcome: bool,
    kalshi_timing: str,
    sportsbook_timing: str,
    kalshi_period: str,
    sportsbook_period: str,
    kalshi_settlement: str,
    sportsbook_settlement: str,
    liquidity_ok: bool,
    spread_ok: bool,
) -> tuple[bool, list[str]]:
    """
    Validate whether Kalshi and sportsbook odds are comparable.

    Returns:
    - is_valid: bool
    - issues: list of reasons comparison may be invalid
    """
    issues = []

    kalshi_timing = normalize_answer(kalshi_timing)
    sportsbook_timing = normalize_answer(sportsbook_timing)
    kalshi_period = normalize_answer(kalshi_period)
    sportsbook_period = normalize_answer(sportsbook_period)
    kalshi_settlement = normalize_answer(kalshi_settlement)
    sportsbook_settlement = normalize_answer(sportsbook_settlement)

    if kalshi_timing not in VALID_TIMINGS:
        issues.append(f"Invalid Kalshi timing: {kalshi_timing}")

    if sportsbook_timing not in VALID_TIMINGS:
        issues.append(f"Invalid sportsbook timing: {sportsbook_timing}")

    if kalshi_period not in VALID_PERIODS:
        issues.append(f"Invalid Kalshi period: {kalshi_period}")

    if sportsbook_period not in VALID_PERIODS:
        issues.append(f"Invalid sportsbook period: {sportsbook_period}")

    if kalshi_settlement not in VALID_SETTLEMENTS:
        issues.append(f"Invalid Kalshi settlement: {kalshi_settlement}")

    if sportsbook_settlement not in VALID_SETTLEMENTS:
        issues.append(f"Invalid sportsbook settlement: {sportsbook_settlement}")

    if not same_event:
        issues.append("Different event or matchup.")

    if not same_outcome:
        issues.append("Different outcome being compared.")

    if kalshi_timing != sportsbook_timing:
        issues.append("Timing mismatch: pregame vs live.")

    if kalshi_period != sportsbook_period:
        issues.append("Period mismatch: full match vs half/other period.")

    if kalshi_settlement != sportsbook_settlement:
        issues.append("Settlement mismatch: regulation-only vs extra-time/unknown.")

    if not liquidity_ok:
        issues.append("Liquidity is not acceptable.")

    if not spread_ok:
        issues.append("Spread is not acceptable.")

    return len(issues) == 0, issues


def market_check_verdict(is_valid: bool, issues: list[str]) -> str:
    if is_valid:
        return "VALID COMPARISON"

    return "INVALID COMPARISON - do not trust this edge"