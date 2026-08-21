import streamlit as st

from src.matcher import reconcile_transactions
from src.reconciliation import load_transactions

st.markdown(
    """
    <style>
        .stApp {
            background-color: #0b1220;
            color: #f3f6fb;
        }

        h1, h2, h3 {
            color: #f8fbff;
        }

        [data-testid="stMetric"] {
            background: #111c2e;
            border: 1px solid #22324a;
            padding: 16px;
            border-radius: 14px;
        }

        [data-testid="stFileUploader"] {
            background: #111c2e;
            border: 1px solid #22324a;
            padding: 12px;
            border-radius: 14px;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.set_page_config(
    page_title="Recon-AI",
    page_icon="📊",
    layout="wide",
)
st.markdown(
    """
    <div style="margin-bottom: 8px;">
        <span style="
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 2px;
            color: #5eead4;
        ">
            RECONCILIATION INTELLIGENCE
        </span>
    </div>

    <h1 style="
        font-size: 48px;
        margin: 0;
        padding: 0;
        line-height: 1.1;
    ">
        Recon-AI
    </h1>

    <p style="
        font-size: 20px;
        color: #a9b7ca;
        margin-top: 10px;
        margin-bottom: 4px;
    ">
        Intelligent account reconciliation, without the spreadsheet archaeology.
    </p>
    """,
    unsafe_allow_html=True,
)

st.write(
    "Upload a bank transaction CSV and a general ledger CSV to identify "
    "matched and unmatched transactions."
)
with st.sidebar:
    st.header("Matching Settings")

    amount_tolerance = st.number_input(
        "Amount tolerance",
        min_value=0.00,
        value=0.01,
        step=0.01,
        format="%.2f",
    )

    date_tolerance_days = st.slider(
        "Date tolerance (days)",
        min_value=0,
        max_value=7,
        value=2,
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

    results = reconcile_transactions(
    bank_df,
    ledger_df,
    amount_tolerance=amount_tolerance,
    date_tolerance_days=date_tolerance_days,
)

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
    csv_report = results.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Reconciliation Report",
        data=csv_report,
        file_name="recon_ai_reconciliation_report.csv",
        mime="text/csv",
    )