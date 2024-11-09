import pandas as pd
from pathlib import Path
import extract_information
from datetime import datetime

history_table_str = "./db/history.csv"
transaction_table_str = "./db/transaction.csv"
history_columns = ["history", "new_category", "requires_update", "date_id"]


def create_merged_df():

    # create dataframe
    transaction_table_df = pd.read_csv(transaction_table_str, dtype=str)
    history_table_df = pd.read_csv(history_table_str, dtype={"requires_update": "bool"})

    # left join
    merged_df = transaction_table_df.merge(history_table_df, how="left", left_on="date_id", right_on="date_id")

    # fill "history" and "requires_update" columns / why? / this should be made by the ETL????
    merged_df = merged_df.fillna(
        {i: (False if i == "requires_update" else (merged_df["category"] if i == "new_category" else "")) for i in history_columns}
    )

    # convert to datetime type / think this should be deleted
    merged_df["date_id"] = pd.to_datetime(merged_df["date_id"])

    return merged_df


def create_if_doesnt_exist():

    # check db directory
    empty_data = {i: [] for i in history_columns}

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


def get_count(edited_data):
    return (edited_data == "").sum()


def save_df(df):

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    df[history_columns].to_csv(history_table_str, index=False)
    df[history_columns].to_csv(f"/mnt/c/Users/josue/Desktop/reports/personal information {now}.csv", index=False)


def get_categories():
    return pd.read_csv("./db/category.csv")["category"].to_list()


def call_ETL(string_data):
    extract_information.ETL_transaction_table(string_data)
