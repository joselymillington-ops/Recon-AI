import pandas as pd


def load_transactions(file):
    """Load transaction data from a CSV file."""
    return pd.read_csv(file)
