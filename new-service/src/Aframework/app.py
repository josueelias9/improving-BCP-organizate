import requests
import pandas as pd
import streamlit as st

BASE_URL = "http://localhost:8000"


# Fetch all documents
docs_response = requests.get(f"{BASE_URL}/document/", params={"limit": 1000})
docs_response.raise_for_status()
documents = docs_response.json().get("documents", [])



doc_options = {doc["id"]: doc["id"] for doc in documents}
selected_label = st.selectbox("Document", options=list(doc_options.keys()))
selected_document_id = doc_options.get(selected_label)

# Fetch transactions filtered by selected document
params = {"document_id": selected_document_id} if selected_document_id else {}
response = requests.get(f"{BASE_URL}/transactions", params=params)
response.raise_for_status()
transactions = response.json()["transactions"]

# Fetch categories for the edit form
categories_response = requests.get(f"{BASE_URL}/categories/")
categories_response.raise_for_status()
category_names = [c["name"] for c in categories_response.json().get("categories", [])]

df = pd.DataFrame(transactions)
if "order" in df.columns:
    df = df.sort_values("order").reset_index(drop=True)

tab_single, tab_batch = st.tabs(["Edit single", "Batch update categories"])

# --- Single-row edit ---
with tab_single:
    event = st.dataframe(
        df,
        use_container_width=True,
        selection_mode="single-row",
        on_select="rerun",
        key="tx_table_single",
    )

    selected_rows = event.selection.get("rows", [])

    if selected_rows:
        row_idx = selected_rows[0]
        row = df.iloc[row_idx]
        transaction_id = row["id"]

        st.subheader("Edit transaction")
        with st.form("edit_form"):
            new_history = st.text_area("History", value=row.get("history") or "")
            current_category = row.get("category_name") or ""
            default_idx = (
                category_names.index(current_category)
                if current_category in category_names
                else 0
            )
            new_category = st.selectbox(
                "Category", options=category_names, index=default_idx
            )

            if st.form_submit_button("Save"):
                payload = {"history": new_history, "category_name": new_category}
                put_response = requests.put(
                    f"{BASE_URL}/transactions/{transaction_id}", json=payload
                )
                if put_response.ok:
                    st.success("Transaction updated successfully.")
                    st.rerun()
                else:
                    st.error(f"Error: {put_response.text}")

# --- Multi-row batch category update ---
with tab_batch:
    event_batch = st.dataframe(
        df,
        use_container_width=True,
        selection_mode="multi-row",
        on_select="rerun",
        key="tx_table_batch",
    )

    selected_batch_rows = event_batch.selection.get("rows", [])

    if selected_batch_rows:
        st.caption(f"{len(selected_batch_rows)} transaction(s) selected")
        with st.form("batch_category_form"):
            new_category_batch = st.selectbox(
                "Category to assign", options=category_names
            )
            if st.form_submit_button("Apply to selected"):
                updates = [
                    {
                        "transaction_id": df.iloc[i]["id"],
                        "category_name": new_category_batch,
                    }
                    for i in selected_batch_rows
                ]
                batch_response = requests.put(
                    f"{BASE_URL}/transactions/batch", json={"updates": updates}
                )
                if batch_response.ok:
                    result = batch_response.json()
                    st.success(result.get("message", "Batch update completed."))
                    if result.get("errors"):
                        st.warning(f"Errors: {result['errors']}")
                    st.rerun()
                else:
                    st.error(f"Error: {batch_response.text}")
    else:
        st.info("Select one or more rows to batch-update their category.")


st.bar_chart(
    df[df["transaction_type"] == "expense"]
    .groupby("category_name", as_index=False)["amount"]
    .sum(),
    x="category_name",
    y="amount",
    stack=False,
)

st.bar_chart(df, x="transaction_type", y="amount", stack=False)


# One balance-evolution line chart per account
docs_df = pd.DataFrame(documents)
if not docs_df.empty and {"end_date", "balance", "account"}.issubset(docs_df.columns):
    docs_df["end_date"] = pd.to_datetime(docs_df["end_date"])
    st.subheader("Balance evolution by account")
    for account, group in docs_df.groupby("account"):
        st.caption(account)
        st.line_chart(group.sort_values("end_date").set_index("end_date")["balance"])

st.divider()