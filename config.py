from pathlib import Path

# Paths
DATA_DIR = Path("data")
TRADES_CSV = DATA_DIR / "trades.csv"
BANKROLL_JSON = DATA_DIR / "bankroll.json"

# Risk rules
MAX_REAL_TRADE = 1.00
MAX_BANKROLL_FRACTION = 0.02
DAILY_LOSS_LIMIT = -3.00

# Trading modes
VALID_MODES = {"real", "paper", "test"}