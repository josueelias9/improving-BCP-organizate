import os
import requests
import pandas as pd
import streamlit as st

BASE_URL = "http://localhost:8000"
DOWNLOADS_DIR = "/downloads"

# --- Sidebar: Add Document and Transactions ---
with st.sidebar:
    st.header("Add Document and Transactions")

    pdf_files = sorted(
        f for f in os.listdir(DOWNLOADS_DIR) if f.lower().endswith(".pdf")
    ) if os.path.isdir(DOWNLOADS_DIR) else []

    selected_file = st.selectbox("PDF File", options=pdf_files, index=0 if pdf_files else None)
    pdf_filepath = f"{DOWNLOADS_DIR}/{selected_file}" if selected_file else ""

    document_type = st.selectbox("Document Type", ["bcp_debit", "bcp_credit"])
    user_email = st.text_input("User Email", value="admin@bcpextractor.com")

    if st.button("Add Document and Transactions", type="primary"):
        if not pdf_filepath or not user_email:
            st.error("PDF file path and user email are required.")
        else:
            with st.spinner("Creating document..."):
                doc_res = requests.post(
                    f"{BASE_URL}/document/",
                    json={"pdf_filepath": pdf_filepath, "document_type": document_type, "user_email": user_email},
                )
            if not doc_res.ok:
                st.error(f"Create document failed: {doc_res.text}")
            else:
                doc_data = doc_res.json()
                document_id = doc_data["document_id"]
                with st.spinner("Loading transactions..."):
                    tx_res = requests.post(f"{BASE_URL}/transactions/{document_id}")
                if not tx_res.ok:
                    st.warning("Document created but transactions failed.")
                    st.json(doc_data)
                    st.error(tx_res.text)
                else:
                    st.success("Done!")
                    st.json(doc_data)
                    st.json(tx_res.json())
                    st.rerun()

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
