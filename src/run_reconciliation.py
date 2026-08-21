from pathlib import Path

from reconciliation import load_transactions
from matcher import reconcile_transactions


BASE_DIR = Path(__file__).resolve().parent.parent

bank_file = BASE_DIR / "data" / "sample_bank.csv"
ledger_file = BASE_DIR / "data" / "sample_ledger.csv"

bank_df = load_transactions(bank_file)
ledger_df = load_transactions(ledger_file)

results = reconcile_transactions(bank_df, ledger_df)

print("\nRecon-AI Reconciliation Results\n")
print(results.to_string(index=False))