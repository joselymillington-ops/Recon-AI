import pandas as pd


def reconcile_transactions(
    bank_df,
    ledger_df,
    amount_tolerance=0.01,
    date_tolerance_days=2,
):
    """
    Reconcile bank transactions against ledger transactions.

    Matching rules:
    1. Amounts must be within the allowed tolerance.
    2. Dates may differ by up to the allowed number of days.
    3. Each ledger transaction can only be matched once.
    """

    bank_df = bank_df.copy()
    ledger_df = ledger_df.copy()

    bank_df["date"] = pd.to_datetime(bank_df["date"])
    ledger_df["date"] = pd.to_datetime(ledger_df["date"])

    matched_ledger_indices = set()
    results = []

    for _, bank_row in bank_df.iterrows():
        best_match_index = None
        best_date_difference = None

        for ledger_index, ledger_row in ledger_df.iterrows():
            if ledger_index in matched_ledger_indices:
                continue

            amount_difference = abs(
                bank_row["amount"] - ledger_row["amount"]
            )

            date_difference = abs(
                (bank_row["date"] - ledger_row["date"]).days
            )

            if (
                amount_difference <= amount_tolerance
                and date_difference <= date_tolerance_days
            ):
                if (
                    best_date_difference is None
                    or date_difference < best_date_difference
                ):
                    best_match_index = ledger_index
                    best_date_difference = date_difference

        if best_match_index is not None:
            ledger_match = ledger_df.loc[best_match_index]
            matched_ledger_indices.add(best_match_index)

            results.append(
                {
                    "date": bank_row["date"].date(),
                    "description": bank_row["description"],
                    "amount": bank_row["amount"],
                    "bank_reference": bank_row["reference"],
                    "ledger_reference": ledger_match["reference"],
                    "status": "Matched",
                    "date_difference_days": best_date_difference,
                    "amount_difference": abs(
                        bank_row["amount"] - ledger_match["amount"]
                    ),
                }
            )

        else:
            results.append(
                {
                    "date": bank_row["date"].date(),
                    "description": bank_row["description"],
                    "amount": bank_row["amount"],
                    "bank_reference": bank_row["reference"],
                    "ledger_reference": None,
                    "status": "Unmatched",
                    "date_difference_days": None,
                    "amount_difference": None,
                }
            )

    return pd.DataFrame(results)