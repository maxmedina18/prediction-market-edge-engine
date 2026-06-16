"""
Probability Estimator V0.

This script helps estimate fair probability by comparing:
- Kalshi contract price
- Sportsbook 3-way soccer market odds

For soccer:
- Team A win
- Draw
- Team B win

The script removes sportsbook vig and compares fair probability to Kalshi.
"""
from engine.odds import (
    american_to_implied_probability,
    decimal_to_implied_probability,
    remove_vig,
    probability_gap,
)


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def ask_float(prompt: str) -> float:
    while True:
        raw = input(prompt).strip()

        try:
            return float(raw)
        except ValueError:
            print("Please enter a valid number.")


def ask_odds_format() -> str:
    while True:
        odds_format = input("Odds format [american/decimal]: ").strip().lower()

        if odds_format in {"american", "decimal"}:
            return odds_format

        print("Please enter american or decimal.")


def convert_odds_to_probability(odds: float, odds_format: str) -> float:
    if odds_format == "american":
        return american_to_implied_probability(int(odds))

    return decimal_to_implied_probability(odds)


def main() -> None:
    print("\n=== PROBABILITY ESTIMATOR V0 ===")
    print("Use this for soccer 3-way markets: Team A / Draw / Team B")
    print("--------------------------------\n")

    kalshi_price = ask_float("Kalshi price for Team A win, decimal like 0.65: ")
    odds_format = ask_odds_format()

    team_a_odds = ask_float("Sportsbook odds for Team A win: ")
    draw_odds = ask_float("Sportsbook odds for Draw: ")
    team_b_odds = ask_float("Sportsbook odds for Team B win: ")

    raw_team_a = convert_odds_to_probability(team_a_odds, odds_format)
    raw_draw = convert_odds_to_probability(draw_odds, odds_format)
    raw_team_b = convert_odds_to_probability(team_b_odds, odds_format)

    raw_probs = [raw_team_a, raw_draw, raw_team_b]
    fair_team_a, fair_draw, fair_team_b = remove_vig(raw_probs)

    gap = probability_gap(kalshi_price, fair_team_a)

    print("\n=== SPORTSBOOK RAW IMPLIED PROBABILITIES ===")
    print(f"Team A raw implied: {pct(raw_team_a)}")
    print(f"Draw raw implied: {pct(raw_draw)}")
    print(f"Team B raw implied: {pct(raw_team_b)}")
    print(f"Raw total with vig: {pct(sum(raw_probs))}")

    print("\n=== NO-VIG FAIR PROBABILITIES ===")
    print(f"Team A fair probability: {pct(fair_team_a)}")
    print(f"Draw fair probability: {pct(fair_draw)}")
    print(f"Team B fair probability: {pct(fair_team_b)}")
    print(f"No-vig total: {pct(fair_team_a + fair_draw + fair_team_b)}")

    print("\n=== KALSHI COMPARISON ===")
    print(f"Kalshi Team A price: {pct(kalshi_price)}")
    print(f"Sportsbook no-vig Team A probability: {pct(fair_team_a)}")
    print(f"Discrepancy: {pct(gap)}")

    print("\n=== ESTIMATED PROBABILITY ===")
    print(f"Suggested estimate: {pct(fair_team_a)}")

    print("\n=== COACH READ ===")

    if gap >= 0.05:
        print("Interesting: sportsbook no-vig probability is at least 5 points above Kalshi.")
        print("This may be worth running through main.py for EV and sizing.")
    elif gap > 0:
        print("Small possible edge, but below our 5-point threshold. Be careful.")
    elif gap == 0:
        print("No discrepancy. Market agrees almost exactly.")
    else:
        print("Pass signal: Kalshi is pricing Team A higher than sportsbook fair value.")


if __name__ == "__main__":
    main()