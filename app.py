import streamlit as st

from src.matcher import reconcile_transactions
from src.reconciliation import load_transactions


st.set_page_config(
    page_title="Recon-AI",
    page_icon="📊",
    layout="wide",
)

st.title("Recon-AI")
st.subheader("AI-Powered Account Reconciliation Assistant")

st.write(
    "Upload a bank transaction CSV and a general ledger CSV to identify "
    "matched and unmatched transactions."
)

st.divider()

col1, col2 = st.columns(2)

with col1:
    bank_file = st.file_uploader(
        "Upload Bank Transactions",
        type=["csv"],
        key="bank_file",
    )

with col2:
    ledger_file = st.file_uploader(
        "Upload General Ledger",
        type=["csv"],
        key="ledger_file",
    )
if bank_file is not None and ledger_file is not None:
    bank_df = load_transactions(bank_file)
    ledger_df = load_transactions(ledger_file)

    results = reconcile_transactions(bank_df, ledger_df)

    st.success("Reconciliation complete.")
    st.dataframe(results, use_container_width=True)

    matched_count = (results["status"] == "Matched").sum()
    unmatched_count = (results["status"] == "Unmatched").sum()

    metric1, metric2 = st.columns(2)

    with metric1:
        st.metric("Matched Transactions", matched_count)

    with metric2:
        st.metric("Unmatched Transactions", unmatched_count)

    st.subheader("Discrepancy Analysis")

    unmatched_results = results[results["status"] == "Unmatched"]

    if unmatched_results.empty:
        st.success("No discrepancies found.")
    else:
        st.dataframe(
            unmatched_results[
                [
                    "date",
                    "description",
                    "amount",
                    "bank_reference",
                    "discrepancy_reason",
                    "date_difference_days",
                    "amount_difference",
                ]
            ],
            use_container_width=True,
        )