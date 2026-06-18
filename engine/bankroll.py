import json
from pathlib import Path

from config import BANKROLL_JSON


def load_bankroll():
    if not BANKROLL_JSON.exists():
        raise FileNotFoundError(
            f"Missing {BANKROLL_JSON}. Create data/bankroll.json first."
        )

    with open(BANKROLL_JSON, "r") as f:
        return json.load(f)


def save_bankroll(bankroll_data):
    BANKROLL_JSON.parent.mkdir(parents=True, exist_ok=True)

    with open(BANKROLL_JSON, "w") as f:
        json.dump(bankroll_data, f, indent=2)


def get_current_bankroll():
    bankroll_data = load_bankroll()
    return float(bankroll_data.get("current_bankroll", 0.0))


def update_current_bankroll(new_amount):
    bankroll_data = load_bankroll()
    bankroll_data["current_bankroll"] = float(new_amount)
    save_bankroll(bankroll_data)