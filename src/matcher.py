import pandas as pd


def reconcile_transactions(bank_df, ledger_df):
    """
    Match bank transactions to ledger transactions using date and amount.

    Returns a DataFrame showing whether each bank transaction
    has a matching ledger transaction.
    """

    results = []

    for _, bank_row in bank_df.iterrows():
        matches = ledger_df[
            (ledger_df["date"] == bank_row["date"])
            & (ledger_df["amount"] == bank_row["amount"])
        ]

        if not matches.empty:
            status = "Matched"
        else:
            status = "Unmatched"

        results.append(
            {
                "date": bank_row["date"],
                "description": bank_row["description"],
                "amount": bank_row["amount"],
                "bank_reference": bank_row["reference"],
                "status": status,
            }
        )

    return pd.DataFrame(results)
