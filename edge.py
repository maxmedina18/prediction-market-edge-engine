"""
Edge Engine launcher.

Simple menu for running the main tools from one place.
"""

import subprocess
import sys


MENU_OPTIONS = {
    "1": ("Analyze trade", "main.py"),
    "2": ("Estimate probability from one sportsbook", "estimate_probability.py"),
    "3": ("Estimate probability from multi-book consensus", "estimate_consensus.py"),
    "4": ("Run market check", "market_check.py"),
    "5": ("Settle trade", "settle_trade.py"),
    "6": ("View summary", "summary.py"),
    "7": ("View calibration", "calibration.py"),
    "8": ("View risk dashboard", "risk_dashboard.py"),
    "9": ("Validate trade log", "validate_trades.py"),
    "10": ("Exit", None),
}


def run_script(script_name: str) -> None:
    subprocess.run([sys.executable, script_name], check=False)


def print_menu() -> None:
    print("\n=== EDGE ENGINE ===")
    for key, (label, _) in MENU_OPTIONS.items():
        print(f"{key}. {label}")


def run_validate_trades() -> None:
    import validate_trades
    validate_trades.main()


def main() -> None:
    while True:
        print_menu()
        choice = input("\nChoose an option: ").strip()

        option = MENU_OPTIONS.get(choice)

        if option is None:
            print("Invalid choice. Try again.")
            continue

        label, script_name = option

        if script_name is None:
            print("Exiting Edge Engine.")
            break

        print(f"\n--- Running: {label} ---\n")

        if script_name == "validate_trades.py":
            run_validate_trades()
        else:
            run_script(script_name)


if __name__ == "__main__":
    main()