Prediction Market Edge Engine

A Python-based decision-support engine for analyzing binary prediction-market trades.

This project is designed for educational and research purposes. It helps evaluate event contracts using expected value, implied probability, Kelly-style sizing, market validation, calibration tracking, and strict bankroll risk controls.

It does not place trades automatically.

⸻

Purpose

The goal of this project is to move from impulsive betting decisions toward a structured trading process.

Instead of asking:

“Do I think this team wins?”

The engine forces better questions:

* What probability is the market implying?
* What is my estimated probability?
* Is the edge large enough after fees?
* Is the position size controlled?
* Is this the same exact market I am comparing against?
* Am I risking too much of the bankroll?
* Did the trade beat the closing line?
* Was this a good process even if it lost?

⸻

Core Features

Expected Value Analysis

Calculates:

* Market implied probability
* Estimated edge
* EV per contract
* Expected profit on stake
* Expected ROI

Kelly and Sizing Tools

Includes:

* Full Kelly fraction
* Fractional Kelly
* Beginner capped stake
* Hard learning-mode stake limits

Risk Guard Firewall

Blocks or flags trades that violate bankroll rules, including:

* Stake above learning-mode max
* Stake above bankroll percentage cap
* Daily realized loss limit
* Low-confidence trades
* Engine verdicts that say PASS or REDUCE SIZE

Market Validation

Checks whether a Kalshi/event-contract market is comparable to sportsbook odds:

* Same event
* Same outcome
* Same timing
* Same period
* Same settlement rules
* Liquidity acceptable
* Spread acceptable

This helps avoid fake edges caused by comparing mismatched markets.

Probability Estimation

Includes tools for:

* Single sportsbook no-vig probability estimation
* Multi-book consensus probability estimation
* Fair probability comparison against Kalshi prices

Trade Logging

Logs trades to CSV with:

* Date
* Mode: real, paper, or test
* Sport
* Event
* Market
* Price
* Estimated probability
* Stake
* EV
* ROI
* Kelly sizing
* Verdict
* Result
* Closing price
* CLV
* Profit/loss
* Notes

Settlement and CLV Tracking

After a market resolves, trades can be settled with:

* Win/loss/push
* Closing price
* Closing line value
* Profit/loss

Summary Dashboard

Reports:

* Total trades
* Settled trades
* Open trades
* Wins/losses/pushes
* Win rate
* Total P/L
* Average CLV
* Average EV
* Average ROI
* Best trade
* Worst trade

Supports filtering by:

* real
* paper
* test
* all

Calibration Dashboard

Tracks whether estimated probabilities match real outcomes over time.

Manual legacy trades with blank probabilities are skipped so they do not pollute calibration.

Manual Legacy Trade Importer

Allows safe import of historical trades, combos, or parlays without manually editing the CSV.

This prevents column-shift errors and keeps calibration clean.

⸻

Project Structure

prediction-market-edge-engine/
├── edge.py
├── main.py
├── estimate_probability.py
├── estimate_consensus.py
├── market_check.py
├── settle_trade.py
├── summary.py
├── calibration.py
├── manual_trade.py
├── backtest.py
├── data/
│   └── sample_trades.csv
├── engine/
│   ├── ev.py
│   ├── kelly.py
│   ├── verdict.py
│   ├── logger.py
│   ├── settlement.py
│   ├── calibration.py
│   ├── odds.py
│   ├── market_check.py
│   └── risk_guard.py
└── README.md

⸻

How to Run

Clone the repo:

git clone https://github.com/maxmedina18/prediction-market-edge-engine.git
cd prediction-market-edge-engine

Create a virtual environment:

python -m venv .venv
source .venv/bin/activate

Run the launcher:

python edge.py

⸻

Launcher Menu

=== EDGE ENGINE ===
1. Analyze trade
2. Estimate probability from one sportsbook
3. Estimate probability from multi-book consensus
4. Run market check
5. Settle trade
6. View summary
7. View calibration
8. Add manual legacy trade
9. Exit

⸻

Example Trade Pipeline

A disciplined trade should follow this process:

python summary.py
python calibration.py
python market_check.py
python estimate_consensus.py
python main.py

After the event resolves:

python settle_trade.py
python summary.py
python calibration.py

For historical/manual trades:

python manual_trade.py

⸻

Trading Rules

Current learning-mode rules:

* Maximum real trade size: 2% of bankroll
* Maximum stake: 2% of bankroll
* Daily realized loss limit: -$3
* No parlays
* No revenge trading
* No live chasing
* No low-confidence real trades
* No real trade unless the risk guard allows it
* Every real trade must be logged

A real trade is only allowed when:

Verdict: SMALL TRADE OK
Risk guard: TRADE ALLOWED

⸻

Sample Data

The repo includes:

data/sample_trades.csv

This is a sanitized example dataset.

Private real trade logs should be stored locally as:

data/trades.csv

That file is ignored by Git and should not be committed.

⸻

Current Limitations

This project is still in early development.

Known limitations:

* Odds are entered manually.
* No live API integration yet.
* No automatic Kalshi API ingestion yet.
* Calibration needs a larger sample size to become statistically useful.
* No web dashboard yet.
* No automated alerting yet.
* No automatic trading.

⸻

Roadmap

Planned upgrades:

* Streamlit dashboard
* Daily risk dashboard
* Bankroll recovery tracker
* Open exposure tracker
* Better backtesting tools
* Multi-sportsbook data ingestion
* Kalshi API integration
* Positive-EV opportunity scanner
* Closing line value trend charts
* Model calibration charts
* Trade review journal

Long-term goal:

An OddsJam-inspired decision-support dashboard for event contracts and prediction markets.

The focus is on research, risk management, and disciplined execution — not automated gambling.

⸻

Disclaimer

This project is for educational and research purposes only.

Prediction markets and sports-related event contracts involve risk, variance, and possible total loss of capital. This software does not guarantee profit and should not be used as financial advice.

The engine is designed to encourage disciplined decision-making, bankroll protection, and post-trade analysis.
