"""
Market Check CLI.

Use this before trusting a Kalshi vs sportsbook discrepancy.

This helps catch fake edges caused by mismatched markets.
"""

from engine.market_check import (
    validate_market_comparison,
    market_check_verdict,
    yes_no_to_bool,
)


def ask_yes_no(prompt: str) -> bool:
    while True:
        raw = input(prompt).strip().lower()

        try:
            return yes_no_to_bool(raw)
        except ValueError:
            print("Please enter y or n.")


def ask_choice(prompt: str, choices: set[str]) -> str:
    choices_display = "/".join(sorted(choices))

    while True:
        raw = input(f"{prompt} [{choices_display}]: ").strip().lower()

        if raw in choices:
            return raw

        print(f"Please enter one of: {choices_display}")


def main() -> None:
    print("\n=== MARKET CHECK ===")
    print("Use this before trusting a sportsbook-vs-Kalshi discrepancy.")
    print("--------------------------------\n")

    same_event = ask_yes_no("Same exact event/matchup? [y/n]: ")
    same_outcome = ask_yes_no("Same exact outcome? [y/n]: ")

    kalshi_timing = ask_choice(
        "Kalshi timing",
        {"pregame", "live"},
    )

    sportsbook_timing = ask_choice(
        "Sportsbook timing",
        {"pregame", "live"},
    )

    kalshi_period = ask_choice(
        "Kalshi period",
        {"full_match", "first_half", "second_half"},
    )

    sportsbook_period = ask_choice(
        "Sportsbook period",
        {"full_match", "first_half", "second_half"},
    )

    kalshi_settlement = ask_choice(
        "Kalshi settlement",
        {"regulation_only", "includes_extra_time", "unknown"},
    )

    sportsbook_settlement = ask_choice(
        "Sportsbook settlement",
        {"regulation_only", "includes_extra_time", "unknown"},
    )

    liquidity_ok = ask_yes_no("Kalshi liquidity acceptable? [y/n]: ")
    spread_ok = ask_yes_no("Kalshi spread acceptable? [y/n]: ")

    is_valid, issues = validate_market_comparison(
        same_event=same_event,
        same_outcome=same_outcome,
        kalshi_timing=kalshi_timing,
        sportsbook_timing=sportsbook_timing,
        kalshi_period=kalshi_period,
        sportsbook_period=sportsbook_period,
        kalshi_settlement=kalshi_settlement,
        sportsbook_settlement=sportsbook_settlement,
        liquidity_ok=liquidity_ok,
        spread_ok=spread_ok,
    )

    verdict = market_check_verdict(is_valid, issues)

    print("\n=== MARKET CHECK RESULT ===")
    print(f"Verdict: {verdict}")

    if issues:
        print("\nIssues:")
        for issue in issues:
            print(f"- {issue}")

    print("\n=== COACH READ ===")

    if is_valid:
        print("Good. You can use the discrepancy as a cleaner probability signal.")
    else:
        print("Do not trade from this discrepancy yet. Fix the mismatch first.")


if __name__ == "__main__":
    main()