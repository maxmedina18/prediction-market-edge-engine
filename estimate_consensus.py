"""
Consensus Probability Estimator V0.

This script estimates fair probability by comparing:
- Kalshi contract price
- Multiple sportsbook 3-way soccer odds

For soccer 3-way markets:
- Team A win
- Draw
- Team B win

For each sportsbook:
1. Convert odds to raw implied probability
2. Remove vig
3. Store no-vig fair probabilities

Then:
1. Average all sportsbook no-vig probabilities
2. Compare consensus probability to Kalshi price
3. Output discrepancy and coach read
"""

from dataclasses import dataclass

from engine.odds import (
    american_to_implied_probability,
    decimal_to_implied_probability,
    remove_vig,
    probability_gap,
)


@dataclass
class BookEstimate:
    book_name: str
    team_a_fair: float
    draw_fair: float
    team_b_fair: float
    raw_total_with_vig: float


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def ask_float(prompt: str) -> float:
    while True:
        raw = input(prompt).strip()

        try:
            return float(raw)
        except ValueError:
            print("Please enter a valid number.")


def ask_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()

        try:
            value = int(raw)

            if value > 0:
                return value

            print("Please enter a positive integer.")
        except ValueError:
            print("Please enter a valid integer.")


def ask_probability(prompt: str) -> float:
    """
    Ask for a probability decimal between 0 and 1.

    Example:
    48c = 0.48
    65c = 0.65
    """
    while True:
        value = ask_float(prompt)

        if 0 < value < 1:
            return value

        print("Please enter a decimal between 0 and 1.")
        print("Example: 48c = 0.48, 65c = 0.65")


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


def average(values: list[float]) -> float:
    if not values:
        return 0.0

    return sum(values) / len(values)


def estimate_book(
    book_name: str,
    odds_format: str,
    team_a_odds: float,
    draw_odds: float,
    team_b_odds: float,
) -> BookEstimate:
    raw_team_a = convert_odds_to_probability(team_a_odds, odds_format)
    raw_draw = convert_odds_to_probability(draw_odds, odds_format)
    raw_team_b = convert_odds_to_probability(team_b_odds, odds_format)

    raw_probs = [raw_team_a, raw_draw, raw_team_b]
    fair_team_a, fair_draw, fair_team_b = remove_vig(raw_probs)

    return BookEstimate(
        book_name=book_name,
        team_a_fair=fair_team_a,
        draw_fair=fair_draw,
        team_b_fair=fair_team_b,
        raw_total_with_vig=sum(raw_probs),
    )


def confidence_grade(book_estimates: list[BookEstimate]) -> str:
    """
    Grade confidence based on how tightly books agree.

    Uses Team A probability range.
    """
    team_a_probs = [book.team_a_fair for book in book_estimates]

    probability_range = max(team_a_probs) - min(team_a_probs)

    if len(book_estimates) < 3:
        return "LOW - fewer than 3 books"

    if probability_range <= 0.025:
        return "HIGH - books are tightly clustered"

    if probability_range <= 0.05:
        return "MEDIUM - books mostly agree"

    return "LOW - books disagree heavily"


def main() -> None:
    print("\n=== CONSENSUS PROBABILITY ESTIMATOR V0 ===")
    print("Use this for soccer 3-way markets: Team A / Draw / Team B")
    print("Best used with pregame odds from multiple sportsbooks.")
    print("--------------------------------\n")

    kalshi_price = ask_probability(
        "Kalshi price for Team A win, decimal like 0.65: "
    )

    odds_format = ask_odds_format()

    number_of_books = ask_int("Number of sportsbooks to enter: ")

    book_estimates = []

    for index in range(number_of_books):
        print(f"\n--- Sportsbook {index + 1} ---")

        book_name = input("Book name: ").strip()

        if book_name == "":
            book_name = f"Book {index + 1}"

        team_a_odds = ask_float("Team A win odds: ")
        draw_odds = ask_float("Draw odds: ")
        team_b_odds = ask_float("Team B win odds: ")

        estimate = estimate_book(
            book_name=book_name,
            odds_format=odds_format,
            team_a_odds=team_a_odds,
            draw_odds=draw_odds,
            team_b_odds=team_b_odds,
        )

        book_estimates.append(estimate)

    consensus_team_a = average([book.team_a_fair for book in book_estimates])
    consensus_draw = average([book.draw_fair for book in book_estimates])
    consensus_team_b = average([book.team_b_fair for book in book_estimates])

    gap = probability_gap(kalshi_price, consensus_team_a)

    team_a_values = [book.team_a_fair for book in book_estimates]
    low_team_a = min(team_a_values)
    high_team_a = max(team_a_values)
    team_a_range = high_team_a - low_team_a

    grade = confidence_grade(book_estimates)

    print("\n=== BOOK-BY-BOOK NO-VIG PROBABILITIES ===")

    for book in book_estimates:
        print(
            f"{book.book_name}: "
            f"Team A={pct(book.team_a_fair)} | "
            f"Draw={pct(book.draw_fair)} | "
            f"Team B={pct(book.team_b_fair)} | "
            f"Raw total with vig={pct(book.raw_total_with_vig)}"
        )

    print("\n=== CONSENSUS FAIR PROBABILITIES ===")
    print(f"Team A consensus: {pct(consensus_team_a)}")
    print(f"Draw consensus: {pct(consensus_draw)}")
    print(f"Team B consensus: {pct(consensus_team_b)}")
    print(f"Consensus total: {pct(consensus_team_a + consensus_draw + consensus_team_b)}")

    print("\n=== MARKET DISCREPANCY ===")
    print(f"Kalshi Team A price: {pct(kalshi_price)}")
    print(f"Consensus Team A fair probability: {pct(consensus_team_a)}")
    print(f"Discrepancy: {pct(gap)}")
    print(f"Book range for Team A: {pct(low_team_a)} to {pct(high_team_a)}")
    print(f"Book disagreement range: {pct(team_a_range)}")
    print(f"Confidence grade: {grade}")

    print("\n=== SUGGESTED ESTIMATE ===")
    print(f"Use this in main.py: {consensus_team_a:.4f}")

    print("\n=== COACH READ ===")

    if gap >= 0.05 and "HIGH" in grade:
        print("Strong investigate signal: consensus edge clears 5 points and books agree.")
        print("Run this through main.py for EV, Kelly sizing, and verdict.")
    elif gap >= 0.05:
        print("Possible edge, but book disagreement or sample quality needs checking.")
        print("Verify same market, same timing, same settlement rules, and liquidity.")
    elif gap > 0:
        print("Small possible edge, but below 5-point threshold.")
        print("Probably investigate only, not a forced trade.")
    elif abs(gap) < 0.005:
        print("No meaningful discrepancy. Kalshi and consensus agree.")
    else:
        print("Pass signal: Kalshi is pricing Team A above sportsbook consensus.")

    print("\n=== MARKET CHECKLIST ===")
    print("Before trading, confirm:")
    print("- Same exact event")
    print("- Same exact outcome")
    print("- Same timing: pregame vs live")
    print("- Same period: full match vs first half")
    print("- Same settlement rules: regulation only vs extra time")
    print("- Liquidity is acceptable")
    print("- Spread is acceptable")


if __name__ == "__main__":
    main()