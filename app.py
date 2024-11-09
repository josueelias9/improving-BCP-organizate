import streamlit as st
import pandas as pd
from pathlib import Path
from io import StringIO
import extract_information

history_table_str = "./db/history.csv"
transaction_table_str = "./db/transaction.csv"


def create_merged_df():

    # create dataframe
    transaction_table_df = pd.read_csv(transaction_table_str, dtype=str)
    history_table_df = pd.read_csv(history_table_str, dtype={"modify_category": "bool"})

    # left join
    merged_df = transaction_table_df.merge(history_table_df, how="left", left_on="date_id", right_on="date_id")

    # fill "history" and "modify_category" columns
    merged_df = merged_df.fillna({"history": "", "modify_category": False})

    # convert to datetime type
    merged_df["date_id"] = pd.to_datetime(merged_df["date_id"])

    return merged_df


def create_if_doesnt_exist():

    # check db directory
    empty_data = {"history": [], "modify_category": [], "date_id": []}

    # if directory doesnt exist, create the directory and file
    if not (Path.cwd() / "db").exists():
        (Path.cwd() / "db").mkdir()

    # check history table
    if not (Path.cwd() / "db" / "history.csv").exists():
        pd.DataFrame(data=empty_data).to_csv(history_table_str, index=False)

    # check transaction table
    if not (Path.cwd() / "db" / "transaction.csv").exists():
        return {
            "log": f"""
directory/db        EXISTS
transaction.csv     NOT EXISTS
history.csv         EXISTS """,
            "type": "error",
        }

    return {
        "log": f"""
directory/db        EXISTS
transaction.csv     EXISTS
history.csv         EXISTS """,
        "type": "success",
    }


def save_df(df):
    df.to_csv(history_table_str, index=False)
    df.to_csv("/mnt/c/Users/josue/Desktop/personal_information.csv", index=False)


# ============== STREAMLIT ==============
st.set_page_config(layout="wide")


st.title('Improving "BCP organizate"')

st.image("BCP.png", caption="BCP")

uploaded_file = st.file_uploader("Load the html from BCP")
if uploaded_file is not None:
    # To read file as string:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    string_data = stringio.read()
    extract_information.ETL_transaction_table(string_data)


if create_if_doesnt_exist()["type"] == "success":

    merged_df = create_merged_df()

    st.title("Edit you story")
    st.write("Edit the story of each transaction. Order by `date_id`.")

    edited_data = st.data_editor(
        merged_df,
        column_config={"history": {"editable": True}},  # Solo se permite editar "history"
        use_container_width=True,
    )
    # count how many empty strings are ing the "history" column
    st.write(f'missing stories: {(edited_data["history"] == "").sum()}')

    if st.button("Save data"):
        save_df(edited_data[["history", "modify_category", "date_id"]])
        st.write("data to database")

else:
    st.header("Upload the html from BCP")
