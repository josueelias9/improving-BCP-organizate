import requests
import pandas as pd
import streamlit as st

BASE_URL = "http://localhost:8000"

# Fetch documents for the combobox
docs_response = requests.get(f"{BASE_URL}/document/")
docs_response.raise_for_status()
documents = docs_response.json().get("documents", [])

doc_options = {doc["unique_identifier"]: doc["id"] for doc in documents}
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

# Export CSV button
if selected_document_id:
    if st.button("Export CSV"):
        export_resp = requests.get(
            f"{BASE_URL}/transactions/export/csv",
            params={"document_id": selected_document_id},
        )


# Row selection
event = st.dataframe(
    df,
    use_container_width=True,
    selection_mode="single-row",
    on_select="rerun",
    key="tx_table",
)

selected_rows = event.selection.get("rows", [])

# Edit form appears when a row is selected
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

st.bar_chart(df, x="category_name", y="amount", stack=False)
