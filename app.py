import streamlit as st
import pandas as pd
from pathlib import Path
import my_data


st.title('Improving "BCP organizate"')
import streamlit as st

st.image("image.png", caption="Sunrise by the mountains")

uploaded_file = st.file_uploader("Load the html from BCP")


option = st.selectbox(
    "Select the month to analyze:",
    tuple(my_data.translate.keys()),
    index=None,
    placeholder="Select month...",
)

if option:
    st.write("Month to be analized:", option)

    # route of tables
    history_table_str = "./db/history.csv"
    transaction_table_str = "./db/transaction.csv"

    # if doesnt exist, create empty csv file
    ruta_sub_carpeta = Path.cwd() / "db"
    ruta_del_mes = [archivo for archivo in ruta_sub_carpeta.rglob("*") if archivo == ruta_sub_carpeta / "history.csv"]

    if not ruta_del_mes:
        pd.DataFrame(data={"history": [], "modify_category": [], "date_id": []}).to_csv(history_table_str, index=False)

    # create dataframe
    transaction_table_df = pd.read_csv(transaction_table_str, dtype=str)
    history_table_df = pd.read_csv(history_table_str, dtype={"modify_category": "bool"})

    # left join
    merged_df = transaction_table_df.merge(history_table_df, how="left", left_on="date_id", right_on="date_id")

    st.title("Table Editor")

    edited_data = st.data_editor(
        merged_df,
        column_config={"history": {"editable": True}},  # Solo se permite editar "history"
        use_container_width=True,
    )

    if st.button("Save data"):
        edited_data[["history", "modify_category", "date_id"]].to_csv(history_table_str, index=False)
        st.write("Saved data")
