"""
Validate data/trades.csv for schema and data quality issues.

This protects the engine from bad rows, missing columns, invalid prices,
bad probabilities, invalid modes, and settlement inconsistencies.
"""

import csv
from pathlib import Path


TRADE_LOG_PATH = Path("data/trades.csv")

REQUIRED_COLUMNS = {
    "date",
    "mode",
    "sport",
    "event",
    "market",
    "price",
    "estimated_probability",
    "stake",
    "fee_rate",
    "confidence",
    "verdict",
    "result",
    "closing_price",
    "clv",
    "profit_loss",
    "notes",
    "review_market_valid",
    "review_estimate_sourced",
    "review_followed_stake_rules",
    "review_beat_closing_line",
    "review_emotional",
    "review_lesson",
}

VALID_MODES = {"test", "paper", "real", "manual", "legacy"}
VALID_RESULTS = {"", "open", "win", "loss", "push"}
VALID_CONFIDENCE = {"low", "medium", "high", ""}


def safe_float(value):
    if value is None:
        return None

    value = str(value).strip()

    if value == "":
        return None

    try:
        return float(value)
    except ValueError:
        return None


def read_trades(path=TRADE_LOG_PATH):
    if not path.exists():
        raise FileNotFoundError(f"No trade log found at {path}")

    with path.open("r", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader), reader.fieldnames or []


def validate_range(row_number, row, column, min_value=None, max_value=None):
    errors = []

    value = safe_float(row.get(column))

    if value is None:
        return errors

    if min_value is not None and value < min_value:
        errors.append(
            f"Row {row_number}: {column}={value} is below minimum {min_value}"
        )

    if max_value is not None and value > max_value:
        errors.append(
            f"Row {row_number}: {column}={value} is above maximum {max_value}"
        )

    return errors


def validate_required_numeric(row_number, row, column):
    value = safe_float(row.get(column))

    if value is None:
        return [f"Row {row_number}: missing or invalid required numeric field '{column}'"]

    return []


def validate_row(row_number, row):
    errors = []
    warnings = []

    mode = row.get("mode", "").strip().lower()
    result = row.get("result", "").strip().lower()
    confidence = row.get("confidence", "").strip().lower()

    if mode not in VALID_MODES:
        errors.append(f"Row {row_number}: invalid mode '{mode}'")

    if result not in VALID_RESULTS:
        errors.append(f"Row {row_number}: invalid result '{result}'")

    if confidence not in VALID_CONFIDENCE:
        errors.append(f"Row {row_number}: invalid confidence '{confidence}'")

    is_manual_or_legacy = (
    row.get("mode", "").strip().lower() in {"manual", "legacy"}
    or "manual" in row.get("notes", "").strip().lower()
    or "legacy" in row.get("notes", "").strip().lower()
)

    if not is_manual_or_legacy:
        errors += validate_required_numeric(row_number, row, "price")
        errors += validate_required_numeric(row_number, row, "stake")
    else:
        # Manual/legacy trades may only have final P/L.
        if safe_float(row.get("profit_loss")) is None:
            warnings.append(
                f"Row {row_number}: manual/legacy trade has no profit_loss"
        )

    errors += validate_range(row_number, row, "price", 0.0, 1.0)
    errors += validate_range(row_number, row, "estimated_probability", 0.0, 1.0)
    errors += validate_range(row_number, row, "calibrated_probability", 0.0, 1.0)
    errors += validate_range(row_number, row, "fee_rate", 0.0, 1.0)
    errors += validate_range(row_number, row, "stake", 0.0, None)
    errors += validate_range(row_number, row, "closing_price", 0.0, 1.0)

    profit_loss = safe_float(row.get("profit_loss"))
    closing_price = safe_float(row.get("closing_price"))
    clv = safe_float(row.get("clv"))

    is_open = result in {"", "open"}
    is_settled = result in {"win", "loss", "push"}

    if is_open:
        if profit_loss is not None:
            warnings.append(
                f"Row {row_number}: open trade has profit_loss filled"
            )
        if closing_price is not None:
            warnings.append(
                f"Row {row_number}: open trade has closing_price filled"
            )
        if clv is not None:
            warnings.append(
                f"Row {row_number}: open trade has clv filled"
            )

    if is_settled:
        if profit_loss is None:
            errors.append(
                f"Row {row_number}: settled trade is missing profit_loss"
            )
        if closing_price is None:
            warnings.append(
                f"Row {row_number}: settled trade is missing closing_price"
            )
        if clv is None and not is_manual_or_legacy:
            warnings.append(
                f"Row {row_number}: settled trade is missing clv"
            )

    return errors, warnings


def main():
    trades, fieldnames = read_trades()

    missing_columns = sorted(REQUIRED_COLUMNS - set(fieldnames))

    all_errors = []
    all_warnings = []

    if missing_columns:
        all_errors.append(
            "Missing required columns: " + ", ".join(missing_columns)
        )

    for row_index, row in enumerate(trades, start=2):
        errors, warnings = validate_row(row_index, row)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    print("\n=== TRADE CSV VALIDATION ===")
    print(f"File: {TRADE_LOG_PATH}")
    print(f"Rows checked: {len(trades)}")

    if all_warnings:
        print("\nWarnings:")
        for warning in all_warnings:
            print(f"- {warning}")

    if all_errors:
        print("\nErrors:")
        for error in all_errors:
            print(f"- {error}")

        print("\nStatus: FAILED")
        raise SystemExit(1)

    print("\nStatus: PASSED")


if __name__ == "__main__":
    main()