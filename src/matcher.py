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
    4. Unmatched items receive a discrepancy reason.
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

        closest_amount_difference = None
        closest_date_difference = None

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
                closest_amount_difference is None
                or amount_difference < closest_amount_difference
            ):
                closest_amount_difference = amount_difference

            if (
                closest_date_difference is None
                or date_difference < closest_date_difference
            ):
                closest_date_difference = date_difference

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
                    "discrepancy_reason": None,
                    "date_difference_days": best_date_difference,
                    "amount_difference": abs(
                        bank_row["amount"] - ledger_match["amount"]
                    ),
                }
            )

        else:
            same_date_candidates = ledger_df[
                ledger_df["date"] == bank_row["date"]
            ]

            same_amount_candidates = ledger_df[
                (
                    ledger_df["amount"] - bank_row["amount"]
                ).abs() <= amount_tolerance
            ]

            if not same_date_candidates.empty:
                closest_same_date_amount_difference = (
                    same_date_candidates["amount"] - bank_row["amount"]
                ).abs().min()

                discrepancy_reason = "Amount mismatch"

                closest_amount_difference = (
                    closest_same_date_amount_difference
                )

                closest_date_difference = 0

            elif not same_amount_candidates.empty:
                closest_same_amount_date_difference = (
                    same_amount_candidates["date"] - bank_row["date"]
                ).abs().dt.days.min()

                discrepancy_reason = "Date outside tolerance"

                closest_date_difference = (
                    closest_same_amount_date_difference
                )

                closest_amount_difference = 0.0

            else:
                discrepancy_reason = "Possible missing ledger entry"

                closest_date_difference = None
                closest_amount_difference = None

            results.append(
                {
                    "date": bank_row["date"].date(),
                    "description": bank_row["description"],
                    "amount": bank_row["amount"],
                    "bank_reference": bank_row["reference"],
                    "ledger_reference": None,
                    "status": "Unmatched",
                    "discrepancy_reason": discrepancy_reason,
                    "date_difference_days": closest_date_difference,
                    "amount_difference": closest_amount_difference,
                }
            )
    return pd.DataFrame(results)