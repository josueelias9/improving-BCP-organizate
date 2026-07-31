import requests
import pandas as pd
import streamlit as st

# Fetch documents for the combobox
docs_response = requests.get("http://localhost:8000/document/")
docs_response.raise_for_status()
documents = docs_response.json().get("documents", [])

doc_options = {doc["unique_identifier"]: doc["id"] for doc in documents}
selected_label = st.selectbox("Document", options=list(doc_options.keys()))
selected_document_id = doc_options.get(selected_label)

# Fetch transactions filtered by selected document
params = {"document_id": selected_document_id} if selected_document_id else {}
response = requests.get("http://localhost:8000/transactions", params=params)
response.raise_for_status()

data = response.json()

df = pd.DataFrame(data["transactions"])

st.dataframe(df, use_container_width=True)

st.bar_chart(df, x="category_name", y="amount", stack=False)
