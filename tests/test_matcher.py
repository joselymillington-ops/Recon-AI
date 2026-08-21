import pandas as pd

from src.matcher import reconcile_transactions


def test_reconcile_transactions_flags_match_and_mismatch():
    bank_df = pd.DataFrame(
        [
            {
                "date": "2026-08-01",
                "description": "Office Supplies",
                "amount": -125.49,
                "reference": "TXN1001",
            },
            {
                "date": "2026-08-04",
                "description": "Travel Expense",
                "amount": -420.75,
                "reference": "TXN1004",
            },
        ]
    )

    ledger_df = pd.DataFrame(
        [
            {
                "date": "2026-08-01",
                "description": "Office Supplies",
                "amount": -125.49,
                "reference": "GL1001",
            },
            {
                "date": "2026-08-04",
                "description": "Travel Expense",
                "amount": -400.75,
                "reference": "GL1004",
            },
        ]
    )

    result = reconcile_transactions(bank_df, ledger_df)

    assert result.loc[0, "status"] == "Matched"
    assert result.loc[1, "status"] == "Unmatched"
def test_matches_transactions_within_date_tolerance():
    bank_df = pd.DataFrame(
        {
            "date": ["2026-08-10"],
            "description": ["Client Payment"],
            "amount": [2500.00],
            "reference": ["BANK001"],
        }
    )

    ledger_df = pd.DataFrame(
        {
            "date": ["2026-08-12"],
            "description": ["Client Payment"],
            "amount": [2500.00],
            "reference": ["LEDGER001"],
        }
    )

    results = reconcile_transactions(bank_df, ledger_df)

    assert results.iloc[0]["status"] == "Matched"
    assert results.iloc[0]["date_difference_days"] == 2