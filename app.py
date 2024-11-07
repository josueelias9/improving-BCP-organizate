import streamlit as st
import pandas as pd
from pathlib import Path
from io import StringIO


st.title('Improving "BCP organizate"')
import streamlit as st

st.image("image.png", caption="Sunrise by the mountains")

uploaded_file = st.file_uploader("Load the html from BCP")


option = st.selectbox(
    "How would you like to be contacted?",
    ("septiembre", "octubre", "noviembre"),
    index=None,
    placeholder="Select contact method...",
)

if option:
    st.write("Month to be analized:", option)

    # route of tables
    table_BCP = f"./db/gastos_{option}.csv"
    table_historia = f"./db/historia_{option}.csv"

    # if doesnt exist, create empty csv file
    ruta_actual = Path.cwd()
    ruta_sub_carpeta = ruta_actual / "db"
    ruta_del_mes = [archivo for archivo in ruta_sub_carpeta.rglob("*") if option == archivo.name]

    if not ruta_del_mes:
        pd.DataFrame(data={"historia": [], "modify_category": []}).to_csv(table_historia, index=False)

    # create dataframe
    df_table_BCP = pd.read_csv(table_BCP, dtype=str)
    df_table_historia = pd.read_csv(table_historia, dtype={"modify_category": "bool"})

    df_table_BCP["historia"] = ["" for i in range(len(df_table_BCP) - len(df_table_historia))] + df_table_historia["historia"].to_list()

    df_table_BCP["modify_category"] = [False for i in range(len(df_table_BCP) - len(df_table_historia))] + df_table_historia[
        "modify_category"
    ].to_list()

    st.title("Editor de CSV")

    edited_data = st.data_editor(
        df_table_BCP,
        column_config={"historia": {"editable": True}},  # Solo se permite editar "historia"
        use_container_width=True,
    )

    if st.button("Save data"):
        edited_data[["historia", "modify_category"]].to_csv(table_historia, index=False)
        st.write("Saved data")
