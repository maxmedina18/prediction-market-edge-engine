# Kalshi Edge Engine

A Python-based decision-support engine for binary prediction-market trades.

The goal is not to generate random picks. The goal is to evaluate trades using:

- Implied probability
- Expected value
- Fees
- Kelly Criterion
- Bankroll limits
- Closing line value
- Profit/loss tracking
- Long-term calibration

## Current Features

- Analyze a binary contract trade from the command line
- Calculate post-fee expected value
- Calculate full Kelly and fractional Kelly sizing
- Apply beginner bankroll caps
- Log trades to CSV
- Settle trades after result
- Track closing line value and profit/loss
- Print summary dashboard

## Project Structure

```text
kalshi-edge-engine/
├── main.py
├── settle_trade.py
├── summary.py
├── engine/
│   ├── ev.py
│   ├── kelly.py
│   ├── verdict.py
│   ├── logger.py
│   └── settlement.py
├── data/
│   └── trades.csv
└── README.md