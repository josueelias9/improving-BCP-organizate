import requests
import pandas as pd
import streamlit as st

response = requests.get("http://localhost:8000/transactions")
response.raise_for_status()

data = response.json()

df = pd.DataFrame(data["transactions"])

st.dataframe(df, use_container_width=True)
